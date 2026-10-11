"""API local de demostración y frontend; /docs expone el contrato OpenAPI."""
import os
import importlib.util
from pathlib import Path
from uuid import UUID
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .agent import ConversationAgent
from .memory import MemoryStore
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
    memory = MemoryStore(Path(os.getenv("CATIA_MEMORY_DB", str(ROOT / "runtime/memory.sqlite3"))),
                         window=int(os.getenv("CATIA_MEMORY_WINDOW", "3")))
    return ConversationAgent(Retriever(read_config(), embeddings=embeddings), generator, memory,
                             ROOT / "runtime/traces", mode=os.getenv("CATIA_ORCHESTRATION", "react"))


def create_app(agent=None):
    """Construye la aplicación; acepta un agente de prueba para evitar servicios externos en tests."""
    @asynccontextmanager
    async def lifespan(app):
        """Crea un agente compartido al arrancar; el índice no se reconstruye para cada petición."""
        app.state.agent = agent or create_agent()
        yield

    app = FastAPI(title="CAT-IA · Mesa de soporte EA2", version="2.0.0", lifespan=lifespan)

    @app.middleware("http")
    async def local_boundary(request: Request, call_next):
        # Impide POST desde páginas ajenas. Este prototipo se sirve solo en loopback.
        """Filtra POST de otro origen y añade cabeceras del navegador; no implementa autenticación."""
        origin = request.headers.get("origin")
        if request.method in {"POST", "DELETE"} and origin and origin != str(request.base_url).rstrip("/"):
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
                "orchestration": getattr(active, "mode", "legacy"),
                "memory_enabled": hasattr(active, "memory"),
                "crew_available": importlib.util.find_spec("crewai") is not None,
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
        except KeyError as exc:
            raise HTTPException(404, "Sesión inexistente. Inicia una conversación nueva.") from exc
        except Exception as exc:
            raise HTTPException(503, "No se completó la operación. Revisar fuentes, memoria y proveedores.") from exc

    def session_store():
        """Obtiene la memoria de EA2 sin exigirla a agentes inyectados por pruebas anteriores."""
        if not hasattr(app.state.agent, "memory"):
            raise HTTPException(503, "La memoria EA2 no está habilitada")
        return app.state.agent.memory

    @app.post("/api/sessions", status_code=201)
    def new_session():
        """Inicia un hilo local; el UUID no es un mecanismo de autenticación empresarial."""
        return {"session_id": session_store().create()}

    @app.get("/api/sessions/{session_id}")
    def get_session(session_id: UUID):
        """Devuelve ventana y resumen persistidos para el operador de este equipo local."""
        try:
            return session_store().get(str(session_id))
        except KeyError as exc:
            raise HTTPException(404, "Sesión inexistente") from exc

    @app.delete("/api/sessions/{session_id}")
    def delete_session(session_id: UUID):
        """Borra memoria del hilo; no borra resultados descargados previamente."""
        if not session_store().delete(str(session_id)):
            raise HTTPException(404, "Sesión inexistente")
        return {"deleted": True}

    @app.get("/")
    def home():
        """Sirve el HTML inicial; JavaScript solicita después los datos a la API."""
        return FileResponse(ROOT / "web/index.html")

    # HTML referencia /assets/app.js y /assets/style.css, servidos desde la misma aplicación.
    app.mount("/assets", StaticFiles(directory=ROOT / "web"), name="assets")
    return app


# Punto de entrada que Uvicorn importa mediante catia.api:app.
app = create_app()
