# Formulario de Reclama Virtual por categoría (Etapa 1)

Referencia de `paso-2-formulario`. Las Etapas 2 y 3, el resumen y la entrega al usuario son comunes a todas las categorías: ver `portal-mecanica.md` §5–7. Relevado del comportamiento observable del portal el 23/09/2026; si la pantalla no coincide, detenerse y describir la diferencia.

| Categoría (`categoria:` en la ficha) | Opción del portal | INDICE (`portal-mecanica.md` §3) | Campos propios |
|---|---|---|---|
| `bancario` | Servicios Bancarios y Financieros | 0 | Producto financiero (O) y número de cuenta (Op) |
| `transporte` | Transporte | 1 | Ninguno; tipos de adjunto propios |
| `colegios` | Colegios | 2 | ¿Reclamo anónimo? (O); con Sí se omite la Etapa 3 |
| `otros` | Otros | 3 | Ninguno (categoría residual) |
| `llamadas` | Llamadas de publicidad no autorizadas | 4 | Formulario propio: sin motivo ni solicitud libres; registro de cada llamada |

## Servicios Bancarios y Financieros (`categoria: bancario`, INDICE = 0)

Campos en orden de pantalla (O = obligatorio, Op = opcional). Usar los helpers `RV.*`.

| # | Campo del portal | O/Op | Fuente en la ficha | Acción |
|---|---|---|---|---|
| 1 | ¿Expusiste tu problema ante el reclamado? | O | `expuso_al_proveedor` | `RV.click('#exponeReclamoSi')` o `#exponeReclamoNo` |
| 2 | Medio de reclamo (aparece si Sí) | O si Sí | `medio_reclamo` | `RV.set('nuReclamoMedioReclamo', v)` 1 Personal · 2 Telefónico · 3 Virtual · 4 Libro de reclamaciones · 5 Otros |
| 3 | Otro medio (si 5) | O si Otros | `medio_reclamo_otro` | `RV.set('vcOtroMedioReclamo', texto≤150)` |
| 4 | Identifica el producto financiero | O | `producto_financiero` | `RV.set('#productoFinanciero', v)` 1 Créditos comerciales · 2 Crédito de consumo · 3 Cuenta corriente · 4 Depósito de ahorros · 5 Depósito CTS · 6 Arrendamiento financiero · 7 Depósito a plazo · 8 Tarjeta de crédito · 9 Tarjeta de débito · 10 Crédito hipotecario · 11 Otros |
| 5 | Ingresa el número de cuenta | Op (≤30) | `numero_cuenta` | Solo si la ficha lo trae: `RV.set('#vcNumeroCuenta', digitos)`. Elegir el producto **antes** (cambiarlo borra el número). Solo dígitos salvo producto 11 |
| 6 | ¿Cómo realizaste la compra o la contratación del servicio? | O | `medio_compra` | `RV.set('#realizarCompra', v)` 1 Presencial · 2 Telefónico · 3 Virtual · 4 No compré/ No contraté |
| 7 | Explícanos el motivo del reclamo | O (≤4000) | `## MOTIVO` | `RV.set('#motivoReclamo', TEXTO)` → `RV.bloqueos()` debe devolver `motivo: ''` y `textareaMotivo: true` |
| 8 | Documentos (tipo + archivo) | Op (≤5, ≤5,25 MB) | `adjuntos` | Ver abajo |
| 9 | ¿Recuerdas cuándo sucedió el problema? | O | `recuerda_fecha` | `RV.click('#sucesoSi')` → `await RV.fecha('DD/MM/AAAA')` (debe devolver la fecha) · o `#sucesoNo` → `RV.set('#fechaAproxSuceso', texto≤150)` |
| 10 | ¿Qué solicitas? | O (≤3000) | `## SOLICITUD` | `RV.set('#textSolicitud', TEXTO)` → `RV.bloqueos()` debe devolver `solicitud: ''` |
| 11 | Oficina del Indecopi | O | `oficina` | `RV.set('#oficinaIndecopi', value)` (value en `catalogos.json > oficinas`) |

