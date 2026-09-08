"""Smoke test de interfaz con Edge/CDP. Requiere websocket-client.

Iniciar Edge headless con puerto de depuración 9223 y perfil temporal antes.
No se usa para inferencia; prueba los flujos del modo activo de la aplicación.
"""
import base64
import json
import time
import urllib.request
from pathlib import Path
import websocket

ROOT=Path(__file__).resolve().parent.parent
pages=json.load(urllib.request.urlopen("http://127.0.0.1:9223/json"))
page=next(p for p in pages if p.get("type")=="page" and "127.0.0.1:8000" in p.get("url",""))
ws=websocket.create_connection(page["webSocketDebuggerUrl"],origin="http://localhost:9223",timeout=150)
seq=0


def call(method,params=None):
    """Envía un comando CDP y espera la respuesta con su identificador, ignorando otros eventos."""
    global seq
    seq+=1
    ws.send(json.dumps({"id":seq,"method":method,"params":params or {}}))
    while True:
        reply=json.loads(ws.recv())
        if reply.get("id")==seq:
            if "error" in reply:raise RuntimeError(reply["error"])
            return reply.get("result",{})


def js(expression):
    """Ejecuta una expresión en el navegador de prueba y propaga sus errores."""
    r=call("Runtime.evaluate",{"expression":expression,"awaitPromise":True,"returnByValue":True})
    if "exceptionDetails" in r:raise RuntimeError(r["exceptionDetails"])
    return r.get("result",{}).get("value")


def submit(example):
    """Selecciona un ejemplo, envía el formulario y espera el resultado antes de inspeccionarlo."""
    js(f"document.querySelector('[data-example={example}]').click(); document.getElementById('ticket-form').requestSubmit();")
    js("new Promise((resolve,reject)=>{let n=0;const t=setInterval(()=>{if(!document.getElementById('submit').disabled){clearInterval(t);resolve(true);}else if(++n>1400){clearInterval(t);reject(Error('timeout'));}},100);})")
    return js("({category:document.getElementById('category').textContent,status:latest.status,mode:latest.mode,priority:latest.priority,sources:latest.sources.map(x=>x.source_type)})")


if __name__=="__main__":
    results={"browser":"Microsoft Edge headless / CDP","checks":[]}
    call("Emulation.setDeviceMetricsOverride",{"width":1440,"height":1250,"deviceScaleFactor":1,"mobile":False})
    r=submit("firefox")
    assert r["status"]=="draft" and set(r["sources"])=={"internal","external"},r
    results["mode"]=r["mode"];results["checks"].append("Firefox: borrador y ambas fuentes")
    screenshot=call("Page.captureScreenshot",{"format":"png","captureBeyondViewport":False})
    (ROOT/"reports/interfaz_resultado.png").write_bytes(base64.b64decode(screenshot["data"]))
    r=submit("billing");assert r["category"]=="Facturación",r
    results["checks"].append("Facturación: categoría y resultado renderizados")
    r=submit("unknown");assert r["status"]=="insufficient_context",r
    results["checks"].append("Sin evidencia: abstención visible")
    call("Emulation.setDeviceMetricsOverride",{"width":390,"height":844,"deviceScaleFactor":1,"mobile":True})
    js("window.scrollTo(0,0)")
    assert js("document.documentElement.scrollWidth <= window.innerWidth"),"Desbordamiento móvil"
    screenshot=call("Page.captureScreenshot",{"format":"png","captureBeyondViewport":False})
    (ROOT/"reports/interfaz_movil.png").write_bytes(base64.b64decode(screenshot["data"]))
    results["checks"].append("Viewport 390 px: sin desbordamiento horizontal")
    results["passed"]=True
    (ROOT/"reports/browser_checks.json").write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding="utf-8")
    ws.close();print(json.dumps(results,ensure_ascii=False))
