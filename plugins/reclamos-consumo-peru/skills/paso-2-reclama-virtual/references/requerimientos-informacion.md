# Análisis del proceso y requerimientos de información — Reclama Virtual

Objetivo: que el usuario entregue **todo** lo necesario antes de abrir el portal, para que el llenado sea una sola pasada sin preguntas intermedias ni rebotes del filtro de palabras.

## 1. El proceso de punta a punta

```
[0] Antes del portal: Paso 0 (expediente y viabilidad) y Paso 1 (reclamo al proveedor y su respuesta)
    → elegir categoría → MOTIVO y SOLICITUD desde el expediente y la respuesta → ficha → validar_ficha.py
[1] Portada: "Siguiente" → "He leído los alcances del servicio" → categoría
[2] Etapa 1 · Cuéntanos tu reclamo      (varía por categoría; filtro de palabras; adjuntos se suben aquí)
[3] Etapa 2 · Identifica al reclamado   (RUC/DNI → autocompleta SUNAT/RENIEC; dirección obligatoria)
[4] Etapa 3 · Completa tus datos        (DNI → autocompleta RENIEC; correo y teléfono obligatorios)
                                          (se omite si Colegios + anónimo)
[5] Resumen · Verifica la información   (editar por bloque)
[6] El usuario revisa el resumen y pulsa ENVIAR RECLAMO
[7] ¡REGISTRO EXITOSO! → ID de reclamo, cargo PDF y correo
[8] Después (INDECOPI): traslado al proveedor → mediación/conciliación (audiencia virtual o presencial)
    → acuerdo (registrar literal y verificar su cumplimiento) o sin acuerdo (fin del ciclo del plugin)
```

### Puntos de falla y cómo se neutralizan

| Punto | Qué pasa | Prevención |
|---|---|---|
| Filtro de palabras (Etapa 1) | Oculta el texto y no deja avanzar | Correr `validar_ficha.py`; reescribir con sinónimos (sección 4) |
| Límite de caracteres | Textarea corta en 4000 / 3000 | Validar longitud; condensar antes, no en el portal |
| Markdown / emojis | Se ve literal o puede bloquear el envío | `validar_ficha.py --limpiar` |
| Número de cuenta con asteriscos/espacios | El campo solo acepta dígitos | Omitirlo o dejar solo dígitos |
| Calendario | No acepta tecleo, ni fechas futuras, ni antes de 2016 | Fecha DD/MM/AAAA válida; helper `RV.fecha` |
| Adjuntos | `alert` si > 5,25 MB, extensión inválida o nombre repetido; máx. 5 | Revisar tamaño, extensión y nombres; comprimir o unir PDFs |
| Adjuntos en navegador integrado | No hay subida automática de archivos | Usar Claude in Chrome o que el usuario haga clic en "Cargar archivo" |
| RUC/DNI sin respuesta | Servicios RENIEC/SUNAT lentos | Esperar ~6 s, reintentar una vez; llenar a mano si el portal lo habilita |
| Razón social inesperada | RUC equivocado | Cotejar con `reclamado_nombre_esperado` |
| Recarga de la página | Se pierde lo avanzado (estado en la pestaña) | No recargar ni cambiar de pestaña |
| Doble envío | Reclamo duplicado | Un solo clic; si aparece "ya ha sido registrado", no reintentar |

## 2. Requerimientos de información por caso

Leyenda: **U** = lo da el usuario · **D** = se deduce del expediente · **A** = lo autocompleta el portal · **F** = texto fijo del portal.

### 2.1 Comunes a todas las categorías

| Dato | Origen | Obligatorio | Formato / fuente |
|---|---|---|---|
| Categoría | D (confirmar con U si hay duda) | Sí | Ver instructivo |
| Oficina de INDECOPI | U (por defecto la última usada) | Sí | Nombre exacto de `catalogos.json` |
| RUC del proveedor (o DNI/CE si es persona natural) | D (carta, comprobante, web del proveedor; verificar en SUNAT) | Sí, salvo "No cuento con esa información" | 11 dígitos, empieza con 10/15/17/20 |
| Razón social esperada | D | Para cotejo | — |
| Dirección del reclamado | A (desde RUC) o U | Sí | ≤200 |
| Correo / teléfono del reclamado | U | No | Dejar vacío salvo dato verificado |
| Tipo de persona del reclamante | U | Sí | Natural / Jurídica |
| Documento del reclamante | U (pedirlo al llenar; no guardarlo en memoria) | Sí | DNI 8 · CE 8–12 · RUC 11 · Pasaporte 7–12 |
| Nombres y dirección del reclamante | A (RENIEC con DNI) | Sí | Con CE/Pasaporte tener apellidos y nombres a mano |
| Correo y teléfono del reclamante | U | Sí | El correo recibe todas las notificaciones |
| Discapacidad | U | No | No / visual / auditiva / motora / cognitiva |
| Representante (si reclamante es persona jurídica) | U | Sí | DNI, dirección, correo, teléfono |

### 2.2 Categorías con texto libre (Bancario, Transporte, Colegios, Otros)

