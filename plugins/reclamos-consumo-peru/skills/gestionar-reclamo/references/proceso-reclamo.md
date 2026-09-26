# El proceso del reclamo de consumo: Paso 0 → Paso 1 → Paso 2

## 1. Alcance

Una controversia de consumo tiene tres instancias. Este plugin cubre las dos primeras, más la preparación previa:

| Paso | Instancia | Analogía | Skill | Resultado |
|---|---|---|---|---|
| **0** | Preparación y análisis de viabilidad | Estudio del caso | `paso-0-preparar-caso` | Expediente: hechos, evidencias, viabilidad y pretensión reencuadrada |
| **1** | Reclamo directo al proveedor | Trato directo | `paso-1-reclamo-proveedor` | Hoja de reclamación o reclamo SBS presentado, constancia, respuesta evaluada |
| **2** | Reclamo en Reclama Virtual (SAC INDECOPI) | Conciliación previa | `paso-2-reclama-virtual` + `paso-2-formulario` | Reclamo registrado en INDECOPI, seguimiento del acuerdo |
| 3 | Denuncia administrativa | "Juicio" | **Fuera del plugin** | — |

La denuncia administrativa **no forma parte del plugin**: no se redacta y no se recomiendan pretensiones para ella. Pero los Pasos 0 a 2 se diseñan para **habilitarla**: cada paso busca la solución y, si no llega, deja prueba útil (información obtenida, admisiones, contradicciones y omisiones del proveedor). Cuando el Paso 2 termina sin acuerdo, o el proveedor incumple lo acordado, el plugin compila el **legajo habilitante** (`10 Legajo habilitante.md`, con `scripts/legajo.py`), informa que el siguiente escalón existe y cierra su ciclo.

### Principio: ganar o documentar

| Paso | Cómo se saca el mayor provecho |
|---|---|
| 0 | Reorientar el petitorio para que sea viable. Formular las preguntas de investigación (06) y responderlas con el consumidor; solo lo que queda sin respuesta y está en poder del proveedor pasa a ser requerimiento (07). Ver `<raíz>/skills/paso-0-preparar-caso/references/guia-preguntas-requerimientos.md` |
| 1 | Requerimientos precisos y concisos (máx. 4) + pretensión directa o condicionada. El proveedor entrega (información nueva), no entrega (no acreditó lo que le tocaba) o entrega algo que no cuadra (contradicción). Todo queda registrado en 08 |
| 2 | Obtener la pretensión: la denuncia es larga y costosa. La ficha se apoya en A##/C##/O##; la audiencia se prepara (09) y no se falta |

Aunque la ley permite denunciar sin pasos previos, el plugin sigue el orden 0 → 1 → 2. Un caso en el que consta la negativa del proveedor a solucionar el problema, primero en trato directo y luego en conciliación, es más sólido y más fácil de resolver.

## 2. Compuertas entre pasos

| Transición | Condición para avanzar | Si no se cumple |
|---|---|---|
| Inicio → Paso 0 | Hay relato y proveedor identificado | Pedir el relato en una sola pregunta |
| Paso 0 → Paso 1 | Dictamen **Procede** o **Procede con reencuadre**; decisión del usuario sobre el petitorio registrada (`petitorio_aceptado` true u "original"); 00, 04, 05, 06 y 07 presentes; 06 sin preguntas en estado Pendiente; 07 con requerimientos válidos (`validar_requerimientos.py` sin errores) y pretensión definida. Lo verifica `estado.py compuerta 0-1` | Si el dictamen es "No procede ante INDECOPI", orientar a la entidad competente. Si es "Información insuficiente", resolver los pendientes |
| Paso 1 → Paso 2 | Reclamo presentado con constancia (código, fecha y hora), `08 Análisis de respuesta.md` escrito, **y** una de estas situaciones: (a) respuesta desfavorable o parcial, (b) respuesta sin fundamento o que no atiende lo pedido, (c) sin respuesta al vencer el plazo (15 días hábiles), (d) oferta rechazada por el usuario. No se eleva si la clasificación es `favorable` o `desfavorable fundada` | Esperar el plazo; hacer seguimiento; si la negativa está fundada, proponer el cierre |
| Paso 1 → Cierre | El proveedor soluciona, o el usuario acepta su oferta ("Acuerdo aceptado para solucionar el reclamo") | Registrar el acuerdo literal y su plazo de cumplimiento. Si luego lo incumple, el siguiente paso es una denuncia: fuera del plugin |
| Paso 2 → Cierre | Acuerdo en Reclama Virtual (registrar literal) o reclamo concluido sin acuerdo | Con acuerdo: verificar el cumplimiento. Sin acuerdo o incumplido: generar `10 Legajo habilitante.md` e informar el cierre del ciclo del plugin |
| Cerrado → Reapertura | Solo con un **hecho nuevo** o un **pedido distinto y proporcional** (p. ej., "reclamo en segunda instancia" que ofrezca el proveedor, nueva respuesta, nuevo cargo). Se reabre en el Paso 1; un nuevo Paso 2 solo si ese Paso 1 genera un hecho nuevo | Repetir el mismo pedido en otro Reclama Virtual puede tratarse como reiteración: no recomendarlo |

