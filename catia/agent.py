"""Agente acotado: observar, recuperar, consultar políticas, generar, validar.

La autonomía es de flujo y no de ejecución sobre sistemas del cliente.
Los errores del proveedor terminan en abstención, nunca en una falsa respuesta LLM.
"""
import hashlib
import json
import re
import time
import uuid
from datetime import datetime, timezone

from .config import ROOT
from .schemas import Decision, Ticket


def redact(text):
    """Oculta patrones conocidos de correo, RUT y secretos etiquetados; no anonimiza todo dato personal."""
    text = re.sub(r"[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}", "[EMAIL]", text)
    text = re.sub(r"\b\d{1,2}\.?\d{3}\.?\d{3}-[\dkK]\b", "[RUT]", text)
    text = re.sub(r"(?i)\b(contraseña|password|token|clave)\s*[:=]\s*\S+", r"\1=[SECRETO]", text)
    return text


def priority_for(ticket):
    """Aplica la política interna: devuelve prioridad y horas hábiles de primera respuesta."""
    # Seguridad o caída de toda la organización: primera respuesta en una hora hábil.
    if ticket.security_incident or (ticket.service_down and ticket.impact == "organizacion"):
        return "Alta", 1
    if ticket.service_down or ticket.impact in {"equipo", "organizacion"}:
        return "Media", 4
    return "Baja", 24


def validate_evidence(decision, hits):
    """Exige citas existentes en los fragmentos; no prueba que la respuesta esté respaldada semánticamente."""
    sources = {h["id"]: h["text"] for h in hits}
    if not decision.citations:
        raise ValueError("Sin citas verificables")
    for citation in decision.citations:
        if citation.source_id not in sources or citation.quote not in sources[citation.source_id]:
            raise ValueError("La cita no pertenece al contexto recuperado")