Detalles:
- Pasar los textos con `JSON.stringify` para escapar comillas y saltos de línea. Verificar después `RV.q('#motivoReclamo').value.length` = longitud del texto de la ficha.
- Si `RV.bloqueos()` muestra texto (palabra resaltada), aplicar el procedimiento "Filtro de palabras" de `portal-mecanica.md` §4 y actualizar también la ficha.
- Fecha: si hubo reclamo previo, la ficha trae normalmente la fecha de la respuesta del proveedor; usar exactamente `fecha_hecho`.
- **Adjuntos**: por cada línea de `adjuntos`, `RV.set('#tipoDocumento', value_del_tipo)` y subir el archivo según `portal-mecanica.md` §4 (Claude in Chrome: `file_upload`; navegador integrado: el usuario hace clic en "Cargar archivo"). Tipos válidos en esta categoría: Contrato (1) · Estado de cuenta (2) · Hoja resumen (3) · Factura (10) · Garantía (13) · Hoja de reclamación (11) · Hoja de servicio técnico (12) · Otros (14). Verificar que cada archivo quede listado bajo su tipo.

**En el resumen, cotejar además:**
   - Sector = "Servicios Bancarios y Financieros"
   - ¿Cuál es tu producto financiero? = producto: número de cuenta (o "-")
   - ¿Expusiste…? y medio; ¿Cómo realizaste la compra?
   - Motivo completo, sin escapes de Markdown ni cortes
   - Documentos adjuntos: nombre y tipo de cada uno
   - Fecha de suceso (exacta o aproximada) y ¿Qué solicitas? completo
   - Sede donde serás atendido = `oficina`

**Notas de la categoría:**
- Adjuntos típicos: hoja de reclamación y carta de respuesta del banco (tipo *Hoja de reclamación*), estados de cuenta (*Estado de cuenta*), contrato u hoja resumen si la controversia es sobre condiciones pactadas.
- El número de cuenta se traslada al proveedor; no incluir números completos de tarjeta. Si el usuario no lo pide, dejarlo vacío (el resumen mostrará "-").
- Evitar en la redacción: *se disponga, se ordene, reconocimiento, compensación, indemnización, investigar*; pedir "que el banco entregue/abone/corrija…".

## Transporte (`categoria: transporte`, INDICE = 1)

Campos en orden de pantalla (O = obligatorio, Op = opcional). Usar los helpers `RV.*`.

| # | Campo del portal | O/Op | Fuente en la ficha | Acción |
|---|---|---|---|---|
| 1 | ¿Expusiste tu problema ante el reclamado? | O | `expuso_al_proveedor` | `RV.click('#exponeReclamoSi')` o `#exponeReclamoNo` |
| 2 | Medio de reclamo (aparece si Sí) | O si Sí | `medio_reclamo` | `RV.set('nuReclamoMedioReclamo', v)` 1 Personal · 2 Telefónico · 3 Virtual · 4 Libro de reclamaciones · 5 Otros |
| 3 | Otro medio (si 5) | O si Otros | `medio_reclamo_otro` | `RV.set('vcOtroMedioReclamo', texto≤150)` |
| 4 | ¿Cómo realizaste la compra o la contratación del servicio? | O | `medio_compra` | `RV.set('#realizarCompra', v)` 1 Presencial · 2 Telefónico · 3 Virtual · 4 No compré/ No contraté |
| 5 | Explícanos el motivo del reclamo | O (≤4000) | `## MOTIVO` | `RV.set('#motivoReclamo', TEXTO)` → `RV.bloqueos()` debe devolver `motivo: ''` y `textareaMotivo: true` |
| 6 | Documentos (tipo + archivo) | Op (≤5, ≤5,25 MB) | `adjuntos` | Ver abajo |
| 7 | ¿Recuerdas cuándo sucedió el problema? | O | `recuerda_fecha` | `RV.click('#sucesoSi')` → `await RV.fecha('DD/MM/AAAA')` (debe devolver la fecha) · o `#sucesoNo` → `RV.set('#fechaAproxSuceso', texto≤150)` |
| 8 | ¿Qué solicitas? | O (≤3000) | `## SOLICITUD` | `RV.set('#textSolicitud', TEXTO)` → `RV.bloqueos()` debe devolver `solicitud: ''` |
| 9 | Oficina del Indecopi | O | `oficina` | `RV.set('#oficinaIndecopi', value)` (value en `catalogos.json > oficinas`) |

Detalles:
- Pasar los textos con `JSON.stringify` para escapar comillas y saltos de línea. Verificar después `RV.q('#motivoReclamo').value.length` = longitud del texto de la ficha.
- Si `RV.bloqueos()` muestra texto (palabra resaltada), aplicar el procedimiento "Filtro de palabras" de `portal-mecanica.md` §4 y actualizar también la ficha.
- Fecha: la del viaje o incidente (vuelo cancelado, pérdida de equipaje) o la de la respuesta del proveedor si hubo reclamo previo, según `fecha_hecho`.
- **Adjuntos**: por cada línea de `adjuntos`, `RV.set('#tipoDocumento', value_del_tipo)` y subir el archivo según `portal-mecanica.md` §4 (Claude in Chrome: `file_upload`; navegador integrado: el usuario hace clic en "Cargar archivo"). Tipos válidos en esta categoría: Boleta de venta (7) · Boleto de viaje (6) · Reserva (8) · Ticket de equipaje (9) · Factura (10) · Garantía (13) · Hoja de reclamación (11) · Hoja de servicio técnico (12) · Otros (14). Verificar que cada archivo quede listado bajo su tipo.