| Dato | Origen | Obligatorio | Formato / regla |
|---|---|---|---|
| ¿Expuso el problema al proveedor? | D (hay hoja de reclamación / respuesta) | Sí | Sí/No |
| Medio usado | D | Si "Sí" | Personal · Telefónico · Virtual · Libro de reclamaciones · Otros (+ texto ≤150) |
| Cómo compró o contrató | D/U | Sí | Presencial · Telefónico · Virtual · No compré/ No contraté |
| MOTIVO | D (redactado desde el relato y documentos) | Sí | ≤4000, texto plano, sin palabras bloqueadas ni emojis |
| Fecha del problema | D | Sí | Exacta DD/MM/AAAA o aproximada (≤150). Criterio del plugin: si hubo reclamo previo, usar la **fecha de la respuesta del proveedor** (o de su vencimiento sin respuesta), que es cuando se configura la controversia |
| SOLICITUD | D | Sí | ≤3000, mismas reglas; pedidos concretos y verificables |
| Adjuntos | D | No | ≤5, ≤5,25 MB, tipo por categoría |
| **Bancario**: producto financiero | D | Sí | Una de las 11 opciones |
| **Bancario**: número de cuenta | U | No | Solo dígitos, ≤30 (omitir si es tarjeta completa) |
| **Colegios**: ¿anónimo? | U | Sí | Recomendado "No" (con "Sí" se pierde la mediación personal) |

### 2.3 Llamadas de publicidad no autorizadas

| Dato | Origen | Obligatorio | Formato / regla |
|---|---|---|---|
| ¿Solicitó el cese al proveedor? | U | Sí | Sí/No (normalmente No) |
| Número propio (donde recibió) | U | Sí | 7–12 dígitos |
| ¿Autorizó recibir publicidad? | U | Sí | Normalmente No; si es Sí, el reclamo pierde sustento |
| Llamadas: número que llamó + fecha + hora:minuto | U (captura del registro de llamadas) | ≥1 | 7–12 dígitos sin +51; fecha ≤ hoy; 24 h |
| Evidencia (captura) | U | No | Tipo "Imágenes" |
| Motivo y requerimiento | F | — | No editables |

### 2.4 Checklist para pedir al usuario (una sola vez, antes de empezar)

- [ ] Relato breve: qué pasó, cuándo, con qué proveedor, qué quiere lograr.
- [ ] Documentos del caso (comprobante, contrato, hoja de reclamación y respuesta, estados de cuenta, capturas).
- [ ] Oficina de INDECOPI.
- [ ] Número de documento del reclamante (en el momento del llenado).
- [ ] Correo y teléfono de contacto (si no están en el perfil).
- [ ] Bancario: producto; número de cuenta solo si quiere incluirlo.
- [ ] Colegios: ¿anónimo?
- [ ] Llamadas: número propio, número(s) que llamaron con fecha y hora, ¿pidió cese?, ¿autorizó publicidad?
- [ ] El usuario sabe que el plugin se detiene en el resumen y que el clic en "ENVIAR RECLAMO" lo hace él.

## 3. Estructura recomendada de la carpeta del caso

```
<carpeta de casos>/
  r<N>_<proveedor>_<tema-breve>/
    r<N>_<proveedor>_expediente/             00–07 · Estado del caso.md · caso.json · evidencias-en-bruto/ · al cierre, 10 Legajo habilitante.md
    r<N>_<proveedor>_reclamo-proveedor/      Reclamo proveedor - <Proveedor>.md · constancia · respuesta · 08 Análisis de respuesta.md
    r<N>_<proveedor>_conciliacion-indecopi/  Ficha Reclama Virtual - <Proveedor>.md · adjuntos · Cargo Reclama Virtual - <Proveedor>.md · 08b · 09 Plan de audiencia.md · acta
```
La ficha (`plantilla-ficha.md`) es el único insumo de `paso-2-formulario`; se construye desde el 00 Expediente, el 07 y el 08 (análisis de la respuesta del proveedor). Casos anteriores al plugin con `.md` de reclamación sueltos: primero reconstruir el caso con `gestionar-reclamo` (modo retrospectivo) hasta tener 08; nunca copiar al portal textos viejos sin pasar por `validar_requerimientos.py`.

## 4. Redacción compatible con el filtro

Mantener el enfoque de **mediación/conciliación**: pedir conductas concretas del proveedor, no castigos ni actos de autoridad. Estas reformulaciones son solo para el lenguaje sancionador en asuntos que sí son de INDECOPI; nunca para pasar el filtro de competencia.

| En lugar de… (bloquea) | Usar… |
|---|---|
| solicito **se disponga** / **se ordene** que… | solicito que el proveedor… / pido que la empresa… |
| que **se investigue** / **investigar** / investigaron | que se revise / se verifique / se evalúe; "revisaron" |
| **sanción**, **multa**, **infracción**, acciones administrativas | (omitir: no es un pedido conciliable) |
| **indemnización**, **resarcimiento**, **compensación**, daños y perjuicios, reparación civil | devolución de lo pagado / reembolso de S/ X / abono / corrección del cargo |
| **reconocimiento** de… | que el proveedor admita / acepte / asuma… |
| medidas correctivas | que el proveedor corrija / regularice… |
| **fiscalización**, **inspección**, fiscalizar | verificación / revisión |
| me **estafó** | me cobró indebidamente / no cumplió lo ofrecido |
| **facturación** (indebida) de un producto o servicio de competencia de INDECOPI | cobro / cargo / monto cobrado en el comprobante. Si se trata de telecomunicaciones o servicios públicos, no reformular: derivar a la entidad competente |
| recibo de luz / agua / gas | (probablemente competencia de OSINERGMIN/SUNASS: reconsiderar la vía) |

Atención a subcadenas: "sancionatoria", "multas", "investigaron", "indemnizatorio", "compensación" dentro de otras palabras también bloquean.
