# Instructivo de opciones de Reclama Virtual (INDECOPI)

Relevado el 23/09/2026 recorriendo el portal y leyendo su código y su API pública. Portal: https://enlinea.indecopi.gob.pe/reclamavirtual/

## 0. Qué es y qué no es

- **Es** el canal virtual para **reclamos de consumo** ante el Servicio de Atención al Ciudadano (SAC) de INDECOPI. INDECOPI traslada el reclamo al proveedor y actúa como intermediario (mediación o conciliación, con audiencias presenciales o virtuales). Si hay acuerdo, el caso se cierra. Si no lo hay, termina el ciclo de este plugin: lo que sigue está fuera de su alcance.
- **No es** para pedir sanciones, multas, medidas correctivas ni indemnizaciones, ni para presentar otros escritos: eso corresponde a otros canales, fuera del alcance de este plugin. El portal lo hace cumplir con un **filtro de palabras** que bloquea el avance (ver sección 3).
- Gratuito y 100% virtual. Sin cuenta ni login. Todo el flujo son 3 etapas + resumen + envío.

## 1. Las 5 opciones y cuándo usar cada una

| # | Opción en pantalla | Úsala cuando… | No la uses cuando… |
|---|---|---|---|
| 1 | **Servicios Bancarios y Financieros** | El reclamado es un banco, financiera, caja u otra entidad financiera, por un producto financiero (tarjetas, créditos, cuentas, depósitos, CTS, hipotecario, leasing, etc.). | Seguros o AFP: el portal no tiene opción propia; evaluar "Otros" o la entidad supervisora. |
| 2 | **Transporte** | Cualquier medio de transporte: aéreo, terrestre, marítimo o fluvial (vuelos, buses interprovinciales, equipaje, reservas, boletos). | Taxi por aplicativo u otros servicios no de transporte en sí (evaluar "Otros"). |
| 3 | **Colegios** | Colegios particulares (educación básica privada): pensiones, matrícula, certificados, cobros. Es la **única opción que permite reclamo anónimo**. | Universidades, institutos, academias: usar "Otros". |
| 4 | **Otros** | Todo otro tema de consumo: tiendas, e-commerce, inmobiliarias, electrodomésticos, garantías, espectáculos, servicios técnicos, telecomunicaciones fuera de la competencia de OSIPTEL, etc. | Temas de otra entidad: facturación de servicios públicos (agua, luz, gas → SUNASS/OSINERGMIN), reclamos de telefonía/internet sobre facturación, calidad, contratación no solicitada o incumplimiento de ofertas (OSIPTEL), salud/mala praxis (SUSALUD). El portal marca en verde estas palabras y no deja avanzar. |
| 5 | **Llamadas de publicidad no autorizadas** | Exclusivamente para reportar llamadas con fines publicitarios que el consumidor no autorizó (telemarketing, llamadas robotizadas ofreciendo productos). | Llamadas de cobranza, fraude o cualquier otro problema con el mismo proveedor: usar la categoría que corresponda al producto. |

## 2. Características particulares de cada formulario (Etapa 1)

Las Etapas 2 (reclamado) y 3 (reclamante) y el resumen son **iguales** para las cinco opciones (con la excepción del anónimo en Colegios). Lo que cambia es la Etapa 1:

### Comparativo de campos de la Etapa 1

