"""Controles de dominio auditables; son heurísticas, no un juez semántico universal."""
import re
import unicodedata


def normalize(text):
    """Unifica acentos y mayúsculas para reglas explícitas de soporte en español."""
    return ''.join(c for c in unicodedata.normalize('NFD', text.lower()) if unicodedata.category(c) != 'Mn')


# Vocabulario explícito del dominio: \b limita palabras y \w* admite terminaciones.
# Ejemplo: factur\w* reconoce factura/facturación. Estas reglas no aprenden solas.
PATTERNS = {
    'billing': r'\b(factur\w*|cobr\w*|cargo\w*|pago\w*)\b',
    'vpn': r'\bvpn\b',
    'browser': r'\b(firefox|cookies?|navegador\w*)\b',
    'access': r'\b(contrasena|cuenta|bloquead\w*)\b',
    'security': r'\b(phishing|sospechos\w*|malware)\b',
    'commercial': r'\b(precio\w*|cotiz\w*|contratar|planes)\b',
}


def topics(text):
    """Detecta señales conocidas; una consulta sin señal conserva incertidumbre."""
    return {name for name, pattern in PATTERNS.items() if re.search(pattern, normalize(text))}


def expand_query(text):
    """Expansión léxica acotada: no se presenta como embeddings ni comprensión general."""
    normalized = normalize(text)
    # Se mantiene la consulta original y se añaden términos presentes en INT-FAC.
    # No se altera el documento ni su hash y no se expande cualquier uso de «doble».
    if re.search(r'\b(cobraron|cobrado|cobran|debitaron|descontaron)\b.*\b(dos veces|doble)\b', normalized):
        return text + ' factura cobro duplicado'
    return text


def select_context(clean, previous, memory, enabled):
    """Recorta al segmento temático reciente; no borra el historial del operador."""
    current = topics(clean)
    if not enabled:
        return {}, {'action': 'disabled', 'topic_change': False, 'topics': sorted(current)}
    recent = previous['turns']
    # Buscar desde el final evita usar como tema activo la primera consulta del hilo.
    # Una frase genérica como «¿qué hago?» puede continuar el último tema reconocido.
    last = next((topics(t['user']) for t in reversed(recent) if topics(t['user'])), set())
    changed = bool(current and last and current.isdisjoint(last))
    # isdisjoint significa que no hay señales temáticas compartidas. Es una regla
    # conservadora: temas mixtos o desconocidos no garantizan detección del cambio.
    if changed:
        return {}, {'action': 'ignore_previous_topic', 'topic_change': True, 'topics': sorted(current)}
    target = current or last
    retained = []
    for turn in reversed(recent):
        # Recorremos hacia atrás hasta encontrar otro tema; no borramos SQLite.
        signal = topics(turn['user'])
        if target and signal and target.isdisjoint(signal):
            break
        retained.append(turn['user'][:450])
    context = memory.context(previous)
    context['recent_user_messages'] = list(reversed(retained[:2]))
    # Un resumen mezclado no vuelve a introducir el tema descartado.
    if target and topics(context['summary']) - target:
        context['summary'] = ''
    return context, {'action': 'recent_topic_context', 'topic_change': False, 'topics': sorted(target)}


class EvidenceMismatch(ValueError):
    """Salida con citas auténticas pero señales de desalineación con el caso."""


def validate_alignment(decision, query):
    """Control conservador de tema, categoría y citas; no prueba implicación de cada afirmación."""
    expected = topics(query)
    if len(expected) != 1:
        return  # Casos mixtos/ambiguos requieren revisión humana, no clasificación forzada.
    topic = next(iter(expected))
    category = {'billing': 'Facturación', 'commercial': 'Dudas Comerciales'}.get(topic, 'Soporte Técnico')
    # Son tres controles independientes: categoría, contenido del borrador y citas.
    # Una cita literal puede fallar aquí si trata Firefox y la consulta pide VPN.
    cited = ' '.join(c.quote for c in decision.citations)
    if decision.category != category:
        raise EvidenceMismatch('Categoría incompatible con el tema detectado; revisar evidencia.')
    if topic not in topics(decision.suggested_reply):
        raise EvidenceMismatch('La respuesta no contiene una señal del tema detectado; puede ser desalineación o una paráfrasis no reconocida.')
    if topic not in topics(cited):
        raise EvidenceMismatch('Las citas no contienen una señal del tema detectado; no basta con que existan en el documento.')