**En el resumen, cotejar además:**
   - Sector = "Transporte"
   - ¿Expusiste…? y medio; ¿Cómo realizaste la compra?
   - Motivo completo, sin escapes de Markdown ni cortes
   - Documentos adjuntos: nombre y tipo de cada uno
   - Fecha de suceso (exacta o aproximada) y ¿Qué solicitas? completo
   - Sede donde serás atendido = `oficina`

**Notas de la categoría:**
- Incluir en el motivo: ruta, fecha y número de vuelo/servicio, código de reserva, qué se ofreció y qué ocurrió, gastos concretos con montos.
- Pedir devoluciones o reembolsos concretos ("reembolso de S/ X del boleto"), no "compensación" ni "indemnización" (bloquean).

## Colegios (`categoria: colegios`, INDICE = 2)

Campos en orden de pantalla (O = obligatorio, Op = opcional). Usar los helpers `RV.*`.

| # | Campo del portal | O/Op | Fuente en la ficha | Acción |
|---|---|---|---|---|
| 1 | ¿Deseas presentar el reclamo de manera anónima? | O | `anonimo` | `RV.click('#anonimoSi')` o `#anonimoNo`. Si la ficha dice `si`, confirmar antes con el usuario que entiende que no habrá mediación con sus datos |
| 2 | ¿Expusiste tu problema ante el reclamado? | O | `expuso_al_proveedor` | `RV.click('#exponeReclamoSi')` o `#exponeReclamoNo` |
| 3 | Medio de reclamo (aparece si Sí) | O si Sí | `medio_reclamo` | `RV.set('nuReclamoMedioReclamo', v)` 1 Personal · 2 Telefónico · 3 Virtual · 4 Libro de reclamaciones · 5 Otros |
| 4 | Otro medio (si 5) | O si Otros | `medio_reclamo_otro` | `RV.set('vcOtroMedioReclamo', texto≤150)` |
| 5 | ¿Cómo realizaste la compra o la contratación del servicio? | O | `medio_compra` | `RV.set('#realizarCompra', v)` 1 Presencial · 2 Telefónico · 3 Virtual · 4 No compré/ No contraté |
| 6 | Explícanos el motivo del reclamo | O (≤4000) | `## MOTIVO` | `RV.set('#motivoReclamo', TEXTO)` → `RV.bloqueos()` debe devolver `motivo: ''` y `textareaMotivo: true` |
| 7 | Documentos (tipo + archivo) | Op (≤5, ≤5,25 MB) | `adjuntos` | Ver abajo |
| 8 | ¿Recuerdas cuándo sucedió el problema? | O | `recuerda_fecha` | `RV.click('#sucesoSi')` → `await RV.fecha('DD/MM/AAAA')` (debe devolver la fecha) · o `#sucesoNo` → `RV.set('#fechaAproxSuceso', texto≤150)` |
| 9 | ¿Qué solicitas? | O (≤3000) | `## SOLICITUD` | `RV.set('#textSolicitud', TEXTO)` → `RV.bloqueos()` debe devolver `solicitud: ''` |
| 10 | Oficina del Indecopi | O | `oficina` | `RV.set('#oficinaIndecopi', value)` (value en `catalogos.json > oficinas`) |

Detalles:
- Pasar los textos con `JSON.stringify` para escapar comillas y saltos de línea. Verificar después `RV.q('#motivoReclamo').value.length` = longitud del texto de la ficha.
- Si `RV.bloqueos()` muestra texto (palabra resaltada), aplicar el procedimiento "Filtro de palabras" de `portal-mecanica.md` §4 y actualizar también la ficha.
- Fecha: si hubo reclamo previo, la ficha trae normalmente la fecha de la respuesta del proveedor; usar exactamente `fecha_hecho`.
- **Adjuntos**: por cada línea de `adjuntos`, `RV.set('#tipoDocumento', value_del_tipo)` y subir el archivo según `portal-mecanica.md` §4 (Claude in Chrome: `file_upload`; navegador integrado: el usuario hace clic en "Cargar archivo"). Tipos válidos en esta categoría: Certificado de estudios (5) · Comprobante de pago (4) · Factura (10) · Garantía (13) · Hoja de reclamación (11) · Hoja de servicio técnico (12) · Otros (14). Verificar que cada archivo quede listado bajo su tipo.

