"""Ejecuta casos sintéticos EA2 y guarda evidencia separada de los resultados EA1."""
import argparse
import json
from datetime import datetime, timezone

from catia.agent import ConversationAgent
from catia.config import ROOT, read_config
from catia.generation import DemoGenerator, OllamaGenerator
from catia.memory import MemoryStore
from catia.retrieval import Retriever
from catia.schemas import Ticket


def main():
    """Distingue integración con simulador de inferencia real; no habilita fallback durante la evaluación."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", choices=["demo", "ollama"], default="demo")
    parser.add_argument("--mode", choices=["react", "crew"], default="react")
    parser.add_argument("--followup", action="store_true")
    args = parser.parse_args()
    generator = OllamaGenerator() if args.provider == "ollama" else DemoGenerator()
    memory = MemoryStore(ROOT / "runtime/smoke_ea2.sqlite3")
    agent = ConversationAgent(Retriever(read_config()), generator, memory, mode=args.mode)
    sid = memory.create()
    texts = ["El portal no inicia sesión en Firefox, pero funciona en otro navegador. ¿Cómo reviso las cookies y los datos del sitio?"]
    if args.followup:
        texts.append("Ya hice esa revisión y sigue igual. ¿Qué antecedente debo entregar al operador?")
    rows = []
    try:
        for text in texts:
            print(f"Ejecutando {args.provider}/{args.mode}: caso {len(rows)+1}", flush=True)
            rows.append(agent.run(Ticket(text=text, session_id=sid)))
        report = {"created_at": datetime.now(timezone.utc).isoformat(), "provider": args.provider,
                  "mode": args.mode, "passed": all(r["status"] == "draft" and not r["fallback_used"] for r in rows),
                  "scope": "Integración sintética, no evaluación independiente de fidelidad o generalización.", "rows": rows}
        path = ROOT / f"reports/ea2_{args.provider}_{args.mode}.json"
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(path)
        print(json.dumps({"passed": report["passed"], "states": [r["status"] for r in rows],
                          "timings_ms": [r["timings"]["total_ms"] for r in rows]}, ensure_ascii=False))
        if not report["passed"]:
            raise SystemExit(1)
    finally:
        memory.delete(sid)


if __name__ == "__main__":
    main()