| Campo | Bancario | Transporte | Colegios | Otros | Llamadas |
|---|---|---|---|---|---|
| ¿Reclamo anónimo? | – | – | **Obligatorio** (Sí/No) | – | – |
| ¿Expusiste tu problema ante el reclamado? | Oblig. | Oblig. | Oblig. | Oblig. | Se reemplaza por **"¿Solicitaste el cese de la/s llamada/s?"** (Oblig.) |
| Medio de reclamo (si Sí) | Oblig. | Oblig. | Oblig. | Oblig. | – |
| Otro medio (si "Otros") | Oblig., ≤150 | Oblig., ≤150 | Oblig., ≤150 | Oblig., ≤150 | – |
| Producto financiero | **Oblig.** (11 opciones) | – | – | – | – |
| Número de cuenta | **Opcional**, solo dígitos, ≤30 (texto libre si producto "Otros") | – | – | – | – |
| Tu número telefónico (donde recibiste las llamadas) | – | – | – | – | **Oblig.**, 7–12 dígitos |
| ¿Dio autorización para recibir publicidad? | – | – | – | – | **Oblig.** (Sí/No) |
| ¿Cómo realizaste la compra o contratación? | Oblig. | Oblig. | Oblig. | Oblig. | – |
| Explícanos el motivo del reclamo | Oblig., ≤4000 | Oblig., ≤4000 | Oblig., ≤4000 | Oblig., ≤4000 | **Texto fijo del sistema, no editable** (se le agrega tu número) |
| Adjuntos (≤5, ≤5,25 MB c/u) | Opcional | Opcional | Opcional | Opcional | Opcional ("evidencia": captura/imagen) |
| ¿Recuerdas cuándo sucedió? | Oblig. → fecha exacta (calendario) o aproximada (≤150) | ídem | ídem | ídem | – |
| Registro de llamadas (número que llamó + fecha + hora + minuto → "Agregar") | – | – | – | – | **Oblig.**, al menos 1; admite varias |
| ¿Qué solicitas? | Oblig., ≤3000 | Oblig., ≤3000 | Oblig., ≤3000 | Oblig., ≤3000 | **Requerimiento fijo**: "Cese de llamadas publicitarias no autorizadas." |
| Oficina de INDECOPI | Oblig. (31 sedes) | Oblig. | Oblig. | Oblig. | Oblig. |

### Tipos de documento adjunto por opción

| Opción | Tipos disponibles |
|---|---|
| Bancario | Contrato · Estado de cuenta · Hoja resumen · Factura · Garantía · Hoja de reclamación · Hoja de servicio técnico · Otros |
| Transporte | Boleta de venta · Boleto de viaje · Reserva · Ticket de equipaje · Factura · Garantía · Hoja de reclamación · Hoja de servicio técnico · Otros |
| Colegios | Certificado de estudios · Comprobante de pago · Factura · Garantía · Hoja de reclamación · Hoja de servicio técnico · Otros |
| Otros | Factura · Garantía · Hoja de reclamación · Hoja de servicio técnico · Otros |
| Llamadas | Imágenes · Hoja de reclamación · Hoja de servicio técnico · Otros |

Formatos: pdf, jpg, jpeg, png, doc, docx, xls, xlsx, ppt, pptx, mp3, mp4 (el portal recomienda PDF). Máximo 5 archivos en total, 5,25 MB cada uno (5 509 120 bytes), sin nombres repetidos ni emojis en el nombre. **Se suben a INDECOPI apenas se eligen**, antes del envío.

### Particularidades por opción

**1. Servicios Bancarios y Financieros**
- Productos: Créditos comerciales, Crédito de consumo, Cuenta corriente, Depósito de ahorros, Depósito CTS, Arrendamiento financiero, Depósito a plazo, Tarjeta de crédito, Tarjeta de débito, Crédito hipotecario, Otros.
- El número de cuenta es opcional y solo acepta dígitos (no admite espacios, guiones ni asteriscos de enmascarado), salvo que el producto sea "Otros". Se traslada al proveedor: preferir omitirlo o poner solo lo imprescindible.
- En el resumen aparece como "¿Cuál es tu producto financiero? Producto: número".

**2. Transporte**
- Mismo formulario base que "Otros", con adjuntos propios del rubro (boleto, reserva, ticket de equipaje, boleta de venta).

