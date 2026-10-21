"""Prueba la UI revisada con servidor demo y Edge/CDP; no mide calidad del LLM."""
import base64
import json
from datetime import datetime, timezone
from scripts.check_browser import ROOT, call, js, submit, ws
from scripts.check_browser_ea2 import wait_result


if __name__ == '__main__':
    report = {'created_at': datetime.now(timezone.utc).isoformat(), 'provider': 'demo', 'checks': []}
    call('Page.reload', {'ignoreCache': True})
    js('new Promise(r=>setTimeout(r,1500))')
    call('Emulation.setDeviceMetricsOverride', {'width':1440,'height':1250,'deviceScaleFactor':1,'mobile':False})
    first = submit('billing')
    assert first['status']=='draft' and first['mode']=='demo'
    assert js("latest.tool_events.at(-1).observation.saved_draft_id!==null")
    js("document.getElementById('use-context').checked=true;document.getElementById('ticket').value='no me conecta la VPN';document.getElementById('ticket-form').requestSubmit()")
    wait_result()
    assert js("latest.context_control.topic_change && !latest.memory.used && document.getElementById('execution-mode').textContent.includes('Cambio de tema')")
    assert js("latest.decision.category!=='Facturación'")
    report['checks'].append('Cambio de factura a VPN: aviso visible y antecedentes excluidos')
    shot=call('Page.captureScreenshot',{'format':'png','captureBeyondViewport':False})
    (ROOT/'reports/interfaz_feedback.png').write_bytes(base64.b64decode(shot['data']))
    js("document.getElementById('filter').value='external';document.getElementById('use-context').checked=false;document.getElementById('ticket').value='me cobraron dos veces';document.getElementById('ticket-form').requestSubmit()")
    wait_result()
    assert js("latest.status==='insufficient_context' && latest.sources.length===0")
    report['checks'].append('Solo externas + cobro: abstención visible y sin fuentes ajenas')
    call('Emulation.setDeviceMetricsOverride',{'width':390,'height':844,'deviceScaleFactor':1,'mobile':True})
    assert js('document.documentElement.scrollWidth<=window.innerWidth')
    report['checks'].append('Vista móvil sin desbordamiento')
    sid=js('sessionId')
    js("document.getElementById('clear-session').click();new Promise(r=>setTimeout(r,500))")
    assert js(f"fetch('/api/sessions/{sid}').then(r=>r.status)")==404
    report['checks'].append('Borrado de sesión desde la interfaz')
    report['passed']=True
    (ROOT/'reports/browser_feedback.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    ws.close(); print(json.dumps(report,ensure_ascii=False))