**En el resumen, cotejar además:**
   - Sector = "Colegios"
   - ¿Es un reclamo anónimo? = Sí/No
   - ¿Expusiste…? y medio; ¿Cómo realizaste la compra?
   - Motivo completo, sin escapes de Markdown ni cortes
   - Documentos adjuntos: nombre y tipo de cada uno
   - Fecha de suceso (exacta o aproximada) y ¿Qué solicitas? completo
   - Sede donde serás atendido = `oficina`

**Notas de la categoría:**
- Anónimo = Sí: la Etapa 3 no existe y el botón "Atrás" del resumen vuelve a la Etapa 2. Útil para alertar a INDECOPI sin exponerse; no sirve para obtener una solución personal.
- Adjuntos típicos: comprobantes de pago de pensiones/matrícula, certificado de estudios retenido, comunicaciones del colegio (tipo *Otros*).
- Universidades e institutos no van aquí: usar la categoría `otros`.

## Otros (`categoria: otros`, INDICE = 3)

Campos en orden de pantalla (O = obligatorio, Op = opcional). Usar los helpers `RV.*`.

| # | Campo del portal | O/Op | Fuente en la ficha | Acción |
|---|---|---|---|---|
| 1 | ¿Expusiste tu problema ante el reclamado? | O | `expuso_al_proveedor` | `RV.click('#exponeReclamoSi')` o `#exponeReclamoNo` |
| 2 | Medio de reclamo (aparece si Sí) | O si Sí | `medio_reclamo` | `RV.set('nuReclamoMedioReclamo', v)` 1 Personal · 2 Telefónico · 3 Virtual · 4 Libro de reclamaciones · 5 Otros |
| 3 | Otro medio (si 5) | O si Otros | `medio_reclamo_otro` | `RV.set('vcOtroMedioReclamo', texto≤150)` |
| 4 | ¿Cómo realizaste la compra o la contratación del servicio? | O | `medio_compra` | `RV.set('#realizarCompra', v)` 1 Presencial · 2 Telefónico · 3 Virtual · 4 No compré/ No contraté |
| 5 | Explícanos el motivo del reclamo | O (≤4000) | `## MOTIVO` | `RV.set('#motivoReclamo', TEXTO)` → `RV.bloqueos()` debe devolver `motivo: ''` y `textareaMotivo: true` |
| 6 | Documentos (tipo + archivo) | Op (≤5, ≤5,25 MB) | `adjuntos` | Ver abajo |
| 7 | ¿Recuerdas cuándo sucedió el problema? | O | `recuerda_fecha` | `RV.click('#sucesoSi')` → `await RV.fecha('DD/MM/AAAA')` (debe devolver la fecha) · o `#sucesoNo` → `RV.set('#fechaAproxSuceso', texto≤150)` |
| 8 | ¿Qué solicitas? | O (≤3000) | `## SOLICITUD` | `RV.set('#textSolicitud', TEXTO)` → `RV.bloqueos()` debe devolver `solicitud: ''` |
| 9 | Oficina del Indecopi | O | `oficina` | `RV.set('#oficinaIndecopi', value)` (value en `catalogos.json > oficinas`) |

Detalles:
- Pasar los textos con `JSON.stringify` para escapar comillas y saltos de línea. Verificar después `RV.q('#motivoReclamo').value.length` = longitud del texto de la ficha.
- Si `RV.bloqueos()` muestra texto (palabra resaltada), aplicar el procedimiento "Filtro de palabras" de `portal-mecanica.md` §4 y actualizar también la ficha.
- Fecha: si hubo reclamo previo, la ficha trae normalmente la fecha de la respuesta del proveedor; usar exactamente `fecha_hecho`.
- **Adjuntos**: por cada línea de `adjuntos`, `RV.set('#tipoDocumento', value_del_tipo)` y subir el archivo según `portal-mecanica.md` §4 (Claude in Chrome: `file_upload`; navegador integrado: el usuario hace clic en "Cargar archivo"). Tipos válidos en esta categoría: Factura (10) · Garantía (13) · Hoja de reclamación (11) · Hoja de servicio técnico (12) · Otros (14). Boletas, capturas y correos van como *Otros*. Verificar que cada archivo quede listado bajo su tipo.

