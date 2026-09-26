# Mecánica del portal Reclama Virtual (referencia técnica compartida)

> Reclama Virtual es un servicio de INDECOPI. Este plugin no está afiliado ni respaldado por INDECOPI. La información de esta página se relevó del comportamiento observable del portal y puede cambiar.

Relevado el 23/09/2026 sobre https://enlinea.indecopi.gob.pe/reclamavirtual/ (Angular, rutas con `#`). Si algo no coincide con lo que se ve en pantalla, el portal cambió: detenerse, describir la diferencia al usuario y no improvisar.

## 1. Navegador y herramientas

- Usar el navegador disponible en la sesión: navegador integrado de Claude (`Claude_Browser__*`) o Claude in Chrome (`mcp__claude-in-chrome__*`). Ambos tienen `navigate`, `find`, `read_page`, `get_page_text`, `javascript_tool`, `form_input`, `computer`.
- Si el sitio pide permiso (`request_access`), solicitarlo para `https://enlinea.indecopi.gob.pe`.
- Llenar con `javascript_tool` usando los helpers de la sección 2 (más rápido y fiable que clics por coordenadas). El árbol de accesibilidad de este portal viene casi vacío; no depender de `read_page` para encontrar campos.
- Nunca provocar `alert()` del portal (bloquea el navegador): los provocan archivos inválidos, de más de 5,25 MB o con nombre repetido. Validar antes.
- Rutas: `#/` portada → `#/iniciar-reclamo` categorías → `#/motivo-del-reclamo` Etapa 1 → `#/identifica-empresa` Etapa 2 → `#/completa-datos` Etapa 3 → `#/resumen`. El estado vive en `sessionStorage` de la pestaña: no recargar ni abrir otra pestaña a mitad del llenado.

## 2. Helpers JS (inyectar una vez por carga de página)

Ejecutar con `javascript_tool` al llegar a `#/iniciar-reclamo` (y de nuevo si la página se recarga: comprobar `typeof window.RV`).

```js
window.RV = {
  w: ms => new Promise(r => setTimeout(r, ms)),
  q: s => document.querySelector(s),
  fc: n => document.querySelector(`[formcontrolname="${n}"]`),
  set(el, v) { if (typeof el === 'string') el = RV.q(el) || RV.fc(el);
    el.focus(); el.value = v; ['input','change'].forEach(t => el.dispatchEvent(new Event(t, {bubbles:true})));
    el.dispatchEvent(new Event('blur')); return el.value; },
  click(sel) { const el = typeof sel === 'string' ? RV.q(sel) : sel; el.click(); return !!el; },
  link(txt) { if (/enviar/i.test(txt)) return 'BLOQUEADO: el envío lo hace el usuario';
    const a = [...document.querySelectorAll('a,button')].find(e => !/enviar reclamo/i.test(e.innerText) && (e.innerText.trim().toLowerCase() === txt.toLowerCase() || e.innerText.includes(txt))); if (a) a.click(); return !!a; },
  siguiente() {                                 // avanza de etapa; nunca actúa en el resumen ni sobre ENVIAR
    if (location.hash.startsWith('#/resumen')) return 'BLOQUEADO: estás en el resumen; el envío lo hace el usuario';
    const b = [...document.querySelectorAll('form button[type=submit]')].filter(e => !/enviar/i.test(e.innerText)).pop();
    if (!b) return 'SIN_BOTON'; b.click(); return b.innerText.trim(); },
  errores() { return [...document.querySelectorAll('.invalid-feedback, [style*="dc3545"]')].map(e => e.innerText.trim()).filter(Boolean); },
  async fecha(ddmmaaaa) {                       // abre el calendario visible y elige el día
    const [d, m, y] = ddmmaaaa.split('/').map(Number);
    const MES = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'];
    RV.q('a[aria-label="Abrir selector de fecha"]').click(); await RV.w(500);
    const dp = RV.q('ngb-datepicker');
    const ys = dp.querySelector('select[aria-label="Select year"]'); ys.value = String(y); ys.dispatchEvent(new Event('change', {bubbles:true})); await RV.w(300);
    const ms = dp.querySelector('select[aria-label="Select month"]'); ms.value = String(m); ms.dispatchEvent(new Event('change', {bubbles:true})); await RV.w(300);
    const cell = dp.querySelector(`[aria-label="${y}-${MES[m-1]}-${d}"] > div`);
    if (!cell) { RV.q('a[aria-label="Abrir selector de fecha"]').click(); return 'DIA_NO_DISPONIBLE'; }
    cell.click(); await RV.w(400);
    return (RV.q('#fechaSuceso') || RV.q('#fecOcurrencia')).value;   // debe devolver DD/MM/AAAA
  },
  bloqueos() { const p = RV.q('#vcDescReclamoProcesado'), s = RV.q('#vcSolicitudProcesado');
    return { motivo: p ? p.innerText.trim() : '', solicitud: s ? s.innerText.trim() : '',
             textareaMotivo: !!RV.q('#motivoReclamo'), textareaSolicitud: !!RV.q('#textSolicitud') }; }
};
'RV listo'
```

