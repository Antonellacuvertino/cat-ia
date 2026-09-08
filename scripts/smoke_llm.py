"""Una prueba real del pipeline; conserva estado y salida sin fingir éxito."""
import json
from catia.agent import Agent
from catia.config import ROOT, read_config
from catia.generation import OllamaGenerator
from catia.retrieval import Retriever
from catia.schemas import Ticket

if __name__ == "__main__":
    # Ejecuta una inferencia real; comprobar Ollama antes y reservar tiempo de espera.
    result=Agent(Retriever(read_config()),OllamaGenerator()).run(Ticket(
        text="El portal no inicia sesión en Firefox. ¿Cómo reviso las cookies y los datos del sitio?"))
    (ROOT/"reports/llm_smoke.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({k:result[k] for k in ["status","model","decision","timings","usage"]},ensure_ascii=False,indent=2))
    # Un HTTP correcto no basta: la prueba exige un borrador con salida y citas validadas.
    if result["status"] != "draft":
        raise SystemExit("La inferencia real no produjo un borrador validado; ver evidencia.")