**3. Colegios**
- Pregunta adicional "¿Deseas presentar el reclamo de manera anónima?". Si es **Sí**, el portal **salta la Etapa 3** (no pide datos del reclamante) y va directo al resumen. Consecuencia: INDECOPI no tendrá a quién notificar ni convocar; útil solo para alertar, no para obtener una solución personal.
- Adjuntos propios: certificado de estudios, comprobante de pago.

**4. Otros**
- Formulario base. Es la opción residual; revisar antes que el problema no sea competencia de otra entidad (el filtro "verde" lo bloquea: facturación, recibo de luz/agua/gas, Sedapal, Osinergmin, Luz del Sur, Osiptel, mala praxis, negligencia médica, intervenciones médicas).

**5. Llamadas de publicidad no autorizadas**
- No hay motivo ni solicitud libres: el portal usa textos fijos. El motivo que se registra es: "El reclamante señala ser titular de la línea telefónica <tu número>. Al respecto, manifiesta que viene recibiendo llamadas telefónicas constantes con fines publicitarios, mediante las cuales se le ofrecen productos y servicios que, según indica, no ha autorizado." El requerimiento es "Cese de llamadas publicitarias no autorizadas."
- En lugar de detalles, se registra cada llamada: **número que llamó** (7–12 dígitos, solo números), **fecha** (calendario), **hora** (00–23) y **minuto** (00–59, formato 24 h) → botón **Agregar**. Se pueden agregar varias y eliminar las erróneas. Se exige al menos una.
- Se pide **tu** número (donde recibiste las llamadas), distinto del que llamó.
- "¿Solicitaste el cese…?" reemplaza a "¿Expusiste tu problema…?" y no pide medio. No pregunta cómo compraste ni la fecha del suceso.
- No requiere reclamo previo al proveedor.

## 3. Reglas transversales que conviene conocer

1. **Filtro de palabras** (motivo y solicitud; no aplica a Llamadas). Si el texto contiene alguna frase de la lista, el portal la resalta y **no deja pasar a la Etapa 2**. Coincide por **subcadena** y sin mayúsculas: "investigaron" contiene "investigar"; "sancionatoria" contiene "sancion". Frases frecuentes en reclamos redactados por abogados que bloquean: *se disponga, se ordene, se investigue, investigar, imponer/imponga, sanción, multa, infracción, indemnización/indemnizar, resarcimiento, compensación, reconocimiento, reparación civil, medidas correctivas, daños y perjuicios, acciones administrativas, fiscalización, inspección, estafó*. Y "otra entidad": *facturación, recibo de luz/agua/gas, Osiptel, Osinergmin, Sedapal, Luz del Sur, mala praxis, negligencia médica*. Lista completa en `palabras-bloqueadas.json`.
2. **Sin emojis** en textos ni en nombres de archivo.
3. **Texto plano**: el Markdown (\[1\], **negritas**, #) se ve literal.
4. **Fecha** solo por calendario (desde 2016, no futura).
5. **Oficinas**: 31 sedes; la elegida gestiona el reclamo (en Lima: Sede Central, Lima Norte, Gamarra, Congreso, Aeropuerto AIJCH).
6. **Reclamado**: persona jurídica por RUC (autocompleta razón social y dirección desde SUNAT) o persona natural por DNI/CE/RUC; opción "No cuento con esa información" para llenarlo a mano. Admite varios reclamados.
7. **Reclamante**: persona natural (DNI autocompleta desde RENIEC; también CE, RUC, Pasaporte) o persona jurídica (RUC + representante). Correo y teléfono obligatorios. Discapacidad opcional (visual, auditiva, motora, cognitiva). Admite varios reclamantes.
8. **Envío**: botón "ENVIAR RECLAMO" en el resumen; lo pulsa el usuario (el plugin se detiene en el resumen). Tras el envío se muestra "¡REGISTRO EXITOSO!", se puede descargar el cargo en PDF y llega un correo con el cargo.
9. Dictado por voz disponible en el motivo (no relevante para automatización).
