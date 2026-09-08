"""Evaluación reproducible de recuperación y clasificación, sin juez implícito.

Faithfulness y relevancia requieren revisión semántica y quedan sin resultado
hasta que una persona evalúe las respuestas; integridad de citas es otra métrica.
"""
import argparse
import hashlib
import json
from datetime import datetime, timezone

import numpy as np
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix

from catia.agent import Agent
from catia.config import ROOT, read_config
from catia.generation import DemoGenerator, OllamaGenerator
from catia.retrieval import Retriever
from catia.schemas import Ticket


def evaluate(provider="demo", split="test", top_k=4, prompt="v3", baseline=False):
    """Ejecuta el conjunto dev o test y calcula métricas con etiquetas conocidas y trazas por caso."""
    cases_path = ROOT / "evaluation/dataset.json"
    cases = [c for c in json.loads(cases_path.read_text(encoding="utf-8")) if c["split"] == split]
    config = read_config().model_copy(update={"top_k": top_k, "prompt_version": prompt})
    # Se fija recuperación léxica para comparar experimentos en condiciones constantes.
    retriever = Retriever(config)
    generator = DemoGenerator() if provider == "demo" else OllamaGenerator()
    if baseline:
        # Ablación sin contexto: la misma generación, sin gate del agente.
        rows = []
        for case in cases:
            try:
                decision, _ = generator.generate(case["text"], [], prompt)
                rows.append({"id": case["id"], "decision": decision.model_dump(), "expected": case["category"]})
            except Exception:
                rows.append({"id": case["id"], "error": "No se obtuvo salida válida", "expected": case["category"]})
        return {"provider": provider, "experiment": "sin_contexto", "rows": rows,
                "note": "Revisar calidad semántica manualmente; no comparable por citas disponibles."}
    agent = Agent(retriever, generator)
    rows = []
    for case in cases:
        if provider == "ollama":
            print(f"Evaluando {case['id']} ({len(rows)+1}/{len(cases)})", flush=True)
        result = agent.run(Ticket(text=case["text"], **case.get("input", {})))
        # Precision y recall se calculan por documento: varios fragmentos del mismo documento cuentan una vez.
        retrieved = {h["doc_id"] for h in result["sources"]}
        gold = set(case["relevant_docs"])
        intersection = len(retrieved & gold)
        # MRR usa la posición del primer fragmento relevante dentro del ranking recuperado.
        ranks = [i + 1 for i, h in enumerate(result["sources"]) if h["doc_id"] in gold]
        rows.append({"id": case["id"], "expected_category": case["category"],
                     "expected_priority": case["priority"], "expected_abstention": not gold,
                     "precision": intersection / len(retrieved) if retrieved else 0.,
                     "recall": intersection / len(gold) if gold else None,
                     "reciprocal_rank": 1 / min(ranks) if ranks else 0., "result": result})
    expected = [r["expected_category"] for r in rows]
    predicted = [r["result"]["decision"]["category"] for r in rows]
    labels = sorted(set(expected + predicted))
    # Las métricas de recuperación promedian casos con documentos relevantes etiquetados.
    supported = [r for r in rows if r["recall"] is not None]
    # La integridad de citas se mide entre borradores que pasaron el validador del agente.
    drafts = [r for r in rows if r["result"]["status"] == "draft"]
    report = {"created_at": datetime.now(timezone.utc).isoformat(), "provider": provider,
              "model": generator.model, "retriever": "lexical", "split": split, "n": len(rows),
              "dataset_sha256": hashlib.sha256(cases_path.read_bytes()).hexdigest(),
              "corpus_sha256": retriever.fingerprint, "config": config.model_dump(),
              "metrics": {
                  "category_accuracy": accuracy_score(expected, predicted),
                  "category_macro_f1": f1_score(expected, predicted, average="macro", zero_division=0),
                  "priority_accuracy": sum(r["expected_priority"] == r["result"]["priority"] for r in rows) / len(rows),
                  "context_precision_doc_level": float(np.mean([r["precision"] for r in supported])),
                  "context_recall_doc_level": float(np.mean([r["recall"] for r in supported])),
                  "mrr": float(np.mean([r["reciprocal_rank"] for r in supported])),
                  "abstention_accuracy": sum(r["expected_abstention"] == (r["result"]["status"] == "insufficient_context") for r in rows) / len(rows),
                  "valid_citation_draft_rate": len([r for r in drafts if r["result"]["decision"]["citations"]]) / len(drafts) if drafts else None,
                  "latency_p50_ms": float(np.percentile([r["result"]["timings"]["total_ms"] for r in rows], 50)),
                  "latency_p95_ms": float(np.percentile([r["result"]["timings"]["total_ms"] for r in rows], 95)),
                  "faithfulness_human": None, "answer_relevancy_human": None,
              }, "confusion_matrix": {"labels": labels, "values": confusion_matrix(expected, predicted, labels=labels).tolist()},
              "limitations": "Dataset sintético pequeño, etiquetas iniciales del implementador sin validación independiente. El simulador no mide un LLM. Citas válidas no prueban fidelidad semántica.",
              "rows": rows}
    return report


# Entrada CLI: selecciona condiciones, guarda evidencia y falla si el proveedor real no completó la ejecución.
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", choices=["demo", "ollama"], default="demo")
    parser.add_argument("--split", choices=["dev", "test"], default="test")
    parser.add_argument("--top-k", type=int, choices=range(1, 9), default=4)
    parser.add_argument("--prompt", choices=["v1", "v2", "v3"], default="v3")
    parser.add_argument("--baseline", action="store_true")
    args = parser.parse_args()
    report = evaluate(args.provider, args.split, args.top_k, args.prompt, args.baseline)
    suffix = "baseline" if args.baseline else args.split
    path = ROOT / f"reports/evaluation_{args.provider}_{suffix}_{args.prompt}_k{args.top_k}.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(path)
    print(json.dumps(report.get("metrics", {}), ensure_ascii=False, indent=2))
    if args.provider == "ollama" and any(r.get("result", {}).get("status") == "provider_error" or "error" in r for r in report["rows"]):
        raise SystemExit("Evaluación LLM incompleta: revisar Ollama. No reportar como éxito.")
