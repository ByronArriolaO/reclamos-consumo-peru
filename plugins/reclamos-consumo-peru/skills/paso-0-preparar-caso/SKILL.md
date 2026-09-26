---
name: paso-0-preparar-caso
description: Paso 0 del reclamo de consumo (Perú). Arma el expediente del caso (evidencias, hechos, matriz hecho-prueba, viabilidad), formula las preguntas de investigación y las responde con el consumidor, y define el petitorio (requerimientos precisos al proveedor + pretensión proporcional). Invocada por gestionar-reclamo para casos nuevos o para actualizar un expediente.
---

# Paso 0 — Preparar el caso, investigar y diseñar el petitorio

Produce el **expediente** del caso, las **preguntas de investigación respondidas** y el **petitorio** (requerimientos + pretensión), que habilitan el Paso 1 (`paso-1-reclamo-proveedor`) y luego el Paso 2 (`paso-2-reclama-virtual`). No presenta nada ni contacta al proveedor. La denuncia administrativa está fuera del alcance, pero el expediente se arma para que, si llega a hacer falta, el legajo esté completo.

Regla central: **las preguntas se responden aquí, con el consumidor; al proveedor solo llegan requerimientos** (máx. 4, una oración cada uno).

Referencias:
- `${CLAUDE_PLUGIN_ROOT}/skills/paso-0-preparar-caso/references/guia-preguntas-requerimientos.md` — ciclo pregunta → consumidor → requerimiento, formato del requerimiento, pretensión directa o condicionada, banco por materia.
- `${CLAUDE_PLUGIN_ROOT}/skills/paso-0-preparar-caso/references/viabilidad-reencuadre.md` — test de viabilidad y de proporcionalidad, reencuadre, dictamen.
- `${CLAUDE_PLUGIN_ROOT}/skills/paso-0-preparar-caso/references/marco-controversia-consumo.md` — elementos del caso, deberes, competencia y prueba.
- `${CLAUDE_PLUGIN_ROOT}/skills/paso-0-preparar-caso/references/guia-evidencias.md` — fuentes, ficha de evidencia y checklists por materia.
- `${CLAUDE_PLUGIN_ROOT}/skills/paso-0-preparar-caso/references/plantilla-expediente.md` — archivos 00–10, IDs y formatos fijos (contrato de entrega).
- `${CLAUDE_PLUGIN_ROOT}/skills/gestionar-reclamo/references/proceso-reclamo.md` — pasos, compuertas, `Estado del caso.md` y `caso.json`.
- `${CLAUDE_PLUGIN_ROOT}/skills/gestionar-reclamo/references/lecciones-practicas.md`, `catalogo-palancas.md`, `perfiles-por-tipo.md`.
- Scripts: `${CLAUDE_PLUGIN_ROOT}/skills/gestionar-reclamo/scripts/plazos.py`, `${CLAUDE_PLUGIN_ROOT}/skills/gestionar-reclamo/scripts/estado.py`, `${CLAUDE_PLUGIN_ROOT}/skills/paso-0-preparar-caso/scripts/validar_requerimientos.py`.

Subagentes del plugin (`agents/`):

