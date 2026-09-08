"""Ingesta y recuperación vectorial dispersa; embeddings densos opcionales.

El índice se reconstruye al arrancar: para este corpus pequeño evita almacenar
un índice obsoleto. SHA-256 y offsets conservan la procedencia de cada fragmento.
"""
import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import httpx
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from .config import RAGConfig, ROOT

STOP_WORDS = "a al algo ante como con cual cuando de del desde donde el ella en entre es esta este esto estos exacta ha hay la las lo los me mi muy no o para pero por que se si sin sobre son su sus tiene un una uno unos y yo cual instante".split()


@dataclass(frozen=True)
class Chunk:
    """Fragmento inmutable con documento de origen, versión, hash y posiciones de palabras."""
    id: str
    doc_id: str
    title: str
    source_type: str
    origin: str
    version: str
    sha256: str
    text: str
    word_start: int
    word_end: int


def load_chunks(config: RAGConfig, data_dir: Path | None = None):
    """Valida fuentes, divide sus textos con solapamiento y devuelve fragmentos y manifiesto."""
    base = data_dir or ROOT / "data"
    manifest = json.loads((base / "sources.json").read_text(encoding="utf-8"))
    chunks = []
    for source in manifest:
        if not source.get("active", True):
            continue
        # El manifiesto solo puede referenciar archivos del directorio documental.
        path = (base / source["file"]).resolve()
        if not path.is_relative_to(base.resolve()):
            raise ValueError("Una fuente no puede salir de data/")
        raw = path.read_bytes()
        # Comprobar bytes permite detectar cambios sin revisión editorial del manifiesto.
        sha = hashlib.sha256(raw).hexdigest()
        if source.get("sha256") and sha != source["sha256"]:
            raise ValueError(f"Hash distinto para {source['id']}; revisar y actualizar el manifiesto")
        words = raw.decode("utf-8").split()
        # Con 110 palabras y 20 de solapamiento, cada ventana avanza 90 palabras.
        step = config.chunk_words - config.overlap_words
        for start in range(0, len(words), step):
            stop = min(start + config.chunk_words, len(words))
            chunks.append(Chunk(
                id=f"{source['id']}:{start}", doc_id=source["id"],
                title=source["title"], source_type=source["type"], origin=source["origin"],
                version=source["version"], sha256=sha, text=" ".join(words[start:stop]),
                # Intervalo [start, stop): incluye inicio y excluye final.
                word_start=start, word_end=stop,
            ))
            if stop == len(words):
                break
    if not chunks:
        raise ValueError("No hay documentos activos")
    return chunks, manifest


class OllamaEmbeddings:
    """Adaptador opcional para obtener vectores densos desde un servidor Ollama."""
    def __init__(self, url: str, model: str):
        """Conserva la dirección del proveedor y el modelo de embeddings solicitado."""
        self.url, self.model = url.rstrip("/"), model

    def encode(self, texts):
        # No hay sustitución silenciosa de embeddings si falla el proveedor.
        """Convierte textos en vectores finitos de norma uno; rechaza respuestas mal formadas."""
        response = httpx.post(self.url + "/api/embed", json={"model": self.model, "input": texts}, timeout=120)
        response.raise_for_status()
        values = np.asarray(response.json()["embeddings"], dtype=float)
        if values.ndim != 2 or len(values) != len(texts) or not np.isfinite(values).all():
            raise ValueError("Embeddings inválidos")
        # Normalizar permite calcular coseno mediante producto escalar en search().
        norms = np.linalg.norm(values, axis=1, keepdims=True)
        if (norms == 0).any():
            raise ValueError("Embedding de norma cero")
        return values / norms


class Retriever:
    """Construye el índice en memoria y ordena documentos según su relación con la consulta."""
    def __init__(self, config: RAGConfig, data_dir=None, embeddings=None):
        """Indexa títulos y fragmentos con TF-IDF; añade embeddings solo si se inyectan."""
        self.config = config
        self.chunks, self.manifest = load_chunks(config, data_dir)
        # TF-IDF pondera términos y pares de términos; no requiere entrenar un LLM.
        self.vectorizer = TfidfVectorizer(strip_accents="unicode", lowercase=True,
                                        ngram_range=(1, 2), sublinear_tf=True, stop_words=STOP_WORDS)
        self.matrix = self.vectorizer.fit_transform([c.title + " " + c.text for c in self.chunks])
        self.embeddings = embeddings
        self.dense = embeddings.encode([c.text for c in self.chunks]) if embeddings else None
        self.mode = "hybrid" if embeddings else "lexical"
        # La traza identifica qué combinación de fragmentos y versiones se consultó.
        self.fingerprint = hashlib.sha256("".join(c.id + c.sha256 for c in self.chunks).encode()).hexdigest()

    def search(self, query: str, top_k=None, source_filter="all"):
        """Devuelve hasta k fragmentos que cumplan filtro, umbral y presupuesto de contexto."""
        # @ multiplica vectores normalizados: el resultado es similitud coseno léxica.
        lexical = (self.matrix @ self.vectorizer.transform([query]).T).toarray().ravel()
        semantic = np.zeros(len(self.chunks))
        if self.embeddings:
            semantic = np.maximum(0, self.dense @ self.embeddings.encode([query])[0])
        weight = self.config.semantic_weight if self.embeddings else 0
        # En lexical, weight=0: el modelo de embeddings no participa.
        scores = (1 - weight) * lexical + weight * semantic
        hits, used = [], 0
        # Orden descendente estable: conserva un desempate reproducible por posición.
        for idx in np.argsort(-scores, kind="stable"):
            chunk = self.chunks[int(idx)]
            if source_filter != "all" and chunk.source_type != source_filter:
                continue
            if scores[idx] <= 0 or scores[idx] < self.config.min_score:
                continue
            # Conserva fragmentos completos; este presupuesto es de caracteres, no tokens.
            if used + len(chunk.text) > self.config.max_context_chars:
                continue
            hits.append({**asdict(chunk), "score": round(float(scores[idx]), 6),
                         "lexical_score": round(float(lexical[idx]), 6),
                         "semantic_score": round(float(semantic[idx]), 6)})
            used += len(chunk.text)
            if len(hits) >= (top_k or self.config.top_k):
                break
        return hits
