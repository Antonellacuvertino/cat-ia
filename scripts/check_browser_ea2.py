"""Comprueba EA2 en un navegador real; servidor demo y Edge/CDP en puerto 9223."""
import base64
import json
from datetime import datetime, timezone
from scripts.check_browser import ROOT, call, js, submit, ws


def wait_result():
    """Espera el fin del envío para comprobar el contrato renderizado."""
    js("new Promise((resolve,reject)=>{let n=0;const t=setInterval(()=>{if(!document.getElementById('submit').disabled){clearInterval(t);resolve(true);}else if(++n>1400){clearInterval(t);reject(Error('timeout'));}},100);})")


if __name__ == '__main__':
    report = {'created_at': datetime.now(timezone.utc).isoformat(), 'provider': 'demo', 'checks': []}
    call('Page.reload', {'ignoreCache': True})
    js("new Promise(r=>setTimeout(r,1800))")
    call('Emulation.setDeviceMetricsOverride', {'width': 1440, 'height': 1250, 'deviceScaleFactor': 1, 'mobile': False})
    r = submit('billing')
    assert r['mode'] == 'demo' and r['status'] == 'draft', r
    js("document.getElementById('use-context').checked=true;document.getElementById('ticket').value='¿Qué hago en ese caso?';document.getElementById('ticket-form').requestSubmit();")
    wait_result()
    assert js("latest.memory.used && latest.memory.previous_turns>=1 && latest.decision.category==='Facturación' && document.getElementById('history').children.length>=2")
    report['checks'].append('Continuación de facturación con antecedentes y memoria visible')
    js("document.getElementById('orchestration').value='crew'")
    r = submit('firefox')
    assert r['status'] == 'draft' and set(r['sources']) == {'internal', 'external'}, r
    assert js("latest.orchestration.executed==='crewai-sequential-demo' && document.getElementById('tool-events').children.length===3")
    report['checks'].append('CrewAI simulado: tres herramientas y fuentes internas/externas visibles')
    shot = call('Page.captureScreenshot', {'format': 'png', 'captureBeyondViewport': False})
    (ROOT/'reports/interfaz_ea2.png').write_bytes(base64.b64decode(shot['data']))
    call('Emulation.setDeviceMetricsOverride', {'width': 390, 'height': 844, 'deviceScaleFactor': 1, 'mobile': True})
    js('window.scrollTo(0,0)')
    assert js('document.documentElement.scrollWidth<=window.innerWidth'), 'Desbordamiento móvil'
    report['checks'].append('Pantalla móvil de 390 px sin desbordamiento horizontal')
    shot = call('Page.captureScreenshot', {'format': 'png', 'captureBeyondViewport': False})
    (ROOT/'reports/interfaz_movil_ea2.png').write_bytes(base64.b64decode(shot['data']))
    old = js('sessionId')
    js("document.getElementById('clear-session').click();new Promise(r=>setTimeout(r,600))")
    assert js("sessionId===null && document.getElementById('history').children.length===0")
    assert js(f"fetch('/api/sessions/{old}').then(r=>r.status)") == 404
    report['checks'].append('Borrado desde la interfaz: memoria vacía y sesión devuelve 404')
    report['passed'] = True
    (ROOT/'reports/browser_checks_ea2.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    ws.close(); print(json.dumps(report, ensure_ascii=False))