| Orden | Subagente | Produce |
|---|---|---|
| 1 | `investigador-evidencias` | 01 Registro de evidencias |
| 2 | `reconstructor-hechos` | 02 Cronología de hechos |
| 3a | `correlacionador-prueba` | 03 Matriz hecho-prueba y brechas B## |
| 3b | `analista-viabilidad` | 04 Viabilidad, palanca y pretensión P## |
| 4 | `estratega-petitorio` (modo A) | 06 Preguntas de investigación |
| — | esta skill, con el usuario | Respuestas en 06 |
| 5 | `estratega-petitorio` (modo B) | 07 Estrategia y petitorio (S## + P##) |
| 6 | `auditor-expediente` | 05 Auditoría y pendientes |
| — | esta skill | 00 Expediente, Estado del caso, caso.json |

Invocar cada subagente por su nombre (en algunos entornos con prefijo `reclamos-consumo-peru:`). Si no están disponibles, leer `${CLAUDE_PLUGIN_ROOT}/agents/<nombre>.md` y ejecutar sus instrucciones en un subagente genérico, o en línea.

**Modo ligero**: si el caso es simple (una sola conducta, 3 documentos o menos, monto bajo), ejecutar las fases en línea sin subagentes. Se mantienen igual 06 (puede tener 2–3 preguntas) y 07; el resto puede ir condensado en 00 + 04.

## Fase 0 — Recepción
1. Ubicar el caso (r# o proveedor) y leer o crear `Estado del caso.md`. Crear o leer `caso.json` **en la carpeta de trabajo** (ver punto 3; todo el Paso 0 usa esa carpeta como `<carpeta_trabajo>`): `python3 "${CLAUDE_PLUGIN_ROOT}/skills/gestionar-reclamo/scripts/estado.py" init <carpeta_trabajo> --caso r# --proveedor "<nombre>"` (no sobrescribe si ya existe; si el caso ya tiene `caso.json` en su carpeta de expediente, copiarlo primero a la carpeta de trabajo). Verificar la etapa real en el correo (`gestionar-reclamo` §1, pasos 3–5). Si ya existe un expediente, trabajar en **modo actualización** (conservar IDs; relanzar solo lo afectado). Si el caso ya pasó por los Pasos 1 o 2 antes del plugin, trabajar en **modo retrospectivo**.
2. Obtener el **relato y el pedido original del usuario**, con sus palabras. Si falta, pedirlo en una sola pregunta: qué pasó, cuándo, con qué proveedor y qué quiere lograr.
3. Preparar el espacio (regla de archivos de `gestionar-reclamo` §0.3): trabajar en el equipo del usuario si hay una terminal con Python 3; si no, copiar los archivos del caso a la sesión conservando la estructura `r#_<proveedor>_<tema>/r#_<proveedor>_expediente/`. Esa carpeta de expediente es `<carpeta_trabajo>`.
4. Bloque de contexto para los subagentes (rutas absolutas):
   - caso, proveedor, relato y pedido original, modo (normal, ligero, actualización, retrospectivo) y fuentes conectadas (correo, almacenamiento, gestor de tareas);
   - carpeta del caso y `<carpeta_trabajo>`;
   - referencias: `${CLAUDE_PLUGIN_ROOT}/skills/paso-0-preparar-caso/references/`, `${CLAUDE_PLUGIN_ROOT}/skills/gestionar-reclamo/references/`, `${CLAUDE_PLUGIN_ROOT}/skills/paso-1-reclamo-proveedor/references/` y `${CLAUDE_PLUGIN_ROOT}/skills/paso-2-reclama-virtual/references/palabras-bloqueadas.json`;
   - scripts: `${CLAUDE_PLUGIN_ROOT}/skills/gestionar-reclamo/scripts/plazos.py` y `${CLAUDE_PLUGIN_ROOT}/skills/paso-0-preparar-caso/scripts/validar_requerimientos.py`;
   - conocimiento propio del usuario, si existe (`<carpeta de casos>/_conocimiento-propio/`).

## Fase 1 — Evidencias → `investigador-evidencias`
## Fase 2 — Hechos → `reconstructor-hechos` (con 01; usar `plazos.py`)
## Fase 3 — En paralelo → `correlacionador-prueba` (01, 02) y `analista-viabilidad` (01, 02, relato y pedido original)
Si la matriz cambia la fortaleza de un hecho clave, pedir al analista que revise la palanca o la pretensión afectada.
**Chequeo de lecciones** (anotar en 04): competencia y proveedor correctos; pretensión de un tipo que suele ganar y que no exige cambiar una regla normada; al menos una palanca (si no, reencuadre a información); evidencia clave con fecha, hora y origen; todas las consecuencias incluidas.

## Fase 4 — Preguntas de investigación → `estratega-petitorio` modo A, luego el usuario
1. El estratega escribe 06 y responde lo que puede con las fuentes conectadas.
2. Presentar al usuario solo las preguntas pendientes. Una ronda: las 4 más importantes con AskUserQuestion (opciones concretas; "Otro" permite responder libremente) y el resto en una lista corta en el mismo mensaje. Pedir la prueba junto con la respuesta ("¿tienes captura o correo?") y la subcarpeta donde guardarla.
3. Registrar cada respuesta en 06 con su estado (Respondida (E##) · Afirmada · Sin respuesta · Descartada). Si llegó evidencia nueva, relanzar `investigador-evidencias` en modo actualización y los agentes afectados (02, 03).
4. Una segunda ronda solo si una respuesta abrió una pregunta crítica nueva. Si el usuario no está disponible, marcar las pendientes como "Sin respuesta" y dejarlo anotado.

## Fase 5 — Requerimientos y petitorio → `estratega-petitorio` modo B
El estratega escribe 07 (palanca, requerimientos S##, pretensión directa o condicionada, piso preliminar). Verificar: `python3 "${CLAUDE_PLUGIN_ROOT}/skills/paso-0-preparar-caso/scripts/validar_requerimientos.py" "<carpeta_trabajo>/07 Estrategia y petitorio.md"` → 0 errores. Si todas las preguntas se resolvieron con el consumidor y no queda nada que requerir, 07 lleva la línea `sin_requerimientos: <motivo>` (el validador la acepta y `estado.py sync` la registra).

## Fase 6 — Auditoría → `auditor-expediente`
Pendientes que puede resolver Claude: relanzar el agente responsable (máx. 2 ciclos) y volver a auditar esos puntos. Si el auditor propone preguntas nuevas para el usuario, agregarlas a 06 como Q## y volver a la Fase 4 solo por ellas.

## Fase 7 — Decisión del usuario sobre el petitorio
1. Presentar en pocas líneas: dictamen y fortaleza; pedido original → pedido reencuadrado (si aplica, según `viabilidad-reencuadre.md` §5); los requerimientos S## tal como irán al proveedor; la pretensión y su forma; qué se gana con cada respuesta posible.
2. Preguntar con AskUserQuestion: "Acepto el petitorio" / "Ajustarlo" / "Mantener mi pedido original (con el riesgo explicado)". Registrar la decisión en el estado y en `caso.json`:
   - Acepta → `python3 "${CLAUDE_PLUGIN_ROOT}/skills/gestionar-reclamo/scripts/estado.py" set <carpeta_trabajo> petitorio_aceptado true`.
   - Ajustarlo → incorporar los cambios (relanzar el estratega en modo B si tocan 07) y volver a preguntar.
   - Mantener el original → `… petitorio_aceptado '"original"'`, reescribir 07 con su pedido (pasando igual por el validador) y anotar la advertencia en la bitácora. La compuerta lo admite: el usuario decide. La decisión se registra siempre, haya o no reencuadre.
3. Si es **No procede ante INDECOPI**: explicar la entidad o vía correcta y cerrar el caso: `estado.py set <carpeta_trabajo> paso '"cerrado"'` y `… situacion '"No procede ante INDECOPI: derivado a <entidad>"'`.

## Fase 8 — Síntesis y compuerta
1. Registrar en 01 como E## las fuentes provisionales N## y actualizar las citas.
2. Escribir `00 Expediente - <Proveedor>.md` según la plantilla (incluye S## y P## del Paso 1).
3. `python3 "${CLAUDE_PLUGIN_ROOT}/skills/gestionar-reclamo/scripts/estado.py" sync <carpeta_trabajo>` y `python3 "${CLAUDE_PLUGIN_ROOT}/skills/gestionar-reclamo/scripts/estado.py" compuerta <carpeta_trabajo> 0-1`. Si falla, resolver lo que lista antes de ofrecer el Paso 1.

## Fase 9 — Entrega y paso siguiente
1. Copiar 00–07 y `caso.json` de la carpeta de trabajo a `r#_<proveedor>_expediente/` (si son la misma carpeta, no hace falta), sin sobrescribir documentos del usuario. Desde aquí, los Pasos 1 y 2 usan `caso.json` de la carpeta del expediente.
2. Actualizar `Estado del caso.md`: dictamen, aceptación, requerimientos y pretensión, prescripción, próxima acción y bitácora.
3. Informar: dictamen, petitorio final, pendientes y el siguiente paso. Si la compuerta 0 → 1 se cumple, ofrecer continuar con `paso-1-reclamo-proveedor`.

## Reglas
- Solo lectura sobre archivos, correo y cuentas del usuario. No contactar al proveedor.
- Nada se afirma sin fuente; lo inferido se marca como inferido.
- No negar el derecho a reclamar: reenfocarlo. El usuario decide.
- Al proveedor no se le hacen preguntas: requerimientos precisos y concisos (máx. 4).
- No guardar en memoria números de documento, cuenta ni tarjeta; en el expediente, enmascararlos.
- El análisis es un insumo técnico para que el usuario decida; en casos complejos (montos altos, salud, controversias colectivas) sugerir la revisión de un abogado.
