// Interfaz del navegador: recoge entradas y muestra los resultados calculados por la API.
const $ = id => document.getElementById(id);
// Conserva la última respuesta en memoria para la descarga solicitada por el usuario.
let latest = null;
// Solo se conserva el identificador local: el contenido de memoria está en SQLite.
let sessionId = localStorage.getItem('catia-session-id');
let busy = false;

async function loadMemory(){
  if(!sessionId){$('session-label').textContent='Nueva conversación';return;}
  const response=await fetch('/api/sessions/'+sessionId);
  if(response.status===404){sessionId=null;localStorage.removeItem('catia-session-id');$('session-label').textContent='Nueva conversación';return;}
  if(!response.ok)throw Error('No se pudo leer la memoria local.');
  const data=await response.json();
  $('session-label').textContent='Hilo '+sessionId.slice(0,8)+' · '+data.turn_count+' intercambios';
  $('memory-summary').textContent=data.summary || 'Aún no hay intercambios antiguos para resumir.';
  $('history').replaceChildren(...data.turns.map(t=>{const row=el('li');row.append(el('strong','Operador: '),el('span',t.user),el('p','Borrador anterior ('+t.status+'): '+t.assistant));return row;}));
}

// Borrar es explícito: elimina el hilo de SQLite y el identificador guardado en el navegador.
$('clear-session').addEventListener('click',async()=>{
  if(busy)return;
  try{
    if(sessionId){const r=await fetch('/api/sessions/'+sessionId,{method:'DELETE'});if(!r.ok&&r.status!==404)throw Error('No se pudo borrar el hilo.');}
    sessionId=null;latest=null;localStorage.removeItem('catia-session-id');
    $('history').replaceChildren();$('memory-summary').textContent='Sin memoria anterior.';
    $('result').hidden=true;$('empty').hidden=false;$('evidence-section').hidden=true;
    $('ticket').value='';$('ticket').dispatchEvent(new Event('input'));await loadMemory();
  }catch(e){$('error').textContent=e.message;}
});
// Casos ficticios para mostrar recuperación, clasificación y ausencia de evidencia.
const examples = {
  firefox: 'El portal no inicia sesión en Firefox, pero funciona en otro navegador. ¿Cómo reviso las cookies y los datos del sitio?',
  billing: 'En mi factura aparecen dos cobros del mismo servicio. Necesito revisar el cargo duplicado.',
  unknown: '¿Cuál es la distancia exacta entre Júpiter y Neptuno en este instante?'
};
// Crea nodos con textContent: el texto del modelo se muestra como texto y no como HTML ejecutable.
const el = (tag, text, cls) => {const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;};
// Actualiza el contador al escribir; la validación definitiva también existe en el servidor.
$('ticket').addEventListener('input',()=>{$('count').textContent=`${$('ticket').value.length} / 4000`;});
// Cada botón de ejemplo rellena el textarea y actualiza su contador sin enviar todavía el ticket.
document.querySelectorAll('[data-example]').forEach(b=>b.addEventListener('click',()=>{$('ticket').value=examples[b.dataset.example];$('use-context').checked=false;$('ticket').dispatchEvent(new Event('input'));}));
// Consulta configuración y manifiesto al cargar la página; health no prueba una inferencia LLM.
async function init(){
  try {
    const response=await fetch('/api/health');if(!response.ok)throw Error();const h=await response.json();
    $('status').textContent=h.provider==='demo'?'● Simulación activa':'● LLM local configurado';
    $('doc-count').textContent=String(h.documents).padStart(2,'0');
    $('retrieval-label').textContent=h.retriever==='hybrid'?'Híbrida':'TF-IDF';
    $('orchestration').value=h.orchestration==='crew'?'crew':'react';
    $('orchestration').querySelector('[value="crew"]').disabled=!h.crew_available;
    if(!h.crew_available)$('crew-install').textContent='Para habilitar el equipo, ejecuta instalar_ea2.bat.';
    await loadMemory();
    // Distingue claramente un LLM configurado del simulador que funciona por reglas.
    $('mode-banner').textContent=h.provider==='demo'?'MODO DEMOSTRACIÓN · Clasificación por reglas y extractos. Este modo no utiliza un LLM ni demuestra su calidad.':'MODO LLM · '+h.model+' · Revisa las citas antes de utilizar cualquier respuesta.';
    const data=await (await fetch('/api/sources')).json();
    // Construye el catálogo con título, versión y procedencia de cada documento.
    for(const s of data.sources){const row=el('div',undefined,'source-row');const info=el('div');info.append(el('div',s.title),el('small',s.id+' · '+s.version));row.append(info,el('span',s.type==='internal'?'INTERNA · SIMULADA':'EXTERNA · MOZILLA'));$('source-list').append(row);}
  }catch{$('status').textContent='Sin conexión';$('error').textContent='No se pudo conectar con el servidor. Inícialo y recarga la página.';}
}
// Intercepta el envío para usar JSON sin recargar la página y bloquear solicitudes duplicadas.
$('ticket-form').addEventListener('submit',async event=>{
  event.preventDefault();if(busy)return;busy=true;$('clear-session').disabled=true;$('submit').disabled=true;$('submit').textContent='Consultando documentos…';$('error').textContent='';
  try{
    // Los nombres de las propiedades coinciden con Ticket en catia/schemas.py.
    const r=await fetch('/api/tickets/analyze',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text:$('ticket').value,impact:$('impact').value,service_down:$('down').checked,security_incident:$('security').checked,top_k:Number($('top-k').value),source_filter:$('filter').value,session_id:sessionId,orchestration:$('orchestration').value,use_context:$('use-context').checked,allow_demo_fallback:$('fallback').checked})});
    if(!r.ok)throw Error('La solicitud no pudo procesarse ('+r.status+'). Revisa los datos o la conexión del servidor.');
    // Solo una respuesta HTTP válida se guarda y pasa a render(); finally rehabilita el botón.
    latest=await r.json();sessionId=latest.session_id;localStorage.setItem('catia-session-id',sessionId);render(latest);await loadMemory();
  }catch(e){$('error').textContent=e.message;}finally{busy=false;$('clear-session').disabled=false;$('submit').disabled=false;$('submit').textContent='Analizar con evidencia ↗';}
});
// Pinta la decisión y la evidencia del servidor; aquí no se calcula la categoría ni el SLA.
function render(r){
  const d=r.decision;$('empty').hidden=true;$('result').hidden=false;$('evidence-section').hidden=false;
  $('category').textContent=d.category;$('priority').textContent='Prioridad '+r.priority;$('summary').textContent=d.summary;
  $('result-time').textContent=r.timings.total_ms+' ms';$('sla').textContent=`Primera respuesta: ${r.first_response_hours} horas hábiles · No es plazo de resolución.`;
  $('reply').textContent=d.suggested_reply;$('justification').textContent=d.justification;
  // Explica si existe un borrador o una abstención; la decisión final siempre corresponde al operador.
  $('review-note').textContent=r.status==='draft'?'Borrador pendiente de revisión. Comprueba alcance, citas e impacto antes de responder.':'El sistema se abstuvo ('+r.status+'). Requiere intervención de un operador.';
  $('trace').textContent='Traza '+r.trace_id+' · '+r.model+' · prompt '+r.prompt_version;
  $('execution-mode').textContent='Ejecutado: '+r.orchestration.executed+' · Contexto previo: '+(r.memory.used?'sí':'no');
  if(r.context_control?.topic_change)$('execution-mode').textContent+=' · Cambio de tema detectado: se ignoraron los antecedentes anteriores para esta consulta.';
  if(r.fallback_used){$('review-note').textContent='SIMULACIÓN DE RESPALDO: falló el proveedor real. Este borrador proviene de reglas y extractos, no del LLM.';}
  else if(r.warning){$('review-note').textContent=r.warning.message+' Estado: '+r.status;}
  $('tool-events').replaceChildren(...r.tool_events.map(e=>el('li',e.actor+' → '+e.tool+' · '+e.status+' · '+JSON.stringify(e.observation))));
  // Sustituye el recorrido anterior por los hitos de esta solicitud.
  $('steps').replaceChildren(...r.steps.map(s=>el('li',s.step+' — '+s.detail)));
  $('evidence').replaceChildren();
  // Relaciona citas con el ID del fragmento; muestra similitud, texto y huella de procedencia.
  for(const s of r.sources){const card=el('article',undefined,'evidence-card');card.append(el('small',`${s.source_type==='internal'?'INTERNA':'EXTERNA'} · Similitud ${s.score.toFixed(3)}`),el('h3',s.title),el('p',s.text));const cited=d.citations.filter(c=>c.source_id===s.id);for(const c of cited)card.append(el('blockquote',c.quote));card.append(el('small',s.id+' · SHA-256 '+s.sha256.slice(0,16)));if(s.origin.startsWith('https://')){const a=el('a','Consultar fuente original ↗');a.href=s.origin;a.target='_blank';a.rel='noopener noreferrer';card.append(el('p'),a);}$('evidence').append(card);}
  if(!r.sources.length)$('evidence').append(el('p','No hubo documentos por encima del umbral configurado.'));
}
// Descarga el resultado completo como JSON; revoca la URL temporal para liberar memoria.
$('download').addEventListener('click',()=>{if(!latest)return;const url=URL.createObjectURL(new Blob([JSON.stringify(latest,null,2)],{type:'application/json'}));const a=el('a');a.href=url;a.download='catia-'+latest.trace_id+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
// Arranque de la interfaz; el atributo defer del HTML asegura que el DOM ya esté disponible.
init();