Notas del calendario: es de solo lectura (escribir la fecha no funciona). Años disponibles desde 2016; no admite fechas futuras (`DIA_NO_DISPONIBLE`). Etiquetas de día: `AAAA-Mmm-D` con meses en español y día sin cero (p. ej. `2025-Mar-5`).

## 3. Portada y categoría

```js
location.hash = '#/'; await RV.w(1500);
RV.link('Siguiente'); await RV.w(1500);                 // lleva a #/iniciar-reclamo
if (!RV.q('#isReclamo').checked) RV.q('#isReclamo').click();   // "He leído los alcances del servicio" (obligatorio)
document.querySelectorAll('a.lnkSector')[INDICE].click(); await RV.w(2500);
location.hash   // debe ser '#/motivo-del-reclamo'
```
INDICE: 0 Servicios Bancarios y Financieros · 1 Transporte · 2 Colegios · 3 Otros · 4 Llamadas de publicidad no autorizadas. Verificar el título de la categoría en pantalla antes de seguir. Cambiar de categoría borra lo avanzado.

## 4. Etapa 1 — piezas comunes

| Acción | JS |
|---|---|
| Radio Sí/No "¿Expusiste…?" | `RV.click('#exponeReclamoSi')` / `#exponeReclamoNo` |
| Medio de reclamo (aparece tras "Sí") | `RV.set('nuReclamoMedioReclamo','4')` (1 Personal, 2 Telefónico, 3 Virtual, 4 Libro de reclamaciones, 5 Otros) |
| Otro medio (si 5) | `RV.set('vcOtroMedioReclamo','texto ≤150')` |
| Medio de compra | `RV.set('#realizarCompra','3')` (1 Presencial, 2 Telefónico, 3 Virtual, 4 No compré/ No contraté) |
| Motivo | `RV.set('#motivoReclamo', TEXTO)` y luego `RV.bloqueos()` |
| ¿Recuerdas la fecha? | `RV.click('#sucesoSi')` → `await RV.fecha('DD/MM/AAAA')` · `RV.click('#sucesoNo')` → `RV.set('#fechaAproxSuceso','texto ≤150')` |
| ¿Qué solicitas? | `RV.set('#textSolicitud', TEXTO)` y luego `RV.bloqueos()` |
| Oficina | `RV.set('#oficinaIndecopi', VALUE)` (valores en `catalogos.json > oficinas`) |
| Siguiente | `RV.siguiente(); await RV.w(1500); [location.hash, RV.errores()]` |

Textos largos: pasar el texto como literal JS con `JSON.stringify` del lado de Claude (comillas y saltos de línea escapados). Tras `RV.set`, comparar `RV.q('#motivoReclamo').value.length` con la longitud esperada.

### Filtro de palabras (bloquea la Etapa 1)
Al escribir o salir del campo, el portal busca frases de `palabras-bloqueadas.json`. Si encuentra alguna: oculta el textarea, resalta la palabra (amarillo = sanción/indemnización; verde = otra entidad) y **no deja avanzar**. Prevenirlo validando antes con `scripts/validar_ficha.py`. Si igual ocurre:
1. `RV.bloqueos()` muestra el texto procesado; identificar la palabra.
2. Reescribir la frase con el usuario (ver sinónimos en `requerimientos-informacion.md`).
3. Clic en el enlace "Modificar texto" → modal con `#motivoReclamoTemp` (o `#solicitudReclamoTemp`) → `RV.set` del texto corregido → clic en el botón "Modificar texto" del modal. Verificar que `#motivoReclamo` reapareció con el texto nuevo.

### Adjuntos (opcional, máx. 5, ≤ 5,25 MB c/u)
1. Elegir el tipo: `RV.set('#tipoDocumento', VALUE_TIPO)` (valores en `catalogos.json > tipos_documento_adjunto`). Recién entonces aparece `input#fileDocument`.
2. Subir el archivo:
   - **Claude in Chrome**: `find` "Cargar archivo" / `input#fileDocument` para obtener el `ref` y usar `file_upload` con la ruta local del archivo en el equipo del usuario.
   - **Navegador integrado** (no tiene `file_upload`): pedir al usuario que, con el panel del navegador visible, haga clic en "Cargar archivo" y elija el archivo indicado; esperar su aviso. No usar ningún otro método para subir archivos.
3. El archivo se envía a INDECOPI al seleccionarlo (antes del envío final). Verificar que aparece listado bajo su tipo y que `document.querySelectorAll('app-document-file').length` aumentó. Repetir tipo → archivo para cada adjunto; el tipo seleccionado agrupa lo que se sube después.
4. Nombres únicos por reclamo; sin emojis.

## 5. Etapa 2 — Identifica al reclamado (igual en todas las categorías)