**En el resumen, cotejar además:**
   - Sector = "Otros"
   - ¿Expusiste…? y medio; ¿Cómo realizaste la compra?
   - Motivo completo, sin escapes de Markdown ni cortes
   - Documentos adjuntos: nombre y tipo de cada uno
   - Fecha de suceso (exacta o aproximada) y ¿Qué solicitas? completo
   - Sede donde serás atendido = `oficina`

**Notas de la categoría:**
- Competencia: facturación, calidad, contratación no solicitada u ofertas de telefonía/internet (OSIPTEL), recibos de luz/agua/gas (OSINERGMIN/SUNASS), atención de salud (SUSALUD) no se tramitan aquí; palabras como *facturación, recibo de luz, Osiptel, negligencia médica* bloquean el paso. Si la materia es de otra entidad, derivar al usuario a esa entidad; nunca reescribir el texto para pasar el filtro. Solo se reformula el lenguaje sancionador en asuntos que sí son de INDECOPI.
- Varios responsables (tienda y fabricante): usar "Agregar otra persona reclamada" en la Etapa 2 y describir el rol de cada uno en el motivo.

## Llamadas de publicidad no autorizadas (`categoria: llamadas`, INDICE = 4)

| # | Campo del portal | O/Op | Fuente en la ficha | Acción |
|---|---|---|---|---|
| 1 | Solicitaste el cese de la/s llamada/s al reclamado | O | `cese_solicitado` | `RV.click('#exponeReclamoSi')` o `#exponeReclamoNo` (no pide medio) |
| 2 | Indique su número telefónico (donde recibió la/s llamadas) | O (7–12 díg.) | `telefono_propio` | `RV.set('#vcNumeroCuenta', digitos)` |
| 3 | ¿Dio autorización para recibir publicidad? | O | `autorizo_publicidad` | `RV.click('#sucesoSi')` o `#sucesoNo` (el portal reutiliza esos ids) |
| 4 | Motivo del reclamo | Fijo | — | Solo lectura. Al avanzar, el portal inserta `telefono_propio` en el texto |
| 5 | Adjuntar evidencia (imagen/captura) | Op (≤5, ≤5,25 MB) | `adjuntos` | Tipos: Imágenes (15) · Hoja de reclamación (11) · Hoja de servicio técnico (12) · Otros (14). Subir según `portal-mecanica.md` §4 |
| 6 | Fecha de ocurrencia de la/las llamadas | O (≥1) | `llamadas` | Por cada llamada, ver abajo |
| 7 | Requerimiento | Fijo | — | "Cese de llamadas publicitarias no autorizadas." (sin acción) |
| 8 | Oficina del Indecopi | O | `oficina` | `RV.set('#oficinaIndecopi', value)` |

Registrar cada llamada (`- número | DD/MM/AAAA | HH:MM`):
```js
RV.set('#vcNroTelefOcurrencia', 'NUMERO_SOLO_DIGITOS');
await RV.fecha('DD/MM/AAAA');                 // debe devolver la fecha; teclearla no funciona
RV.set('#horOcurrencia', 'H');                // 0..23 sin cero a la izquierda (p. ej. '8', '20')
RV.set('#minOcurrencia', 'M');                // 0..59 sin cero a la izquierda
RV.link('Agregar'); await RV.w(600);
[...document.querySelectorAll('form')][0].innerText.match(/Teléfono:[\s\S]*?(?=Requerimiento)/)?.[0]
```
- Verificar en el "Listado de fecha de ocurrencia" que teléfono, fecha y "HH h MM min" sean los de la ficha. Si una entrada sale mal, borrarla con su enlace "Eliminar" y repetir.
- Número propio ≠ número que llamó: no confundirlos.
- Siguiente: `RV.siguiente()` → `#/identifica-empresa`. Error "Se requiere un registro del listado…" = falta hacer clic en Agregar.

**En el resumen, cotejar además:**
   - Sector = "Llamadas de publicidad no autorizadas"
   - Solicitaste el cese… = `cese_solicitado`; número telefónico propio; ¿Dio autorización…? = `autorizo_publicidad`
   - Motivo fijo con el número propio insertado
   - Listado de llamadas (teléfono, fecha, hora de cada una) y evidencia adjunta
   - Requerimiento "Cese de llamadas publicitarias no autorizadas." y sede = `oficina`

**Notas de la categoría:**
- Identificar al proveedor: la empresa cuyos productos se ofrecieron. Si el RUC no se conoce, buscarlo (nombre comercial + "RUC") y contrastar con dos fuentes; nombres comerciales parecidos pueden pertenecer a empresas distintas.
- Si el usuario tiene captura del registro de llamadas, adjuntarla como *Imágenes*.
- Si ya autorizó publicidad, advertir que el reclamo pierde sustento antes de continuar.
