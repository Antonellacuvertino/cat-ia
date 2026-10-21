"""Reproduce P1–P3 y compara recuperación; conserva resultados reales, incluso fallos."""
import json
from datetime import datetime, timezone
from catia.config import ROOT, read_config
from catia.agent import ConversationAgent
from catia.generation import OllamaGenerator
from catia.memory import MemoryStore
from catia.retrieval import Retriever, OllamaEmbeddings
from catia.schemas import Ticket
from catia.guardrails import expand_query


def main():
    """Usa un hilo sintético aislado; borra sus datos al finalizar, no los hilos de la app."""
    generator = OllamaGenerator()
    lexical = Retriever(read_config())
    embeddings = OllamaEmbeddings(generator.url, 'nomic-embed-text')
    hybrid = Retriever(read_config(), embeddings=embeddings)
    comparisons = []
    # Separamos tres condiciones para no atribuir a embeddings una mejora que
    # podría proceder únicamente de añadir «factura cobro duplicado» a la consulta.
    for query in ['me cobraron dos veces', 'me descontaron el doble', 'no me conecta la VPN',
                  'necesito revisar el importe repetido en el recibo']:
        row = {'query': query}
        for name, retriever, text in [('lexical_original',lexical,query),
                                      ('lexical_expanded',lexical,expand_query(query)), ('hybrid',hybrid,query)]:
            row[name] = [{'id':h['id'], 'score':h['score']} for h in retriever.search(text)]
        comparisons.append(row)
    report = {'created_at': datetime.now(timezone.utc).isoformat(), 'model': generator.model,
              'embedding_model': embeddings.model, 'retrieval_comparison': comparisons, 'rows': [],
              'scope': 'Regresión conocida P1–P3; no evaluación independiente ni comparación de tamaños de modelo.'}
    path = ROOT/'reports/feedback_real.json'
    memory = MemoryStore(ROOT/'runtime/feedback.sqlite3')
    agent = ConversationAgent(hybrid, generator, memory)
    sid = memory.create()
    try:
        for label, query, context in [('P1a','Mi factura tiene un cobro duplicado',True),
                ('P1b','¿Qué debo hacer en ese caso?',True),
                ('P2','me cobraron dos veces',False), ('P3','no me conecta la VPN',True)]:
            print('Ejecutando', label, flush=True)
            result = agent.run(Ticket(text=query, session_id=sid, use_context=context))
            report['rows'].append({'case':label,'result':result})
            # Guardar tras cada caso conserva evidencia parcial si una llamada posterior falla.
            path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
            print(label, result['status'], result['decision']['category'], flush=True)
        # Registros anteriores fuera de la ventana se buscan con embeddings reales.
        recalled = memory.search_notes(sid, 'Me cobraron dos veces el mismo servicio', embeddings)
        report['semantic_history_ids'] = [r['note_id'] for r in recalled]
        report['passed'] = (all(r['result']['status']=='draft' for r in report['rows'])
                            and report['rows'][-1]['result']['decision']['category']=='Soporte Técnico'
                            and report['rows'][-1]['result']['context_control']['topic_change']
                            and bool(recalled))
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        print('Resultado de regresión:', report['passed'])
    finally:
        # Solo se borra el UUID sintético creado por este ensayo, no las sesiones de la app.
        memory.delete(sid)


if __name__ == '__main__':
    main()