class Agent:
    """Orquesta herramientas en un flujo acotado y entrega un borrador para revisión humana."""
    def __init__(self, retriever, generator, trace_dir=None):
        """Recibe recuperación y generación como dependencias intercambiables para facilitar pruebas."""
        self.retriever, self.generator = retriever, generator
        self.trace_dir = trace_dir

    def run(self, ticket: Ticket):
        """Procesa un Ticket validado y devuelve decisión, evidencia, estado, tiempos y trazabilidad."""
        started = time.perf_counter()
        steps = []
        def step(name, detail):
            """Registra un hito del flujo y el tiempo transcurrido para explicar el recorrido al usuario."""
            steps.append({"step": name, "detail": detail,
                          "elapsed_ms": round((time.perf_counter() - started) * 1000, 2)})
        # La recuperación y la generación reciben el texto con los patrones sensibles ocultos.
        clean = redact(ticket.text)
        step("preparar", "Datos redactados; entrada validada")
        retrieval_started = time.perf_counter()
        hits = self.retriever.search(clean, ticket.top_k, ticket.source_filter)
        retrieval_ms = (time.perf_counter() - retrieval_started) * 1000
        step("recuperar_documentos", f"{len(hits)} fragmentos; modo {self.retriever.mode}")
        priority, sla = priority_for(ticket)
        # La política de SLA es contexto obligatorio, separado del ranking RAG.
        policy = next(c for c in self.retriever.chunks if c.doc_id == "INT-SLA")
        step("consultar_politica", f"{policy.id}: {priority}; primera respuesta {sla} horas hábiles")
        status = "draft"
        usage = {"input_tokens": None, "output_tokens": None}
        reason = None
        generation_started = time.perf_counter()
        try:
            # Sin evidencia se evita la llamada al LLM y se devuelve abstención explícita.
            if not hits:
                status, reason = "insufficient_context", "No se recuperó evidencia suficiente para proponer una solución."
                raise ValueError(reason)
            decision, usage = self.generator.generate(clean, hits, self.retriever.config.prompt_version)
            step("generar", self.generator.model)
            # Segundo control: una cita debe existir literalmente en el contexto recuperado.
            validate_evidence(decision, hits)
            step("validar_citas", "Identificadores y extractos comprobados; fidelidad semántica requiere revisión")
        except Exception as exc:
            # Un fallo conserva el proveedor declarado: no se fabrica éxito con otro motor.
            if reason is None:
                status = "provider_error" if not isinstance(exc, ValueError) else "invalid_output"
                reason = "No fue posible obtener una salida validada. Revisar conexión, modelo y contrato de respuesta."
            decision = Decision(category="No determinado", summary=clean[:300],
                                suggested_reply=reason + " Derivar a un operador y solicitar más antecedentes.",
                                justification=reason, citations=[], needs_review=True)
            step("abstener", reason)
        generation_ms = (time.perf_counter() - generation_started) * 1000
        if ticket.security_incident:
            decision.needs_review = True
        step("revision_humana", "Borrador: el operador verifica evidencia y decide la acción")
        # UUID enlaza el resultado descargable con el registro técnico de esta ejecución.
        trace_id = str(uuid.uuid4())
        result = {
            "trace_id": trace_id, "created_at": datetime.now(timezone.utc).isoformat(),
            "status": status, "mode": self.generator.name, "model": self.generator.model,
            "retriever": self.retriever.mode, "prompt_version": self.retriever.config.prompt_version,
            "prompt_sha256": hashlib.sha256((ROOT / "prompts" / f"{self.retriever.config.prompt_version}.txt").read_bytes()).hexdigest(),
            "corpus_sha256": self.retriever.fingerprint, "config": self.retriever.config.model_dump(),
            "decision": decision.model_dump(), "priority": priority, "first_response_hours": sla,
            "policy": {"source_id": policy.id, "text": policy.text, "sha256": policy.sha256},
            "sources": hits, "steps": steps, "usage": usage,
            "timings": {"retrieval_ms": round(retrieval_ms, 2), "generation_ms": round(generation_ms, 2),
                        "total_ms": round((time.perf_counter() - started) * 1000, 2)},
            "human_approval_required": True,
        }
        if self.trace_dir:
            self.trace_dir.mkdir(parents=True, exist_ok=True)
            # Sin texto del ticket ni respuesta generada en el registro persistente.
            trace = {k: v for k, v in result.items() if k not in {"decision", "sources", "policy"}}
            trace["retrieved_ids"] = [h["id"] for h in hits]
            trace["category"] = decision.category
            (self.trace_dir / f"{trace_id}.json").write_text(json.dumps(trace, ensure_ascii=False, indent=2), encoding="utf-8")
        return result


