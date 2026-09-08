"""API local de demostración y frontend; /docs expone el contrato OpenAPI."""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .agent import Agent
from .config import ROOT, provider_name, read_config
from .generation import DemoGenerator, OllamaGenerator
from .retrieval import OllamaEmbeddings, Retriever
from .schemas import Ticket


def create_agent():
    """Conecta la configuración con el recuperador y el proveedor de generación elegidos."""
    mode = os.getenv("CATIA_RETRIEVER", "lexical")
    if mode not in {"lexical", "hybrid"}:
        raise ValueError("CATIA_RETRIEVER debe ser lexical o hybrid")
    embeddings = OllamaEmbeddings(os.getenv("OLLAMA_URL", "http://127.0.0.1:11434"),
                                  os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")) if mode == "hybrid" else None
    # La elección del proveedor es explícita y visible en /api/health y en la interfaz.
    generator = OllamaGenerator() if provider_name() == "ollama" else DemoGenerator()
    return Agent(Retriever(read_config(), embeddings=embeddings), generator, ROOT / "runtime/traces")


def create_app(agent=None):
    """Construye la aplicación; acepta un agente de prueba para evitar servicios externos en tests."""
    @asynccontextmanager
    async def lifespan(app):
        """Crea un agente compartido al arrancar; el índice no se reconstruye para cada petición."""
        app.state.agent = agent or create_agent()
        yield

    app = FastAPI(title="CAT-IA · Mesa de soporte", version="1.0.0", lifespan=lifespan)

    @app.middleware("http")
    async def local_boundary(request: Request, call_next):
        # Impide POST desde páginas ajenas. Este prototipo se sirve solo en loopback.
        """Filtra POST de otro origen y añade cabeceras del navegador; no implementa autenticación."""
        origin = request.headers.get("origin")
        if request.method == "POST" and origin and origin != str(request.base_url).rstrip("/"):
            from fastapi.responses import JSONResponse
            return JSONResponse({"detail": "Origen no permitido"}, status_code=403)
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Content-Security-Policy"] = "default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self' data:; frame-ancestors 'none'"
        if request.url.path in {"/docs", "/redoc"}:
            response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; font-src https://fonts.gstatic.com; img-src 'self' data: https://fastapi.tiangolo.com; frame-ancestors 'none'"
        return response

    @app.get("/api/health")
    def health():
        """Muestra la configuración cargada; no realiza una inferencia ni verifica que Ollama responda."""
        active = app.state.agent
        return {"status": "ok", "provider": active.generator.name, "model": active.generator.model,
                "retriever": active.retriever.mode, "documents": len(active.retriever.manifest),
                "chunks": len(active.retriever.chunks), "config": active.retriever.config.model_dump()}

    @app.get("/api/sources")
    def sources():
        """Publica el manifiesto de procedencia para que la interfaz muestre la base documental."""
        return {"sources": app.state.agent.retriever.manifest}

    # Pydantic rechaza un cuerpo inválido con HTTP 422 antes de ejecutar esta función.
    @app.post("/api/tickets/analyze")
    def analyze(ticket: Ticket):
        """Recibe un Ticket validado por FastAPI y ejecuta el flujo; errores no controlados devuelven 503."""
        try:
            return app.state.agent.run(ticket)
        except Exception as exc:
            raise HTTPException(503, "No se pudo consultar la base documental. Revisar el proveedor de embeddings.") from exc

    @app.get("/")
    def home():
        """Sirve el HTML inicial; JavaScript solicita después los datos a la API."""
        return FileResponse(ROOT / "web/index.html")

    # HTML referencia /assets/app.js y /assets/style.css, servidos desde la misma aplicación.
    app.mount("/assets", StaticFiles(directory=ROOT / "web"), name="assets")
    return app


# Punto de entrada que Uvicorn importa mediante catia.api:app.
app = create_app()
