# Plantilla del expediente del caso

El expediente es el **contrato de entrega** del Paso 0 hacia el Paso 1 (reclamo al proveedor) y el Paso 2 (Reclama Virtual). Vive en la carpeta del caso, junto con el `Estado del caso.md` (ver `gestionar-reclamo/references/proceso-reclamo.md`):

```
<carpeta de casos>/r<N>_<proveedor>_<tema>/r<N>_<proveedor>_expediente/
  00 Expediente - <Proveedor>.md          ← índice + síntesis + insumos para formular (lo escribe el orquestador)
  01 Registro de evidencias.md            ← investigador-evidencias
  02 Cronología de hechos.md              ← reconstructor-hechos
  03 Matriz hecho-prueba.md               ← correlacionador-prueba
  04 Viabilidad y encuadre.md             ← analista-viabilidad
  05 Auditoría y pendientes.md            ← auditor-expediente
  06 Preguntas de investigación.md        ← estratega-petitorio (modo A) + respuestas del consumidor
  07 Estrategia y petitorio.md            ← estratega-petitorio (modo B): requerimientos S## y petitorio
  10 Legajo habilitante.md                ← scripts/legajo.py (al cerrar sin acuerdo)
  caso.json                               ← estado legible por el plugin (scripts/estado.py)

r<N>_<proveedor>_reclamo-proveedor/
  08 Análisis de respuesta.md             ← analista-respuesta (respuesta al reclamo)
r<N>_<proveedor>_conciliacion-indecopi/
  08b Análisis respuesta traslado.md      ← analista-respuesta (respuesta al traslado de INDECOPI)
  09 Plan de audiencia.md                 ← preparador-audiencia
```

Orden de ejecución del Paso 0: 01 → 02 → 03 ∥ 04 → 06 (preguntas) → respuestas del consumidor → actualización de 01–03 si hay evidencia nueva → 07 → 05 (auditoría final).

Convenciones comunes:
- IDs estables (nunca renumerar; si algo se descarta, marcarlo "(descartado)"):

| ID | Qué es | Dónde nace |
|---|---|---|
| E## | Evidencia | 01 |
| H## | Hecho | 02 |
| B## | Brecha probatoria (hecho sin prueba suficiente, con su poseedor probable) | 03 |
| P## | Pedido o pretensión | 04 (se ajusta en 07) |
| R## | Respuesta previsible del proveedor y réplica | 04 |
| Q## | Pregunta de investigación o pendiente (se dirige primero al consumidor) | 06 (otros agentes proponen candidatas) |
| S## | Requerimiento al proveedor (solo lo que el consumidor no pudo responder ni probar) | 07 |
| A## | Admisión del proveedor (cita literal) | 08, respuesta al traslado, acta |
| C## | Contradicción (entre documentos del proveedor, o de estos con el expediente) | cualquier archivo |
| O## | Omisión, respuesta genérica o negativa sin sustento del proveedor | 08 |
- Solo el `investigador-evidencias` asigna E##. Si otro agente encuentra una fuente nueva, la cita con un ID provisional **N##** (fuente, fecha, cita) y la lista al final de su archivo; el orquestador la registra como E## en la siguiente actualización de 01.
- La numeración de C##, Q##, A## y O## es **continua en todo el expediente**: cada agente continúa desde el número más alto que ya exista en los archivos previos.
- **Modo retrospectivo** (caso con pasos ya ejecutados): cada archivo registra lo que realmente ocurrió en cada paso. 04 evalúa en retrospectiva y propone reaperturas solo si cumplen `proceso-reclamo.md` §2. 05 dictamina "Reapertura del Paso 1: Sí/No" en lugar de "Listo para el Paso 1".
- Fechas DD/MM/AAAA; montos "S/ 1 234,56" con el cálculo al lado; horas en formato 24 h.
- Cada afirmación lleva su fuente: `[E03 p.2]`. Sin fuente → "afirmado por el usuario" o "inferido" (explicar la inferencia).
- Encabezado de cada archivo: caso, proveedor, versión (v1, v2…), fecha de actualización, agente autor.
- Datos sensibles: el número de documento del reclamante y los números completos de cuenta o tarjeta no se copian al expediente; referenciar "ver E##".

