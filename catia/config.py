"""Configuración explícita y validada; nunca contiene credenciales."""
import json
import os
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from pydantic import BaseModel, Field, model_validator

# Resuelve recursos desde el proyecto, independientemente de la carpeta de la terminal.
ROOT = Path(__file__).resolve().parent.parent
# Las variables ya definidas en el proceso tienen prioridad sobre el archivo .env.
load_dotenv(ROOT / ".env")


class RAGConfig(BaseModel):
    """Define los parámetros del RAG y rechaza valores fuera de los límites declarados."""
    # Tamaño de cada ventana en palabras; no equivale a tokens del LLM.
    chunk_words: int = Field(default=110, ge=30, le=500)
    # Repite palabras para conservar continuidad entre fragmentos consecutivos.
    overlap_words: int = Field(default=20, ge=0)
    # Máximo de fragmentos; pueden llegar menos por umbral, filtro o presupuesto.
    top_k: int = Field(default=4, ge=1, le=8)
    # Piso de similitud de recuperación; no representa certeza del modelo.
    min_score: float = Field(default=0.06, ge=0, le=1)
    # Limita texto documental; no cuenta las instrucciones ni el ticket.
    max_context_chars: int = Field(default=6500, ge=1500, le=12000)
    # Solo en modo híbrido: peso de la señal densa frente a la señal léxica.
    semantic_weight: float = Field(default=0.55, ge=0, le=1)
    # Selecciona el archivo prompts/<versión>.txt utilizado como instrucción de sistema.
    prompt_version: Literal["v1", "v2", "v3"] = "v3"

    @model_validator(mode="after")
    def valid_overlap(self):
        """Evita un avance nulo o negativo al construir las ventanas de palabras."""
        if self.overlap_words >= self.chunk_words:
            raise ValueError("El solapamiento debe ser menor que el fragmento")
        return self


def read_config() -> RAGConfig:
    """Lee config/rag.json en UTF-8 y valida sus valores antes de crear el índice."""
    return RAGConfig.model_validate(json.loads((ROOT / "config/rag.json").read_text(encoding="utf-8")))


def provider_name() -> str:
    """Selecciona el proveedor explícito; un nombre incorrecto detiene la configuración."""
    value = os.getenv("CATIA_PROVIDER", "demo")
    if value not in {"demo", "ollama"}:
        raise ValueError("CATIA_PROVIDER debe ser demo u ollama")
    return value
