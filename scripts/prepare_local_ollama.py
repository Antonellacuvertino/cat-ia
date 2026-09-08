"""Descarga selectiva de ejecutable y bibliotecas CPU del ZIP oficial.

Utilidad de preparación, no dependencia de la app. Usa HTTP Range para evitar
descargar bibliotecas GPU de varios GB. zipfile comprueba CRC al extraer.
"""
import io
import json
import zipfile
import httpx
from catia.config import ROOT


class RemoteZip(io.RawIOBase):
    """Expone un ZIP remoto como archivo posicionable para descargar solo las entradas necesarias."""
    def __init__(self, client, url, size):
        """Guarda el cliente HTTP, la URL, el tamaño remoto y el cursor de lectura."""
        self.client, self.url, self.size, self.pos = client, url, size, 0
    def seekable(self):
        """Indica a zipfile que el adaptador permite cambiar la posición de lectura."""
        return True
    def seek(self, offset, whence=0):
        """Actualiza el cursor respecto del inicio, posición actual o final sin descargar datos."""
        self.pos = offset if whence == 0 else self.pos + offset if whence == 1 else self.size + offset
        return self.pos
    def tell(self):
        """Devuelve el desplazamiento actual que zipfile necesita para localizar sus entradas."""
        return self.pos
    def read(self, count=-1):
        """Descarga el rango pedido, exige respuesta parcial 206 y avanza el cursor."""
        count = self.size - self.pos if count < 0 else min(count, self.size - self.pos)
        if count <= 0:
            return b""
        r = self.client.get(self.url, headers={"Range": f"bytes={self.pos}-{self.pos + count - 1}"})
        if r.status_code != 206 or len(r.content) != count:
            raise RuntimeError(f"El servidor no respetó Range: {r.status_code}")
        self.pos += count
        return r.content


if __name__ == "__main__":
    with httpx.Client(follow_redirects=True, timeout=180) as client:
        # Utilidad de preparación fijada a una versión; no debe ejecutarse durante la defensa.
        release = client.get("https://api.github.com/repos/ollama/ollama/releases/tags/v0.33.3")
        release.raise_for_status()
        asset = next(a for a in release.json()["assets"] if a["name"] == "ollama-windows-amd64.zip")
        with zipfile.ZipFile(RemoteZip(client, asset["browser_download_url"], asset["size"])) as archive:
            entries = [i for i in archive.infolist() if not i.is_dir() and
                       not any(x in i.filename.lower() for x in ["cuda", "rocm", "vulkan", "mlx"]) ]
            target = (ROOT / ".tools/ollama").resolve()
            target.mkdir(parents=True, exist_ok=True)
            print("Archivos CPU:", [(i.filename, i.compress_size) for i in entries], flush=True)
            for info in entries:
                path = (target / info.filename).resolve()
                if not path.is_relative_to(target):
                    raise ValueError("Ruta ZIP inválida")
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(archive.read(info))
                print("Preparado", info.filename, flush=True)
            (target / "source.json").write_text(json.dumps({"url": asset["browser_download_url"], "release": "v0.33.3", "selection": "CPU"}), encoding="utf-8")