---

## 00 Expediente - <Proveedor>.md

```markdown
# Expediente r<N> — <Proveedor>   (v<k>, DD/MM/AAAA)

## Ficha
| Campo | Valor |
|---|---|
| Reclamante | nombre · tipo (persona natural / persona jurídica-microempresa) |
| Proveedor | razón social · RUC · nombre comercial |
| Producto / servicio | … |
| Materia | idoneidad / información / atención de reclamos / métodos agresivos / cobro indebido / … |
| Dictamen de viabilidad | Procede / Procede con reencuadre / No procede ante INDECOPI / Información insuficiente |
| Tipo de manifestación (Paso 1) | Reclamo / Queja / Reclamo + queja |
| Canal del Paso 1 | Libro de Reclamaciones virtual o físico / canal SBS / otro |
| Categoría de Reclama Virtual (Paso 2) | bancario · transporte · colegios · otros · llamadas |
| Monto afectado | S/ … (cálculo en 02) |
| Gestión previa | Reclamo N.º … del DD/MM/AAAA · respuesta DD/MM/AAAA (en plazo / fuera de plazo / sin respuesta) o "aún no presentado" |
| Fecha límite de prescripción | DD/MM/AAAA (2 años desde …) |
| Preparación | Listo para el Paso 1: Sí/No · Listo para el Paso 2: Sí/No/N.A. (aún sin respuesta) |

## Resumen del caso (máx. 8 líneas)
## Teoría del caso (1 párrafo: qué pasó, qué deber incumplió el proveedor, qué se pide y por qué es proporcional)
## Reencuadre (si aplica): pedido original del usuario → pedido reencuadrado, motivo y aceptación del usuario
## Pendientes críticos (de 05, solo los bloqueantes)
## Insumos para la formulación
### Hechos probados en orden narrativo   (H## → texto de una línea → E##)
### Pedidos
- Paso 1: requerimientos S## (de 07) + pretensión P## directa o condicionada (monto, prestación, plazo)
- Paso 2, solicitud en Reclama Virtual: P## (se ajusta según la respuesta del proveedor; sin lenguaje sancionador)
### Evidencias a presentar
- Paso 1: E## que se adjuntan o citan en la hoja (según lo que permita el canal)
- Paso 2 (máx. 5 archivos, 5,25 MB): E## → tipo de adjunto sugerido
### Advertencias de redacción (palabras que bloquea Reclama Virtual, datos a no exponer)
## Índice de archivos del expediente
```

## 01 Registro de evidencias.md

Tabla con los campos de `guia-evidencias.md` §2 (una fila por evidencia) y, al final:
- **Evidencias faltantes** (del checklist por materia): qué falta, por qué importa, cómo obtenerla y quién (usuario / Claude).
- **Mejoras sugeridas** a las evidencias existentes (exportar a PDF, captura del perfil del emisor, tachar datos).

## 02 Cronología de hechos.md

| H## | Fecha y hora | Hecho (una conducta, un actor) | Actor | Canal / lugar | Monto | Estado | Fuente |
|---|---|---|---|---|---|---|---|
Estado: **Acreditado** (hay prueba directa) · **Indiciario** (prueba indirecta) · **Afirmado** (solo relato) · **Controvertido** (el proveedor lo niega o hay pruebas en conflicto).

