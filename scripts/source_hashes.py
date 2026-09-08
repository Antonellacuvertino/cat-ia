"""Ejecutar solo después de revisar editorialmente un cambio de las fuentes."""
import hashlib
import json
from catia.config import ROOT

if __name__ == "__main__":
    file = ROOT / "data/sources.json"
    sources = json.loads(file.read_text(encoding="utf-8"))
    # Registra nuevos hashes tras revisión editorial; no usar para ocultar una modificación accidental.
    for source in sources:
        path = (ROOT / "data" / source["file"]).resolve()
        if not path.is_relative_to((ROOT / "data").resolve()):
            raise ValueError("Ruta de fuente no permitida")
        source["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    file.write_text(json.dumps(sources, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Registrados hashes de {len(sources)} fuentes revisadas")
