"""Regresiones de la retroalimentación docente: recuperación, contaminación y respaldo."""
from unittest.mock import Mock
import numpy as np
import pytest
import httpx
from catia.agent import ConversationAgent
from catia.config import read_config
from catia.generation import DemoGenerator
from catia.guardrails import EvidenceMismatch, expand_query, validate_alignment
from catia.memory import MemoryStore
from catia.retrieval import Retriever
from catia.schemas import Ticket, Decision


@pytest.fixture
def agent(tmp_path):
    # Fixture aislada: SQLite temporal y simulador; no modifica memoria ni llama al LLM real.
    return ConversationAgent(Retriever(read_config()), DemoGenerator(), MemoryStore(tmp_path/'memory.sqlite3'))


def test_paraphrase_recovers_invoice_without_history(agent):
    # Reproduce P2: recuperar INT-FAC por expansión sin depender de un turno previo.
    result = agent.run(Ticket(text='me cobraron dos veces', use_context=False))
    assert result['status'] == 'draft'
    assert result['sources'][0]['doc_id'] == 'INT-FAC'
    assert result['decision']['category'] == 'Facturación'
    assert expand_query('dos veces visité el sitio') == 'dos veces visité el sitio'


def test_topic_change_isolates_generation_and_followup(agent):
    # Inspeccionamos lo que recibe el generador, no solo la categoría final: el
    # contexto de factura tampoco debe reaparecer en la siguiente pregunta genérica.
    first = agent.run(Ticket(text='Mi factura tiene un cobro duplicado'))
    real_demo = agent.generator.generate
    agent.generator.generate = Mock(wraps=real_demo)
    vpn = agent.run(Ticket(text='no me conecta la VPN', session_id=first['session_id']))
    assert vpn['context_control']['topic_change'] and not vpn['memory']['used']
    assert agent.generator.generate.call_args.kwargs['memory'] == {}
    assert vpn['decision']['category'] != 'Facturación'
    followup = agent.run(Ticket(text='¿Qué debo hacer en ese caso?', session_id=first['session_id']))
    used = agent.generator.generate.call_args.kwargs['memory']
    assert 'factura' not in str(used).lower()
    assert followup['decision']['category'] != 'Facturación'


def test_literal_quote_does_not_validate_wrong_answer(agent):
    # La cita existe realmente en INT-NET, pero el borrador habla de factura.
    # El Mock inyecta el error de forma reproducible; no simula una prueba de calidad del LLM.
    hit = next(c for c in agent.retriever.chunks if c.doc_id == 'INT-NET')
    wrong = Decision(category='Facturación', summary='Consulta de VPN',
        suggested_reply='Revise la factura para confirmar si hay dos cobros del mismo servicio.',
        justification='Ejemplo controlado del fallo observado por el docente.',
        citations=[{'source_id':hit.id,'quote':hit.text}], needs_review=True)
    agent.generator.generate = Mock(return_value=(wrong, {}))
    result = agent.run(Ticket(text='no me conecta la VPN'))
    assert result['status'] == 'evidence_mismatch'
    assert not result['decision']['citations']
    assert 'Revise la factura' not in result['decision']['suggested_reply']
    with agent.memory.connect() as db:
        assert db.execute('SELECT COUNT(*) FROM case_notes').fetchone()[0] == 0


def test_right_category_with_unrelated_quote_is_rejected():
    # Tener categoría correcta no basta: una cita de Firefox no respalda el tema VPN.
    wrong = Decision(category='Soporte Técnico', summary='La VPN no conecta',
        suggested_reply='Para la VPN registre el error y la hora.', justification='Prueba de cita no pertinente.',
        citations=[{'source_id':'INT-NET:0','quote':'Si falla Firefox pero otro navegador funciona, revisar datos del sitio.'}], needs_review=True)
    with pytest.raises(EvidenceMismatch):
        validate_alignment(wrong, 'no me conecta la VPN')


def test_tool_writes_and_delete_erases_long_memory(agent):
    # Reabrir SQLite comprueba persistencia, y un segundo UUID comprueba aislamiento.
    r = agent.run(Ticket(text='Mi factura tiene un cobro duplicado'))
    note = r['tool_events'][-1]['observation']['saved_draft_id']
    reopened = MemoryStore(agent.memory.path)
    with reopened.connect() as db:
        assert db.execute('SELECT id FROM case_notes WHERE session_id=?', (r['session_id'],)).fetchone()[0] == note
    # Vectores controlados comprueban aislamiento y uso; no miden calidad de embeddings.
    embeddings = Mock()
    embeddings.encode.side_effect = lambda texts: np.tile([1.,0.], (len(texts),1))
    assert reopened.search_notes(r['session_id'], 'factura', embeddings)[0]['note_id'] == note
    other = reopened.create()
    assert reopened.search_notes(other, 'factura', embeddings) == []
    reopened.delete(r['session_id'])
    assert reopened.search_notes(r['session_id'], 'factura', embeddings) == []


def test_insufficient_source_and_provider_failure(agent, monkeypatch):
    # Primer caso: el filtro excluye el procedimiento necesario. Segundo caso:
    # se simula una conexión fallida sin apagar Ollama ni cambiar la configuración.
    absent = agent.run(Ticket(text='me cobraron dos veces', source_filter='external'))
    assert absent['status'] == 'insufficient_context'
    agent.generator = Mock(name='provider', model='unavailable', url='http://unavailable')
    agent.generator.name = 'ollama'
    monkeypatch.setattr(httpx, 'post', Mock(side_effect=httpx.ConnectError('controlled failure')))
    failed = agent.run(Ticket(text='Mi factura tiene un cobro duplicado'))
    assert failed['status'] == 'provider_error' and not failed['fallback_used']
