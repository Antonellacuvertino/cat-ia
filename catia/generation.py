"""Proveedores intercambiables; el simulador jamás se presenta como un LLM."""
import json
import os
import re

import httpx

from .config import ROOT
from .schemas import Decision


def build_messages(ticket, hits, version):
    """Separa el prompt del sistema de los datos no confiables del ticket y del corpus."""
    system = (ROOT / "prompts" / f"{version}.txt").read_text(encoding="utf-8")
    # JSON delimita datos; la defensa frente a inyección se complementa con
    # validación y revisión humana. Ningún delimitador garantiza inmunidad.
    payload = {"ticket": ticket, "documents": [
        {"source_id": h["id"], "title": h["title"], "type": h["source_type"], "text": h["text"]}
        for h in hits]}
    return [{"role": "system", "content": system},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)}]


class OllamaGenerator:
    """Proveedor LLM real: solicita una respuesta JSON y valida el contrato de Decision."""
    name = "ollama"

    def __init__(self):
        """Lee el modelo y la URL de .env o del entorno; no descarga ni inicia Ollama."""
        self.model = os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b")
        self.url = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")

    def generate(self, ticket, hits, version):
        """Restringe las citas a opciones del contexto y devuelve decisión y uso de tokens."""
        # El mismo contrato de Python se convierte en restricciones para la generación.
        schema = Decision.model_json_schema()
        if hits:
            schema["properties"]["citations"]["minItems"] = 1
            # El modelo elige evidencia; el esquema limita las opciones a
            # identificadores y extractos reales. No certifica respaldo semántico.
            choices = []
            for hit in hits:
                quotes = [s for s in re.split(r"(?<=[.!?])\s+", hit["text"]) if 12 <= len(s) <= 1200]
                if not quotes:
                    quotes = [hit["text"][:1200]]
                # Cada alternativa vincula un ID concreto con citas de ese mismo fragmento.
                choices.append({"type": "object", "properties": {
                    "source_id": {"type": "string", "const": hit["id"]},
                    "quote": {"type": "string", "enum": quotes}},
                    "required": ["source_id", "quote"], "additionalProperties": False})
            schema["$defs"]["Evidence"] = {"anyOf": choices}
        # Petición síncrona local: espera la respuesta completa y limita tiempo y longitud.
        # temperature=0 reduce variación, pero no constituye garantía de exactitud.
        response = httpx.post(self.url + "/api/chat", json={
            "model": self.model, "messages": build_messages(ticket, hits, version),
            "stream": False, "format": schema,
            "options": {"temperature": 0, "num_predict": 1100, "num_ctx": 4096},
        }, timeout=120)
        response.raise_for_status()
        data = response.json()
        # Validar otra vez detecta salidas que no respetan el contrato del proyecto.
        decision = Decision.model_validate_json(data["message"]["content"])
        return decision, {"input_tokens": data.get("prompt_eval_count"),
                          "output_tokens": data.get("eval_count")}


class DemoGenerator:
    """Simulador determinista para practicar la aplicación sin descargar un modelo."""
    name = "demo"
    model = "simulador-extractivo-v1 (sin LLM)"

    def generate(self, ticket, hits, version):
        """Clasifica por palabras clave y copia extractos; no ejecuta ni evalúa un LLM."""
        text = ticket.lower()
        if any(w in text for w in ["factur", "cobro", "cobraron", "cargo", "pago"]):
            category = "Facturación"
        elif any(w in text for w in ["precio", "plan", "cotiz", "contratar", "comercial"]):
            category = "Dudas Comerciales"
        elif any(w in text for w in ["sugier", "sugerencia", "propongo", "mejora"]):
            category = "Sugerencias"
        elif any(w in text for w in ["firefox", "vpn", "acceso", "contraseña", "error", "internet", "correo", "phishing", "portal"]):
            category = "Soporte Técnico"
        else:
            category = "No determinado"
        # El simulador copia hasta dos evidencias y no interpreta las versiones del prompt.
        selected = hits[:2]
        sentences = [re.split(r"(?<=[.!?])\s+", h["text"]) for h in selected]
        quotes = [parts[1 if len(parts) > 1 else 0][:1000] for parts in sentences]
        reply = "Orientación extraída de la base documental:\n" + "\n".join(quotes)
        result = Decision(category=category, summary=ticket[:300], suggested_reply=reply,
                          justification="Simulación: clasificación por reglas y extractos recuperados; revisar adecuación al caso.",
                          citations=[{"source_id": h["id"], "quote": q} for h, q in zip(selected, quotes)],
                          needs_review=True)
        return result, {"input_tokens": None, "output_tokens": None}
