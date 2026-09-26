---
name: paso-2-reclama-virtual
description: Paso 2 del reclamo de consumo (Perú). Arma y valida la ficha para Reclama Virtual de INDECOPI a partir del expediente y de la respuesta del proveedor, deriva el llenado a paso-2-formulario, registra el reclamo, prepara la audiencia de conciliación y cierra el caso con el legajo. Invocada por gestionar-reclamo cuando el proveedor no solucionó en el Paso 1 o cuando hay una excepción registrada; no usar para casos sin expediente.
---

# Paso 2 — Reclama Virtual (conciliación previa)

Flujo: compuerta → categoría → ficha (desde el expediente y 08) → validar → `paso-2-formulario` (llena y se detiene en el resumen; envía el usuario) → registro y seguimiento → audiencia → cierre.

> Reclama Virtual es un servicio de INDECOPI. Este plugin no está afiliado ni respaldado por INDECOPI.

Referencias (en `${CLAUDE_PLUGIN_ROOT}/skills/paso-2-reclama-virtual/references/`):
- `instructivo-categorias.md` — opciones del portal y competencia.
- `requerimientos-informacion.md` — datos por caso, checklist y redacción compatible con el filtro del portal.
- `plantilla-ficha.md` — formato de la ficha. `formulario-por-categoria.md` — campos de cada categoría.
- `portal-mecanica.md`, `catalogos.json`, `palabras-bloqueadas.json`.

Otras: `${CLAUDE_PLUGIN_ROOT}/skills/gestionar-reclamo/references/proceso-reclamo.md` (compuertas y estado), `catalogo-palancas.md`, `perfiles-por-tipo.md`, `lecciones-practicas.md` (misma carpeta), y `${CLAUDE_PLUGIN_ROOT}/skills/paso-0-preparar-caso/references/guia-preguntas-requerimientos.md` §5.

Scripts: `${CLAUDE_PLUGIN_ROOT}/skills/paso-2-reclama-virtual/scripts/validar_ficha.py`, `${CLAUDE_PLUGIN_ROOT}/skills/paso-0-preparar-caso/scripts/validar_requerimientos.py`, `${CLAUDE_PLUGIN_ROOT}/skills/gestionar-reclamo/scripts/estado.py`, `legajo.py` y `plazos.py` (misma carpeta que `estado.py`). Aplicar la regla de archivos de `gestionar-reclamo` §0.3 antes de ejecutarlos.

Subagentes: `analista-respuesta` (respuesta al traslado) y `preparador-audiencia` (plan de audiencia).

## 1. Compuerta de entrada
1. `python3 "${CLAUDE_PLUGIN_ROOT}/skills/gestionar-reclamo/scripts/estado.py" compuerta <carpeta_expediente> 1-2`. Requiere reclamo al proveedor con constancia y `08 Análisis de respuesta.md` (si no existe, ejecutar el modo C de `paso-1-reclamo-proveedor`), salvo excepción registrada (`excepcion: llamadas` o `urgencia`).
2. Si hay correo conectado, buscar (incluida la papelera) si ya existe un reclamo en INDECOPI contra el mismo proveedor por el mismo tema. Si existe, **no presentar otro**: registrar su resultado y aplicar el cierre o la reapertura de `proceso-reclamo.md` §2.
3. Si no hay expediente, volver a `paso-0-preparar-caso` (modo ligero si el caso es simple).

## 2. Categoría
Según `instructivo-categorias.md` §1 y el 00 Expediente: `bancario` (banco, financiera, caja + producto financiero) · `transporte` · `colegios` (colegio particular) · `llamadas` (publicidad no autorizada) · `otros` (todo lo demás, verificando antes la competencia: si la materia es de OSIPTEL, OSINERGMIN, SUNASS o SUSALUD, derivar y no presentar).

## 3. Armar la ficha (un solo hilo con el Paso 1)
1. Copiar `plantilla-ficha.md` a `r#_..._conciliacion-indecopi/Ficha Reclama Virtual - <Proveedor>.md`.
2. **Etapa 1**:
   - "¿Expusiste tu problema?" = Sí; medio = el canal del Paso 1.
   - Fecha del problema = fecha de la respuesta del proveedor o, si no respondió, fecha de vencimiento del plazo (salvo otra indicación del usuario).
   - Adjuntos (máx. 5): constancia del reclamo y respuesta del proveedor (tipo *Hoja de reclamación*) más las evidencias clave de 00. Confirmar la lista con el usuario: los archivos se transmiten a INDECOPI al seleccionarlos.
3. **MOTIVO** (≤ 4000; apuntar a ≤ 2000): hechos probados de 00 en orden narrativo y un bloque sobre el Paso 1 construido con 08: "El [fecha] presenté el reclamo N.º [código], en el que requerí [requerimientos en una línea]. El proveedor respondió el [fecha] / no respondió dentro de los 15 días hábiles." Luego, en frases cortas: lo que **admitió** (cita literal), lo que **contradice** sus propios documentos y lo que **no acreditó** ("no remitió la base contractual ni la demostración matemática requeridas"). Los IDs A##/C##/O## sirven para elegir el contenido; **no se transcriben** en la ficha.
4. Palancas del MOTIVO (`catalogo-palancas.md`): carga de la prueba, contradicción documental, falla operativa admitida.
5. **SOLICITUD** (≤ 3000; apuntar a ≤ 1000): (1) repetir **solo** los requerimientos no atendidos, con la misma redacción o más corta; (2) la pretensión pendiente, retirando lo ya concedido y **sin agregar pretensiones nuevas** si no hay hechos nuevos. Nada de preguntas.
6. **Llamadas**: sin MOTIVO ni SOLICITUD libres (textos fijos del portal). Registrar cada llamada y `cese_solicitado: si` si en el Paso 1 se pidió el cese.
7. Etapas 2 y 3: RUC del proveedor y datos del reclamante. El documento de identidad se pide al llenar y no se guarda en archivos ni en memoria, salvo que el usuario lo pida.
8. Lo que falte y solo sepa el usuario (oficina, contacto, anónimo en colegios, número de cuenta, discapacidad si desea indicarla): una sola ronda de preguntas.

