"""Genera entregables EA2 a partir de documentación y evidencia local, sin inventar métricas."""
import json
import re
import xml.etree.ElementTree as ET

from scripts.build_documents import (ROOT, OUT, AUTHORS, FONT, BOLD, GREEN, LIME,
                                     PAPER, MUTED, rich, markdown_pdf)
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph


def paragraph(c, text, x, y, width, size=19, color=GREEN):
    """Dibuja texto con ajuste de línea y devuelve su altura para evitar superposiciones."""
    p = Paragraph(rich(text).replace('\n', '<br/>'), ParagraphStyle('ea2', fontName=FONT, fontSize=size,
                                            leading=size * 1.35, textColor=color))
    _, height = p.wrap(width, 450)
    p.drawOn(c, x, y - height)
    return height


def results():
    """Lee JUnit, cobertura y smoke tests; diferencia simulador de inferencia real."""
    root = ET.parse(ROOT / 'reports/tests_ea2.xml').getroot()
    cases = root.findall('.//testcase')
    failures = sum(c.find('failure') is not None or c.find('error') is not None for c in cases)
    skipped = sum(c.find('skipped') is not None for c in cases)
    coverage = json.loads((ROOT / 'reports/coverage_ea2.json').read_text('utf-8'))['totals']['percent_covered']
    lines = ['# Resultados verificables · EA2',
             'Autoras: ' + AUTHORS + '. Actualización: 11/10/2026.',
             '## Software',
             f'{len(cases)} pruebas: {failures} fallos y {skipped} omitidas. Cobertura de líneas: {coverage:.1f} %. Evidencia: reports/tests_ea2.xml y reports/coverage_ea2.json.',
             'Incluyen las pruebas anteriores y las de continuidad, aislamiento, persistencia, borrado, concurrencia local, herramientas, API, errores y CrewAI real con generación simulada.',
             '## Integración por proveedor']
    for path in sorted((ROOT / 'reports').glob('ea2_*_*.json')):
        report = json.loads(path.read_text('utf-8'))
        if 'rows' not in report:
            continue
        states = ', '.join(r['status'] for r in report['rows'])
        times = ', '.join(f"{r['timings']['total_ms']/1000:.1f} s" for r in report['rows'])
        lines.append(f"- {report['provider']} / {report['mode']}: {'PASA' if report['passed'] else 'FALLA'}; estados {states}; duración por caso {times}. Fuente: {path.name}; fecha {report['created_at']}.")
    browser = ROOT / 'reports/browser_checks_ea2.json'
    if browser.exists():
        b = json.loads(browser.read_text('utf-8'))
        lines += ['## Interfaz', f"Resultado: {'PASA' if b['passed'] else 'FALLA'}. " + '; '.join(b['checks']) + '. Evidencia: reports/browser_checks_ea2.json.']
    else:
        lines += ['## Interfaz', 'Verificación automatizada de navegador todavía no registrada.']
    lines += ['## Alcance y límites',
              'Los casos de integración son sintéticos y pequeños. No constituyen una evaluación independiente de fidelidad, relevancia o generalización. La validación de citas comprueba procedencia y coincidencia textual; la revisión semántica sigue siendo humana.',
              'Las métricas de EA1 pertenecen a su implementación y prompt v3; no se transfieren al agente EA2 con prompt v4. La cobertura no mide calidad del LLM. Las latencias dependen del hardware y la carga.',
              'Se observaron advertencias de deprecación en dependencias CrewAI/Pydantic durante las pruebas. No impidieron completarlas; revisar al actualizar versiones.']
    text = '\n\n'.join(lines) + '\n'
    (ROOT / 'reports/EA2_RESULTADOS.md').write_text(text, encoding='utf-8')
    return text


