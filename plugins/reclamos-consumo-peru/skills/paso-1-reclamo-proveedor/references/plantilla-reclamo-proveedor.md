# Reclamo al proveedor — <Proveedor> (caso r<N>)
<!-- Guardar en r<N>_<proveedor>_reclamo-proveedor/ como "Reclamo proveedor - <Proveedor>.md". Fuente: 00 Expediente (P## del Paso 1). -->

tipo: reclamo                  <!-- reclamo | queja -->
canal: Libro de Reclamaciones virtual   <!-- virtual | físico | canal SBS (web/agencia/teléfono) | correo | otro -->
url_canal:                     <!-- URL oficial del Libro de Reclamaciones o del formulario de reclamos (verificar el dominio) -->
proveedor: <razón social> · RUC <11 dígitos> · establecimiento/dirección
producto_servicio: <qué se compró o contrató; n.º de comprobante, pedido o contrato>
monto: S/ <monto del producto o servicio objeto del reclamo>
canal_respuesta: correo <correo del usuario>

## DETALLE (versión completa, ≤ 3000)
1. Relación de consumo: …
2. Hechos (cronológicos, con fecha, monto y documento): …
3. Lo esperado según lo ofrecido frente a lo ocurrido: …
4. Gestiones previas: …

## DETALLE (versión corta, ≤ 1000)
…

## PEDIDO
<!-- Copiar literalmente de 07. Primero los requerimientos (máx. 4, una oración cada uno, sin preguntas), luego la pretensión. Las marcas [S01]/[P01] son para validar_requerimientos.py: se quitan al pegar el texto en el formulario del proveedor. -->
1. Requiero … , de forma que se verifique … [S01]
2. Requiero … , de forma que se verifique … [S02]
3. De no acreditarse lo requerido, solicito … [P01]      <!-- o, si la pretensión es directa: "Solicito …" -->
Plazo y canal: respuesta escrita y fundamentada, con la documentación de sustento, al correo indicado dentro del plazo legal de 15 días hábiles.

## ADJUNTOS / DOCUMENTOS DE RESPALDO
- E## | <archivo> | se adjunta / se cita / se envía por correo con el código

## CONTROL
- [ ] Datos mínimos completos (nombre, documento, domicilio o correo, fecha, detalle)
- [ ] PEDIDO idéntico a 07 (S## + P##) y `validar_requerimientos.py` sin errores
- [ ] Detalle limitado a los hechos necesarios (conciso)
- [ ] Sin lenguaje sancionador ni amenazas; sin datos sensibles innecesarios
- [ ] Largo ajustado al límite del formulario
