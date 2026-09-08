"""Comprueba integridad del ZIP y arranque desde una extracción aislada.

Reutiliza las dependencias del intérprete actual; no afirma simular un SO nuevo.
"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import zipfile
from catia.config import ROOT

if __name__=="__main__":
    runtime=ROOT/"runtime"
    runtime.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="package-check-",dir=runtime) as temporary:
        from pathlib import Path
        target=Path(temporary).resolve()
        if not target.is_relative_to(runtime.resolve()):
            raise ValueError("Directorio temporal fuera del espacio de trabajo")
        # Comprueba CRC y rutas antes de extraer en un directorio temporal del proyecto.
        with zipfile.ZipFile(ROOT/"dist/CAT-IA_entrega.zip") as archive:
            assert archive.testzip() is None
            for name in archive.namelist():
                if not (target/name).resolve().is_relative_to(target):
                    raise ValueError("Ruta ZIP fuera del destino")
                assert ".env" not in Path(name).parts and ".tools" not in Path(name).parts
            archive.extractall(target)
        project=target/"CAT-IA"
        manifest=json.loads((project/"MANIFEST_ENTREGA.json").read_text(encoding="utf-8"))
        for name,digest in manifest.items():
            assert hashlib.sha256((project/name).read_bytes()).hexdigest()==digest,name
        # El arranque aislado usa el simulador y las dependencias ya instaladas, sin descargar modelos.
        env={**os.environ,"CATIA_PROVIDER":"demo","CATIA_RETRIEVER":"lexical"}
        code="from catia.api import create_agent; from catia.schemas import Ticket; a=create_agent(); r=a.run(Ticket(text='Mi factura presenta un cobro duplicado')); assert r['status']=='draft'; assert r['decision']['category']=='Facturación'; print('Arranque y análisis correctos desde ZIP')"
        done=subprocess.run([sys.executable,"-X","utf8","-c",code],cwd=project,env=env,capture_output=True,text=True,encoding="utf-8",check=True)
        report={"zip_integrity":True,"hashes_verified":len(manifest),"isolated_source_startup":True,
                "zip_sha256":hashlib.sha256((ROOT/"dist/CAT-IA_entrega.zip").read_bytes()).hexdigest(),
                "environment":"Dependencias del entorno actual; fuentes extraídas del ZIP","output":done.stdout.strip()}
    # El informe describe el ZIP recién verificado y se guarda fuera de ese mismo ZIP.
    (ROOT/"reports/package_check.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    (ROOT/"dist/package_check.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False))