def slides():
    """Ocho diapositivas breves, con la misma fuente editable que usa el guion."""
    sections = re.split(r'\n(?=## )', (ROOT / 'docs/10_presentacion_ea2.md').read_text('utf-8'))
    c = canvas.Canvas(str(OUT / 'presentacion_EA2_CAT-IA.pdf'), pagesize=(960, 540))
    c.setTitle('CAT-IA · Experiencia 2'); c.setAuthor(AUTHORS)
    for i, section in enumerate(sections):
        c.setFillColor(GREEN if i == 0 else PAPER); c.rect(0, 0, 960, 540, fill=1, stroke=0)
        c.setFillColor(LIME if i == 0 else GREEN); c.setFont(BOLD, 13)
        c.drawString(48, 490, 'CAT-IA / EXPERIENCIA 2')
        lines = [line for line in section.splitlines() if line.strip()]
        paragraph(c, lines[0].lstrip('# '), 48, 440, 860, 36, colors.white if i == 0 else GREEN)
        y = 335
        for line in lines[1:]:
            h = paragraph(c, line.removeprefix('- '), 55, y, 845, 19 if i == 0 else 24,
                          colors.white if i == 0 else GREEN)
            y -= h + 22
        if y < 40:
            raise ValueError(f'Diapositiva {i+1} demasiado extensa')
        c.setFont(FONT, 10); c.setFillColor(LIME if i == 0 else MUTED)
        c.drawString(48, 24, 'Nexo TI · Organización ficticia · Revisión humana obligatoria')
        c.drawRightString(912, 24, f'{i+1} / {len(sections)}'); c.showPage()
    c.save()


def architecture():
    """Diagrama vectorial legible, equivalente al flujo Mermaid entregado."""
    c = canvas.Canvas(str(OUT / 'arquitectura_EA2.pdf'), pagesize=(960, 620))
    c.setTitle('Arquitectura CAT-IA EA2'); c.setAuthor(AUTHORS)
    c.setFillColor(PAPER); c.rect(0, 0, 960, 620, fill=1, stroke=0)
    paragraph(c, 'CAT-IA · Arquitectura EA2', 35, 590, 850, 28)
    def box(x, y, w, text):
        c.setFillColor(LIME); c.setStrokeColor(GREEN); c.roundRect(x, y, w, 64, 9, fill=1)
        paragraph(c, text, x+12, y+51, w-24, 13)
    def arrow(x1, y1, x2, y2):
        c.setStrokeColor(GREEN); c.line(x1, y1, x2, y2)
        import math
        a = math.atan2(y2-y1, x2-x1)
        for delta in (-0.45, 0.45):
            c.line(x2, y2, x2-8*math.cos(a+delta), y2-8*math.sin(a+delta))
    box(30, 450, 190, 'Interfaz web\nTicket + sesión + modo')
    box(280, 450, 190, 'API FastAPI\nValidación y redacción PII')
    box(535, 450, 190, 'ConversationAgent\nCoordinación del caso')
    box(770, 450, 165, 'SQLite\nVentana + resumen')
    arrow(220,482,280,482); arrow(470,482,535,482); arrow(725,482,770,482)
    arrow(770,472,725,472)
    box(210, 320, 230, 'Individual: ReAct acotado\nHerramientas LangChain')
    box(505, 320, 330, 'CrewAI secuencial\nTriage → Investigador → Redactor')
    arrow(600,450,325,384); arrow(650,450,670,384)
    box(310, 200, 360, 'Herramientas tipadas\nPolítica SLA · Recuperación · Borrador')
    arrow(325,320,435,264); arrow(670,320,560,264)
    box(30, 200, 230, 'Corpus interno + externo\nTF-IDF / híbrido opcional')
    arrow(260,232,310,232)
    box(730, 200, 205, 'Ollama local / demo\nPrompt v4 + contexto')
    arrow(670,232,730,232)
    arrow(730,222,670,222)
    box(280, 75, 405, 'Validar citas → borrador o abstención\nTrazas de herramientas → revisión humana')
    arrow(490,200,490,139)
    paragraph(c, 'El fallback a demo requiere activación explícita. Ningún agente envía respuestas ni modifica cuentas.', 35, 40, 890, 11)
    c.save()


def build():
    """Punto de entrada reutilizable desde verificar.bat y la generación general."""
    OUT.mkdir(exist_ok=True)
    report = results()
    documents = []
    for name in ('03_agentes_ea2', '11_guion_clase_ea2'):
        source = (ROOT / f'docs/{name}.md').read_text('utf-8')
        documents.append(source)
        # El guion se conserva separado para practicar; el informe y los resultados
        # se consultan en el dossier, sin duplicar sus capítulos en otros PDF.
        if name == '11_guion_clase_ea2':
            markdown_pdf(source, OUT / f'{name}.pdf')
    markdown_pdf('\n\n'.join(documents + [report]), OUT / 'dossier_EA2_CAT-IA.pdf')
    slides(); architecture()
    print('Entregables EA2 generados en', OUT)


if __name__ == '__main__':
    build()
