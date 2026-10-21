"""Herramientas LangChain con estado aislado por solicitud y contratos verificables."""
import time
from dataclasses import dataclass, field
from typing import Literal

from langchain_core.tools import tool

from .agent import priority_for, validate_evidence
from .guardrails import EvidenceMismatch, topics, validate_alignment


@dataclass
class ToolContext:
    """Comparte resultados entre herramientas sin exponer objetos globales ni otras sesiones."""
    ticket: object
    clean: str
    query: str
    memory: dict
    retriever: object
    generator: object
    hits: list = field(default_factory=list)
    completed: list = field(default_factory=list)
    events: list = field(default_factory=list)
    decision: object = None
    priority: str = "Baja"
    sla: int = 24
    usage: dict = field(default_factory=lambda: {"input_tokens": None, "output_tokens": None})
    retrieval_ms: float = 0
    generation_ms: float = 0
    store: object = None
    session_id: str | None = None
    use_history: bool = False


def create_tools(state: ToolContext):
    """Construye herramientas tipadas; el modelo nunca puede cambiar impacto o inventar evidencia."""

    @tool
    def tool_search_knowledge_base(query: str, top_k: int = 4) -> dict:
        """Recupera evidencia del corpus interno y externo de Nexo TI.

        Args:
            query: Consulta de soporte sin secretos, como máximo 6000 caracteres.
            top_k: Máximo de fragmentos entre 1 y 8; respeta filtro y presupuesto.
        """
        if not query.strip() or len(query) > 6000 or not 1 <= top_k <= 8:
            raise ValueError("Argumentos de recuperación inválidos")
        start = time.perf_counter()
        state.hits = state.retriever.search(query, top_k, state.ticket.source_filter)
        target = topics(query)
        if len(target) == 1:
            # Una similitud densa no basta: para temas conocidos exigimos señal en el documento.
            state.hits = [h for h in state.hits if target & topics(h['title'] + ' ' + h['text'])]
        recalled = []
        if state.store and state.use_history and state.retriever.embeddings:
            recalled = state.store.search_notes(state.session_id, query, state.retriever.embeddings)
            if recalled:
                state.memory['semantic_history'] = [r['user'] for r in recalled]
        state.retrieval_ms += (time.perf_counter() - start) * 1000
        return {"count": len(state.hits), "source_ids": [h["id"] for h in state.hits],
                "sufficient_for_draft": bool(state.hits),
                "semantic_history_ids": [r['note_id'] for r in recalled]}

    @tool
    def tool_check_sla_policy(impact: Literal["individual", "equipo", "organizacion"],
                              service_down: bool = False, security_incident: bool = False) -> dict:
        """Consulta la política determinista de primera respuesta, no un plazo de resolución.

        Args:
            impact: Alcance declarado por el operador; debe coincidir con el ticket.
            service_down: Indica interrupción confirmada por el operador.
            security_incident: Indica posible incidente de seguridad declarado.
        """
        actual = (state.ticket.impact, state.ticket.service_down, state.ticket.security_incident)
        if (impact, service_down, security_incident) != actual:
            raise ValueError("La herramienta no puede alterar el impacto declarado")
        state.priority, state.sla = priority_for(state.ticket)
        return {"priority": state.priority, "first_response_hours": state.sla, "policy_id": "INT-SLA"}

    @tool
    def tool_draft_response() -> dict:
        """Genera y valida un borrador con las evidencias recuperadas en esta solicitud.

        No recibe citas del planificador: utiliza únicamente el estado de recuperación.
        Requiere búsqueda y política completadas. La memoria nunca es fuente citable.
        """
        required = {"tool_search_knowledge_base", "tool_check_sla_policy"}
        if not required.issubset(state.completed):
            raise ValueError("Faltan búsqueda o política antes de redactar")
        if not state.hits:
            return {"status": "insufficient_context", "draft_created": False}
        start = time.perf_counter()
        decision, state.usage = state.generator.generate(state.clean, state.hits, "v4", memory=state.memory)
        validate_evidence(decision, state.hits)
        validate_alignment(decision, state.query)
        decision.needs_review = True
        state.decision = decision
        note_id = None
        if state.store:
            note_id = state.store.save_draft(state.session_id, state.clean, decision.model_dump())
        state.generation_ms += (time.perf_counter() - start) * 1000
        return {"status": "draft", "category": decision.category,
                "citation_count": len(decision.citations), "human_approval_required": True,
                "saved_draft_id": note_id, "write_target": "SQLite case_notes" if note_id else None}

    return {t.name: t for t in [tool_search_knowledge_base, tool_check_sla_policy, tool_draft_response]}


def arguments_for(name: str, state: ToolContext) -> dict:
    """Vincula argumentos a datos validados; la decisión de herramienta no autoriza alterar el ticket."""
    if name == "tool_search_knowledge_base":
        return {"query": state.query, "top_k": state.ticket.top_k or state.retriever.config.top_k}
    if name == "tool_check_sla_policy":
        return {"impact": state.ticket.impact, "service_down": state.ticket.service_down,
                "security_incident": state.ticket.security_incident}
    if name == "tool_draft_response":
        return {}
    raise ValueError("Herramienta no permitida")


def execute_tool(name: str, state: ToolContext, registry: dict, actor: str) -> dict:
    """Invoca el contrato LangChain y registra observaciones breves, no razonamiento privado."""
    if name not in registry or name in state.completed:
        raise ValueError("Herramienta desconocida o llamada repetida")
    start = time.perf_counter()
    try:
        result = registry[name].invoke(arguments_for(name, state))
    except Exception as exc:
        detail = str(exc) if isinstance(exc, EvidenceMismatch) else 'La herramienta falló; no se acepta un resultado inventado.'
        state.events.append({"actor": actor, "tool": name, "status": "error", "observation": detail})
        raise
    state.completed.append(name)
    state.events.append({"actor": actor, "tool": name, "status": "ok", "observation": result,
                         "elapsed_ms": round((time.perf_counter() - start) * 1000, 2)})
    return result