class ConversationAgent(Agent):
    """EA2 añade memoria y herramientas; Agent conserva el baseline de EA1 para comparar."""

    def __init__(self, retriever, generator, memory, trace_dir=None, mode="react"):
        """Recibe memoria persistente e identifica el modo por defecto sin estado global de ticket."""
        super().__init__(retriever, generator, trace_dir)
        if mode not in {"react", "crew"}:
            raise ValueError("Modo de orquestación inválido")
        self.memory, self.mode = memory, mode

    def run(self, ticket: Ticket):
        """Serializa un hilo, ejecuta sus herramientas y conserva un intercambio redactado."""
        sid = str(ticket.session_id) if ticket.session_id else self.memory.create()
        with self.memory.locked(sid):
            previous = self.memory.get(sid)
            return self._run_session(ticket, sid, previous)

    def _run_session(self, ticket, sid, previous):
        """Coordina modos reales/demo y expone fallos de forma explícita y auditable."""
        from .generation import DemoGenerator
        from .orchestration import run_crew, run_react
        from .tools import ToolContext

        started = time.perf_counter()
        clean = redact(ticket.text)
        memory = self.memory.context(previous) if ticket.use_context else {}
        # Solo entradas humanas para búsqueda: nunca se indexan borradores del modelo.
        prior_queries = memory.get("recent_user_messages", [])
        query = (" ".join(prior_queries[-1:]) + " " + clean).strip()[:6000]
        state = ToolContext(ticket, clean, query, memory, self.retriever, self.generator)
        requested = ticket.orchestration or self.mode
        engine, status, warning = requested, "draft", None
        fallback = False
        try:
            engine = run_crew(state) if requested == "crew" else run_react(state)
            if state.decision is None:
                status = "insufficient_context"
        except Exception as exc:
            status = "dependency_missing" if isinstance(exc, ImportError) else (
                "invalid_output" if isinstance(exc, ValueError) else "provider_error")
            warning = {"code": status, "message": "No se completó la orquestación. Revisa modelo, herramientas o instalación de EA2."}
            # La continuidad en demo requiere opción explícita; jamás pasa por inferencia real.
            if ticket.allow_demo_fallback and status == "provider_error" and self.generator.name != "demo":
                failed_events = list(state.events)
                state = ToolContext(ticket, clean, query, memory, self.retriever, DemoGenerator())
                try:
                    engine = run_react(state)
                    state.events = failed_events + state.events
                    fallback = True
                    status = "fallback_demo" if state.decision else "insufficient_context"
                except Exception:
                    status = "provider_error"
        if state.decision is None or status in {"provider_error", "invalid_output", "dependency_missing"}:
            state.decision = Decision(category="No determinado", summary=clean[:300], citations=[], needs_review=True,
                suggested_reply="No se obtuvo un borrador con evidencia suficiente. Derivar al operador y revisar antecedentes o conexión.",
                justification="Abstención: contexto insuficiente o ejecución no validada.")
        state.decision.needs_review = True
        # Prioridad invariable incluso si la planificación falla antes de consultar la herramienta.
        priority, sla = priority_for(ticket)
        policy = next(c for c in self.retriever.chunks if c.doc_id == "INT-SLA")
        saved = self.memory.append(sid, clean, state.decision.model_dump(), status)
        steps = [{"step": "memoria", "detail": f"{previous['turn_count']} intercambios previos; contexto {'activado' if ticket.use_context else 'ignorado'}"}]
        steps += [{"step": e["tool"], "detail": f"{e['actor']}: {e['status']}"} for e in state.events]
        steps.append({"step": "revision_humana", "detail": "Revisar afirmaciones y citas antes de usar el borrador"})
        result = {
            "trace_id": str(uuid.uuid4()), "created_at": datetime.now(timezone.utc).isoformat(),
            "session_id": sid, "status": status, "mode": state.generator.name, "model": state.generator.model,
            "requested_provider": self.generator.name, "fallback_used": fallback, "warning": warning,
            "orchestration": {"requested": requested, "executed": engine}, "tool_events": state.events,
            "memory": {"previous_turns": previous["turn_count"], "turn_count": saved["turn_count"],
                       "window_size": self.memory.window, "retained_turns": len(saved["turns"]),
                       "summary": saved["summary"], "used": bool(ticket.use_context and previous["turn_count"]),
                       "summary_strategy": "extractive_user_messages"},
            "retriever": self.retriever.mode, "prompt_version": "v4",
            "prompt_sha256": hashlib.sha256((ROOT / "prompts/v4.txt").read_bytes()).hexdigest(),
            "corpus_sha256": self.retriever.fingerprint,
            "config": {**self.retriever.config.model_dump(), "prompt_version": "v4"},
            "decision": state.decision.model_dump(), "priority": priority, "first_response_hours": sla,
            "policy": {"source_id": policy.id, "text": policy.text, "sha256": policy.sha256},
            "sources": state.hits, "steps": steps, "usage": state.usage,
            "timings": {"retrieval_ms": round(state.retrieval_ms, 2), "generation_ms": round(state.generation_ms, 2),
                        "total_ms": round((time.perf_counter() - started) * 1000, 2)},
            "human_approval_required": True,
        }
        if self.trace_dir:
            self.trace_dir.mkdir(parents=True, exist_ok=True)
            # La memoria contiene contenido redactado; las trazas siguen guardando solo metadatos.
            trace = {k: v for k, v in result.items() if k not in {"decision", "sources", "policy", "memory"}}
            trace["retrieved_ids"] = [h["id"] for h in state.hits]
            trace["category"] = state.decision.category
            (self.trace_dir / f"{result['trace_id']}.json").write_text(json.dumps(trace, ensure_ascii=False, indent=2), encoding="utf-8")
        return result