Secciones adicionales:
- Sección `## Plazos computados` (con ese encabezado exacto; `legajo.py` la copia): respuesta al reclamo (fecha del reclamo + 15 días hábiles = fecha límite, con los días que en realidad transcurrieron), prescripción, plazos de acuerdos u ofrecimientos.
- **Compromisos u ofrecimientos del proveedor** (cita literal + fecha + medio + E##).
- **Contradicciones**, una por línea en formato `C## | ref (H##/E##) | descripción | fuente` (lo lee `legajo.py`).
- **Vacíos** (qué no se sabe): se proponen como Q## candidatas para 06.

## 03 Matriz hecho-prueba.md

1. **Cobertura de elementos del caso** (1 consumidor · 2 proveedor · 3 relación de consumo · 4 conducta · 5 afectación · 6 gestión previa): para cada uno, los hechos y pruebas que lo sostienen, la fortaleza (Alta/Media/Baja/Nula) y lo que falta.
2. **Matriz**: filas H##, columnas E##. En cada celda: D (prueba directa), I (indirecta), C (contradice). Columna final "Cobertura".
3. **Brechas B##**: hechos sin prueba o solo afirmados, ordenados por importancia, con la prueba que los cerraría y su **poseedor probable** (Consumidor · Proveedor · Tercero · Pública).
4. **Evidencias huérfanas** (no prueban ningún hecho relevante) → sugerir si se descartan.
5. **Carga de la prueba**: qué le corresponde acreditar al consumidor y qué defensas tendría que probar el proveedor (art. 104).

## 04 Viabilidad y encuadre.md

1. **Test de viabilidad** (8 preguntas de `viabilidad-reencuadre.md`) con la respuesta y el sustento de cada una.
2. **Competencia**: INDECOPI u otra entidad; si es mixta, qué parte va a cada una.
3. **Infracciones y normas**: por cada conducta, el derecho o deber vulnerado (artículo), los hechos que la configuran (H##) y las pruebas (E##). Citar solo normas verificadas; si hay duda de vigencia, marcarlo.
4. **Monto afectado y prescripción**: cálculo y fecha límite.
5. **Test de proporcionalidad y reencuadre**: el pedido original frente al pedido proporcional; tipo de manifestación (reclamo/queja); motivo del ajuste explicado para el usuario.
6. **Pedidos** (P##):
   - Paso 1: pretensión concreta y verificable, con todas sus consecuencias, y su forma sugerida (directa o condicionada). Los requerimientos S## se definen en 07.
   - Paso 2: solicitud conciliable, con variantes según el tipo de respuesta del proveedor (sin respuesta / rechazo / oferta parcial).
7. **Respuestas previsibles del proveedor y réplica** (R##), según la materia. Ejemplos: llamadas → consentimiento; productos → mal uso o imprudencia; banca → "los cobros son correctos según contrato", "la información está en el estado de cuenta"; general → uso comercial, "ya se solucionó", incompetencia. Si el proveedor ya respondió, sus argumentos reales reemplazan a los previsibles.
8. **Teoría del caso** (1 párrafo), **dictamen** (Procede / Procede con reencuadre / No procede ante INDECOPI / Información insuficiente) y **fortaleza global** (Alta/Media/Baja) justificada.
9. **Qué registrar si el proveedor ofrece algo** (texto literal, plazo, medio), para que sea exigible.

## 05 Auditoría y pendientes.md

1. **Hallazgos** por severidad: Bloqueante (impide presentar) · Importante (debilita) · Menor. Cada uno con su ubicación (archivo + ID) y su corrección.
2. **Verificaciones**: cada afirmación tiene fuente; fechas y montos consistentes entre archivos; cálculos reproducidos; IDs coherentes; normas citadas existentes; ausencia de datos sensibles expuestos.
3. **Nivel de preparación**: Paso 1 (Sí/No + qué falta) · Paso 2 (Sí/No/N.A. + qué falta).
4. **Pendientes**: remitir a las Q## de 06. Si hay pendientes nuevos para el usuario, proponerlos como "Q## propuesta" para que el orquestador los agregue a 06; los que resuelve Claude, con el agente responsable.

## 06 Preguntas de investigación.md

Encabezado estándar y una tabla (formato fijo; lo leen `estado.py` y `legajo.py`):

```markdown
| Q## | Pregunta al consumidor | Resuelve | Poseedor | Estado | Respuesta / evidencia |
|---|---|---|---|---|---|
| Q01 | ¿Tienes el aviso del cambio de tasa (correo, SMS, carta)? | H04, B02 | Proveedor | Sin respuesta | El usuario no recuerda haberlo recibido; no hay registro en el correo |
```
Poseedor: Consumidor · Proveedor · Tercero · Pública. Estado: Pendiente · Respondida (E##) · Afirmada · Sin respuesta · Descartada.
Al final, **como listas y nunca como tabla** (para que los scripts lean una sola fila por Q##): **Trasladables al proveedor** (`- Q01 → S01`) y **Por otra vía** (`- Q03 → consulta RUC en SUNAT`).

## 07 Estrategia y petitorio.md

```markdown
## Palanca
carga de la prueba en el proveedor / falla operativa propia / contradicción documental / deber de informar / ninguna (→ caso reencuadrado a información)

## Requerimientos al proveedor
S01 | Q01, H04 | Requiero la constancia de la comunicación previa del incremento de la tasa aplicado desde el EECC de junio de 2026 (fecha, medio y contenido), de forma que se verifique que se informó con la anticipación exigible.
<!-- Si no queda nada que requerir: sustituir las filas S## por la línea  sin_requerimientos: <motivo> -->

## Pretensión
forma: condicionada        <!-- directa | condicionada -->
P01 | De no acreditarse lo requerido, solicito el extorno de S/ 123,45 cobrados en exceso y de los cargos derivados, y la corrección de mi reporte en las centrales de riesgo.

## Piso preliminar para el Paso 2
Lo mínimo aceptable y por qué (se confirma con el usuario en 09).

## Qué ganamos con cada respuesta posible
Entrega → … · No entrega → … · Entrega algo que no cuadra → …
```
Validar con `scripts/validar_requerimientos.py "07 Estrategia y petitorio.md"`.

## 08 Análisis de respuesta.md (carpeta del Paso 1)

```markdown
| S## | Resultado | Registro | Cita o sustento |
|---|---|---|---|
| S01 | Omitido | O01 | La carta no menciona el aviso previo [E09 p.1] |
```
Resultado: Atendido · Parcial · Genérico · Omitido · Negado sin sustento · Negado con sustento · Contradice.
Luego, listas en formato `ID | S## | texto | fuente`: **Admisiones** (A##, cita literal), **Contradicciones** (C##), **Omisiones** (O##). Cierra con dos líneas que lee `estado.py` y la decisión propuesta:
```
clasificacion: parcial        <!-- favorable | oferta | parcial | desfavorable | desfavorable fundada | sin respuesta -->
en_plazo: si                  <!-- si | no (N días de demora) | sin respuesta -->
fecha_respuesta: DD/MM/AAAA   <!-- vacío si no respondió -->
```

## 09 Plan de audiencia.md (carpeta del Paso 2)

Primera línea: `fecha_audiencia: DD/MM/AAAA` (la lee `estado.py`). Luego: piso aceptable (confirmado por el usuario), alternativa si no hay acuerdo (tiempo y costo de seguir), 3 argumentos apoyados en A##/C##/O##, objeciones previsibles del proveedor (ver `perfiles-por-tipo.md`) con su réplica, y tabla de evaluación de ofertas (oferta · qué se gana · a qué se renuncia · valor esperado de seguir).

## 10 Legajo habilitante.md

Lo genera `scripts/legajo.py` desde los archivos anteriores (sin redacción nueva): cronología probada, admisiones, contradicciones, omisiones, trazabilidad de requerimientos y pretensiones por paso, plazos y brechas abiertas. Es el insumo de una eventual denuncia, que el plugin no redacta.
