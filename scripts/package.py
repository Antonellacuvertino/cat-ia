"""Empaqueta solo los archivos redistribuibles y evita secretos/modelos/cachés."""
import hashlib
import json
import zipfile
from catia.config import ROOT

# Lista permitida: excluye por construcción modelos, entorno virtual y trazas locales.
ALLOWED_DIRS = {"catia", "config", "data", "docs", "evaluation", "prompts", "reports", "scripts", "tests", "web", "deliverables"}
ALLOWED_FILES = {"README.md", "requirements.txt", "requirements-browser.txt", "pyproject.toml", ".gitignore", ".env.example", "iniciar.bat", "iniciar_modelo_local.bat", "instalar.bat", "verificar.bat"}

if __name__ == "__main__":
    destination=ROOT/"dist"
    destination.mkdir(exist_ok=True)
    files=[p for p in ROOT.rglob("*") if p.is_file() and
           (p.relative_to(ROOT).parts[0] in ALLOWED_DIRS or p.relative_to(ROOT).as_posix() in ALLOWED_FILES) and
           not any(part in {"__pycache__", ".pytest_cache"} for part in p.relative_to(ROOT).parts) and p.suffix != ".pyc" and p.name != "package_check.json"]
    with zipfile.ZipFile(destination/"CAT-IA_entrega.zip","w",zipfile.ZIP_DEFLATED) as archive:
        # Cada archivo recibe un SHA-256 para comprobar que el paquete conserva los bytes entregados.
        manifest={}
        for file in sorted(files):
            rel=file.relative_to(ROOT).as_posix();archive.write(file, "CAT-IA/"+rel)
            manifest[rel]=hashlib.sha256(file.read_bytes()).hexdigest()
        archive.writestr("CAT-IA/MANIFEST_ENTREGA.json",json.dumps(manifest,indent=2))
    print(destination/"CAT-IA_entrega.zip", len(files), "archivos")
