"""Diagnóstico de salida en un ticket exclusivamente sintético, sin datos de usuario."""
import json
from catia.config import ROOT, read_config
from catia.retrieval import Retriever
from catia.generation import OllamaGenerator
from catia.agent import validate_evidence

if __name__ == "__main__":
    text="El portal no inicia sesión en Firefox. ¿Cómo reviso las cookies y los datos del sitio?"
    # Aísla recuperación y generación para diagnosticar la versión v2 con un caso ficticio fijo.
    hits=Retriever(read_config()).search(text)
    d,u=OllamaGenerator().generate(text,hits,"v2")
    print(d.model_dump_json(indent=2))
    validate_evidence(d,hits)
    print("Citas válidas",u)