**Excepciones**:
- **Llamadas o mensajes publicitarios no autorizados**: Reclama Virtual tiene una categoría propia que no exige reclamo previo. Aun así, se recomienda como Paso 1 pedir el cese al proveedor (hoja de reclamación o su canal de datos personales). El usuario puede pasar directo al Paso 2: registrar `excepcion: "llamadas"`.
- **Urgencia o plazo de prescripción cercano** (menos de 90 días): el usuario puede decidir pasar al Paso 2 sin esperar el plazo del Paso 1. Advertir que el caso queda más débil, dejar constancia de su decisión y registrar `excepcion: "urgencia"` (la compuerta exige al menos la constancia del reclamo al proveedor).

**Casos antiguos** (con pasos ejecutados antes del plugin): el Paso 0 se corre en **modo retrospectivo**. Evalúa si el caso tenía base y si los pedidos de cada paso fueron proporcionales, registra el resultado real de cada paso y propone solo las reaperturas que admite esta tabla.

## 3. Estado del caso (archivo compartido por todos los pasos)

Ubicación: `r#_<proveedor>_<tema>/r#_<proveedor>_expediente/Estado del caso.md`. Cada skill lo lee al empezar y lo actualiza al terminar.

```markdown
# Estado del caso r<N> — <Proveedor>
Actualizado: DD/MM/AAAA · por: <skill>

| Campo | Valor |
|---|---|
| Paso actual | 0 Preparación · 1 Reclamo al proveedor · 2 Reclama Virtual · Cerrado |
| Situación | p. ej. "Esperando respuesta del proveedor" |
| Dictamen de viabilidad | Procede / Procede con reencuadre / No procede ante INDECOPI / Información insuficiente |
| Petitorio aceptado por el usuario | Sí (DD/MM/AAAA) / Mantiene su pedido original / No |
| Excepción | Ninguna / llamadas / urgencia |
| Requerimientos y pretensión (Paso 1) | S## (n.º) · pretensión directa/condicionada (ver 07) |
| Resultado de los requerimientos | atendidos / omitidos / genéricos (ver 08) · A## · C## · O## |
| Reclamo al proveedor | Canal · código · fecha y hora · constancia (ruta) |
| Plazo de respuesta del proveedor | vence DD/MM/AAAA (15 días hábiles) |
| Respuesta del proveedor | DD/MM/AAAA · favorable / oferta / parcial / desfavorable / sin respuesta · ruta (08) |
| Oferta del proveedor | texto literal · fecha · aceptada o rechazada |
| Reclamo en Reclama Virtual | ID · fecha · categoría · oficina |
| Resultado en INDECOPI | acuerdo (texto literal, plazo) / sin acuerdo / en trámite |
| Próxima acción | qué, quién, fecha |
| Fecha límite de prescripción | DD/MM/AAAA |

## Bitácora
- DD/MM/AAAA — evento (skill)
```

## 4. Estructura de la carpeta del caso