```js
RV.link('Persona Jurídica'); await RV.w(800);           // o 'Persona Natural'
// Natural: RV.set('#nuReclamadoTipoDocumento-0','1')   // 1 DNI, 2 CE, 3 RUC
RV.set('#vcDocumento-0', 'RUC_O_DNI'); await RV.w(6000); // DNI/RUC consultan RENIEC/SUNAT solos
[RV.q('#vcNombreComercial-0')?.value, RV.q('#vcNombres-0')?.value, RV.q('#vcApePaterno-0')?.value, RV.q('#vcDireccion-0')?.value, RV.errores()]
```
- CE: tras escribirlo, hacer clic en el ícono de búsqueda (`a.lnkSendDocument`) o Enter.
- Si no autocompleta en 10 s, reintentar una vez con "Corregir número de documento" y volver a escribir. Si sigue sin datos, el portal muestra los campos para llenarlos a mano.
- Sin documento: `RV.click('#defaultCheck1')` ("No cuento con esa información") y llenar a mano nombre/razón social y dirección.
- Nombre y documento autocompletados quedan en solo lectura; la dirección es editable y obligatoria.
- Correo y teléfono del reclamado: opcionales (`#vcCorreo-0`, `#vcTelefono-0`). Dejarlos vacíos salvo dato verificado.
- **Cotejar** la razón social devuelta contra el proveedor de la ficha. Si no coincide, detenerse y consultar.
- "Agregar otra persona reclamada" permite más de un reclamado (p. ej. tienda y fabricante).
- Siguiente: `RV.siguiente()`.

## 6. Etapa 3 — Completa tus datos (se omite si Colegios + anónimo)

```js
RV.link('Persona Natural'); await RV.w(800);
RV.set('#nuReclamanteTipoDocumento-0','1');              // 1 DNI, 2 CE, 3 RUC, 4 Pasaporte
RV.set('#vcDocumento-0','DNI'); await RV.w(6000);        // autocompleta apellidos, nombres y dirección (RENIEC)
[RV.q('#vcApePaterno-0')?.value, RV.q('#vcApeMaterno-0')?.value, RV.q('#vcNombres-0')?.value, RV.q('#nuDireccionDNI')?.checked, RV.errores()]
RV.set('#vcCorreo-0','correo'); RV.set('#vcTelefono-0','telefono');
// Discapacidad: campo opcional. Marcarlo SOLO si el usuario lo indicó en la ficha (no asumir "No"):
// no → RV.click('#nuDiscapacidadNo'); sí → #chkTipoDiscapacidadVisual|Auditiva|Motora|Cognitiva
```
- "Mantengo la dirección de mi documento" (`#nuDireccionDNI`) viene marcado si RENIEC devuelve dirección; si el usuario quiere otra, desmarcarlo y llenar `RV.set('vcDireccion', '...')` (máx. 200).
- Correo y teléfono son obligatorios para persona natural. El correo recibe las notificaciones del reclamo.
- Persona jurídica: RUC (`#vcDocumento-0`) → razón social; luego representante: tipo (`nuReclamanteTipoDocumentoRpte`), `#vcDocumentoRepresentante`, dirección (`#nuDireccionRepresentanteDNI` o `vcDireccionRepresentante`), `vcCorreoRepresentante`, `#vcTelefonoRepresentante`.
- Apellido materno obligatorio con DNI; opcional con CE/Pasaporte.
- Siguiente → `#/resumen`.

## 7. Resumen y entrega al usuario (el envío lo hace el usuario)

El plugin **no hace clic en "ENVIAR RECLAMO"**. Llena el formulario, verifica el resumen y deja la pantalla lista para que el usuario lo envíe.

1. `get_page_text` en `#/resumen` y cotejar campo por campo contra la ficha: categoría, respuestas Sí/No, producto/medios, motivo completo (sin escapes), adjuntos y su tipo, fecha, solicitud, oficina, reclamado (documento, razón social, dirección), reclamante (nombre, documento, correo, teléfono).
2. Corregir las discrepancias con los enlaces "Editar" de cada bloque (llevan a la etapa con el botón "Continuar"/"Actualizar") y volver al resumen.
3. Mostrar al usuario, en el chat, el **texto literal** del MOTIVO y de la SOLICITUD tal como quedaron en el resumen del portal (pueden haber cambiado al pasar el filtro de palabras), más los datos del reclamado, la oficina, los adjuntos y lo que se asumió.
4. Pedirle que revise la pantalla y, si está conforme, haga él mismo clic en **ENVIAR RECLAMO**. Si el portal muestra algún desafío de verificación (captcha), lo resuelve el usuario; el plugin no interactúa con mecanismos de verificación ni intenta evitarlos.
5. Cuando el usuario avise que envió: leer la pantalla (`get_page_text`) para registrar el modal "¡REGISTRO EXITOSO!" y el ID del reclamo. Si aparece "Su reclamo ya ha sido registrado anteriormente", no reintentar.
6. "Descargar archivo" (PDF del cargo) es una descarga: la hace el usuario o se hace solo con su permiso. INDECOPI también envía el cargo al correo del reclamante.
7. Registrar el resultado en la carpeta del caso según `paso-2-reclama-virtual` §6.
