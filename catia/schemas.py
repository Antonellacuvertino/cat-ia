"""Contratos de API y salida del modelo: JSON sintáctico no basta."""
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator

Category = Literal["Soporte Técnico", "Facturación", "Dudas Comerciales", "Sugerencias", "No determinado"]
Priority = Literal["Baja", "Media", "Alta"]


class Ticket(BaseModel):
    """Contrato de entrada: texto e impacto declarado, más controles opcionales de recuperación."""
    # Rechazar campos desconocidos detecta errores de integración del cliente.
    model_config = ConfigDict(extra="forbid")
    text: str = Field(min_length=12, max_length=4000)
    # El operador declara el impacto; la política de prioridad no depende del LLM.
    impact: Literal["individual", "equipo", "organizacion"] = "individual"
    service_down: bool = False
    security_incident: bool = False
    # None conserva la configuración; un número la cambia solo para este ticket.
    top_k: int | None = Field(default=None, ge=1, le=8)
    source_filter: Literal["all", "internal", "external"] = "all"

    @field_validator("text")
    @classmethod
    def nonblank(cls, value):
        """Elimina espacios exteriores y rechaza textos sin una descripción mínima útil."""
        value = value.strip()
        if len(value) < 12:
            raise ValueError("Describe el problema en al menos 12 caracteres")
        return value


class Evidence(BaseModel):
    """Relaciona una cita textual con el identificador de un fragmento recuperado."""
    model_config = ConfigDict(extra="forbid")
    # Identifica un fragmento (ej. INT-ACC:0), no una URL ni solo el documento.
    source_id: str
    quote: str = Field(min_length=12, max_length=1200)


class Decision(BaseModel):
    """Contrato del borrador: categoría permitida, respuesta, justificación y evidencias."""
    model_config = ConfigDict(extra="forbid")
    category: Category
    summary: str = Field(min_length=5, max_length=320)
    suggested_reply: str = Field(min_length=10, max_length=2500)
    justification: str = Field(min_length=10, max_length=1000)
    citations: list[Evidence] = Field(max_length=8)
    # Agent exige aprobación humana para todo resultado, incluso si este campo es falso.
    needs_review: bool