## 4. Validar
1. `python3 "${CLAUDE_PLUGIN_ROOT}/skills/paso-2-reclama-virtual/scripts/validar_ficha.py" "<ficha>" --json` → 0 errores. Palabras bloqueadas: reformular con la tabla de `requerimientos-informacion.md` §4 solo el lenguaje sancionador en asuntos de INDECOPI; mostrar al usuario las frases cambiadas.
2. `python3 "${CLAUDE_PLUGIN_ROOT}/skills/paso-0-preparar-caso/scripts/validar_requerimientos.py" "<ficha>"` → 0 errores (revisa la SOLICITUD; en llamadas no aplica).

## 5. Llenar el formulario
Invocar `paso-2-formulario` con la ruta de la ficha. Esa skill recorre el portal, verifica el resumen, muestra al usuario el texto literal y **se detiene**: el usuario pulsa "ENVIAR RECLAMO".

## 6. Registro y seguimiento
1. Cuando el usuario confirme el envío, guardar `Cargo Reclama Virtual - <Proveedor>.md` en la carpeta de conciliación: fecha y hora, ID de reclamo, categoría, oficina, valores cargados, adjuntos. Sin el número de documento del reclamante.
2. Actualizar `Estado del caso.md` y el expediente (nuevo E## con el cargo; nuevo H##). Registrar: `python3 "${CLAUDE_PLUGIN_ROOT}/skills/gestionar-reclamo/scripts/estado.py" set <carpeta_expediente> rv '{"id":"…","fecha":"DD/MM/AAAA","categoria":"…","oficina":"…"}'` y `… set <carpeta_expediente> paso 2`.
3. Seguimiento: vigilar las comunicaciones de INDECOPI (correo conectado o archivos que guarde el usuario). Si hay un gestor de tareas conectado, crear una tarea de seguimiento avisando al usuario.
4. **Respuesta al traslado**: lanzar `analista-respuesta` con un bloque de contexto (rutas de la carpeta del caso, de `07`, `08`, `01`, `02`, de `plantilla-expediente.md` §08, `guia-reclamo-proveedor.md`, `perfiles-por-tipo.md` y `plazos.py`). Escribe `08b Análisis respuesta traslado.md` en la carpeta de conciliación, con A##/C##/O## en numeración continua.
5. **Sin respuesta al traslado**: preparar la respuesta a INDECOPI pidiendo la audiencia, dentro del plazo que indique (suele ser 2 días hábiles). Se envía solo con aprobación del usuario.
6. **Audiencia**: no se falta. Agendarla (tarea o evento, avisando al usuario); ante un impedimento, pedir la reprogramación antes de la fecha. Antes de la audiencia, lanzar `preparador-audiencia` con un bloque de contexto (rutas de `07`, `08`, `08b`, la ficha, la citación, `catalogo-palancas.md` y `perfiles-por-tipo.md`). Escribe `09 Plan de audiencia.md`. Confirmar el piso con el usuario (AskUserQuestion) y registrarlo: `… set <carpeta_expediente> piso '"<texto>"'`.
7. **Oferta del proveedor**: compararla con la SOLICITUD y con el valor esperado de seguir (probabilidad, tiempo y costo de la siguiente vía); explicar qué se gana y a qué se renuncia; decide el usuario. Una oferta rechazada puede no repetirse. Si hay acuerdo, registrarlo literal (texto, monto, plazo, medio) con su fecha de verificación.

## 7. Cierre
- **Con acuerdo**: `estado.py set … resultado '"acuerdo"'` y `… paso '"cerrado"'`; verificar el cumplimiento en la fecha pactada. Si luego incumple: `resultado '"incumplido"'` y generar el legajo.
- **Sin acuerdo o incumplido**: `resultado '"sin acuerdo"'` (o `"incumplido"`), `python3 "${CLAUDE_PLUGIN_ROOT}/skills/gestionar-reclamo/scripts/legajo.py" <carpeta_del_caso>` → `10 Legajo habilitante.md` (compila hechos, admisiones, contradicciones, omisiones, requerimientos, pretensiones y plazos; no redacta nada nuevo), `paso '"cerrado"'` y `compuerta … cierre`. Informar que el plugin terminó su ciclo y que el siguiente escalón (denuncia administrativa) está fuera de su alcance. No redactarla ni planificarla.

## Reglas
- El plugin no pulsa "ENVIAR RECLAMO": lo hace el usuario tras revisar el resumen.
- No descargar el PDF del cargo sin permiso. No inventar datos.
- Si el portal difiere de lo documentado, detenerse y describir la diferencia.
- Nunca reescribir un texto para pasar el filtro de competencia del portal: si la materia es de otra entidad, se deriva.
