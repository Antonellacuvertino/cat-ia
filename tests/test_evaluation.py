"""Pruebas del protocolo de evaluación y de la separación de los conjuntos de datos."""
from scripts.evaluate import evaluate


def test_evaluation_is_explicit_about_provider_and_semantic_limits():
    """Comprueba tamaño del conjunto, proveedor declarado y métricas humanas pendientes."""
    report = evaluate(provider="demo", split="test")
    assert report["n"] == 20
    assert report["provider"] == "demo"
    assert 0 <= report["metrics"]["category_macro_f1"] <= 1
    assert report["metrics"]["faithfulness_human"] is None
    assert report["metrics"]["answer_relevancy_human"] is None
    assert len(report["rows"]) == 20


def test_dataset_splits_do_not_overlap():
    """Comprueba identificadores únicos y ausencia de textos idénticos entre dev y test."""
    from catia.config import ROOT
    import json
    cases = json.loads((ROOT / "evaluation/dataset.json").read_text(encoding="utf-8"))
    assert len({c["id"] for c in cases}) == len(cases)
    dev = {c["text"] for c in cases if c["split"] == "dev"}
    test = {c["text"] for c in cases if c["split"] == "test"}
    assert not dev & test