```
<carpeta de casos>/r<N>_<proveedor>_<tema>/
  r<N>_<proveedor>_expediente/          Paso 0: 00–07, Estado del caso.md, caso.json, evidencias-en-bruto/; al cierre, 10 Legajo
  r<N>_<proveedor>_reclamo-proveedor/   Paso 1: borrador del reclamo, constancia, respuesta, 08 Análisis de respuesta
  r<N>_<proveedor>_conciliacion-indecopi/  Paso 2: ficha de Reclama Virtual, cargo, traslado, 09 Plan de audiencia, acta
```
Si hay otras carpetas (p. ej., una denuncia del propio usuario), no se tocan.

## 5. Hilo conductor: coherencia entre pasos

- **Una sola historia**: los hechos del Paso 1 y del Paso 2 salen de la misma cronología (02). En el Paso 2 se agrega lo que pasó en el Paso 1 (reclamo, respuesta, oferta).
- **Requerimientos que se depuran**: en el Paso 2 se repiten solo los S## no atendidos; lo entregado ya es evidencia.
- **Un solo pedido, que se ajusta sin inflarse**: el pedido del Paso 2 parte del pedido del Paso 1. Puede precisarse a la luz de la respuesta (lo que el proveedor ya concedió se retira; lo que omitió explicar se pide). No se agregan pretensiones nuevas sin hechos nuevos.
- **La respuesta del proveedor es prueba**: en el Paso 2 se cita qué respondió, cuándo y por qué es insuficiente (o que no respondió dentro de los 15 días hábiles).
- **Los IDs se mantienen**: E## y H## del expediente se usan en todos los pasos.

## 6. Estado legible por el plugin (`caso.json`)

Junto al `Estado del caso.md` (para el usuario) vive `caso.json` (para el plugin). Lo crea y mantiene `scripts/estado.py`:

```
python3 estado.py init   <carpeta_expediente> --caso r1 --proveedor "Proveedor Ejemplo S.A.C."
python3 estado.py set    <carpeta_expediente> paso 1
python3 estado.py sync   <carpeta_expediente>          # relee 00, 06, 07, 08, 08b y 09; reinicia y actualiza Q/S/P/A/C/O
python3 estado.py compuerta <carpeta_expediente> 0-1   # 0-1 | 1-2 | cierre ; código 1 si no se cumple, 2 si la entrada es inválida
python3 estado.py ver    <carpeta_expediente>
```
Cada skill llama a `sync` al terminar y a `compuerta` antes de avanzar. Si la compuerta falla, el script lista lo que falta.

`estado.py` acepta la carpeta del caso o la del expediente.

Datos que se registran con `set` (no están en los archivos):
- `petitorio_aceptado` (true · "original" · false) al final del Paso 0, siempre.
- `excepcion` ("llamadas" · "urgencia") cuando el Paso 2 procede sin el recorrido normal del Paso 1.
- `reclamo` (canal, código, fecha, vence) y `paso` 1 al presentar el Paso 1.
- `oferta_rechazada` (true) si el usuario rechaza una oferta del proveedor.
- `rv` (id, fecha, categoría, oficina) y `paso` 2 al presentar el Paso 2; `piso` antes de la audiencia.
- `resultado` (acuerdo · sin acuerdo · incumplido) y `paso` "cerrado" al cerrar.
- `situacion` (texto breve y opcional, p. ej. "Esperando respuesta del proveedor" o "No procede ante INDECOPI: derivado a SUSALUD").

Datos que `sync` lee de los archivos: dictamen y fecha límite de prescripción (00); preguntas (06); requerimientos, pretensión, palanca y `sin_requerimientos` (07); `clasificacion:` (favorable · oferta · parcial · desfavorable · desfavorable fundada · sin respuesta), `en_plazo:` y `fecha_respuesta:` (08); `fecha_audiencia:` (09); admisiones, contradicciones y omisiones (08 y 08b).

## 7. Puntos de decisión del usuario

1. Aceptar el reencuadre y el petitorio (fin del Paso 0).
2. Enviar el reclamo al proveedor: el plugin llena el formulario y se detiene; el usuario pulsa el botón de envío.
3. Enviar en Reclama Virtual: el plugin llena y verifica el resumen; el usuario pulsa "ENVIAR RECLAMO".
4. Fijar el piso, responder ofertas y aprobar cualquier correo a INDECOPI o al proveedor.
