# Reclamos de consumo Perú

Plugin para Claude (Cowork, chat y Claude Code) que acompaña a un consumidor peruano en un reclamo de consumo, de principio a fin:

1. **Prepara el caso.** Ordena las evidencias y los hechos, evalúa si el reclamo tiene base y ajusta el pedido para que sea proporcional.
2. **Reclama al proveedor.** Redacta el reclamo para el Libro de Reclamaciones o el canal de reclamos de la SBS, con requerimientos precisos y una pretensión clara.
3. **Eleva el caso a Reclama Virtual de INDECOPI** si el proveedor no lo soluciona. Llena el formulario y se detiene en el resumen para que tú lo revises y lo envíes.

> **Aviso.** Reclama Virtual es un servicio de INDECOPI. Este plugin no está afiliado a INDECOPI ni respaldado por esa entidad, ni por ningún proveedor mencionado. **No brinda asesoría legal**: organiza la información para que tú decidas. En casos de monto alto, salud o controversias complejas, consulta con un abogado.

*English summary: A Claude plugin that helps consumers in Peru prepare consumer complaints, draft the complaint to the provider (Libro de Reclamaciones / SBS channel) with precise document requests, and fill INDECOPI's "Reclama Virtual" form up to the summary screen so the user reviews and submits it. It keeps case files in a folder the user chooses, runs local Python scripts (no network), never submits forms or emails on its own, and does not provide legal advice. Not affiliated with INDECOPI. Content is in Spanish.*

## Cómo funciona

El trabajo sigue el principio **"ganar o documentar"**. Cada paso busca la solución, y si no la consigue, deja pruebas útiles para el siguiente.

| Paso | Qué hace | Skill |
|---|---|---|
| Entrada | Ubica el caso, lee su estado, verifica si puede pasar al siguiente paso y te dice qué sigue | `gestionar-reclamo` |
| **0. Preparación** | Evidencias, cronología, matriz hecho-prueba y viabilidad. Luego formula **preguntas para ti**; lo que no puedas responder ni probar, y esté en poder del proveedor, se convierte en **requerimiento** para el proveedor | `paso-0-preparar-caso` |
| **1. Reclamo al proveedor** | Hasta 4 requerimientos ("Requiero …, de forma que se verifique …") más la pretensión. Llena el formulario y se detiene: **envías tú**. Luego analiza la respuesta requerimiento por requerimiento | `paso-1-reclamo-proveedor` |
| **2. Reclama Virtual** | Arma la ficha con lo que el proveedor admitió, contradijo o no acreditó, llena el portal hasta el resumen (**envías tú**) y prepara la audiencia de conciliación | `paso-2-reclama-virtual`, `paso-2-formulario` |
| Cierre | Si no hay acuerdo, compila un **legajo** con los hechos probados y las respuestas del proveedor. Este plugin no redacta denuncias administrativas | `legajo.py` |

Subagentes: `investigador-evidencias`, `reconstructor-hechos`, `correlacionador-prueba`, `analista-viabilidad`, `estratega-petitorio`, `auditor-expediente`, `analista-respuesta` y `preparador-audiencia`.

### Ejemplos de uso

- "Quiero reclamar al banco por un consumo de S/ 200 que no reconozco en mi tarjeta."
- "La aerolínea perdió mi equipaje en un vuelo Lima–Cusco; ayúdame a preparar el reclamo."
- "Me siguen llamando para ofrecerme un plan de telefonía aunque pedí que no me llamen."
- "¿En qué va mi caso r3?", o "El proveedor ya respondió mi reclamo, ¿qué sigue?"
- "Tengo audiencia de conciliación en Reclama Virtual la próxima semana; prepárame."

## Qué lee, qué ejecuta y qué envía

**Lee:**
- La carpeta de casos que tú indiques. Cada caso vive en `r<N>_<proveedor>_<tema>/`.
- Solo si los conectaste, y solo para buscar lo relacionado con el caso (nombre del proveedor, códigos de reclamo, INDECOPI):
  - tu correo, incluida la papelera (restaura un correo solo con tu aprobación);
  - tu almacenamiento en la nube;
  - tu gestor de tareas.
- Páginas públicas, como la consulta de RUC o la web del proveedor, para ubicar su canal oficial de reclamos.

**Escribe:** archivos Markdown y `caso.json` dentro de la carpeta del caso. Crea borradores de correo, tareas o eventos solo avisándote.

**Ejecuta:** scripts de Python 3 incluidos en el plugin (`estado.py`, `plazos.py`, `legajo.py`, `validar_requerimientos.py`, `validar_ficha.py`).
- No usan red, no leen credenciales y solo escriben dentro de la carpeta del caso.
- En el portal de INDECOPI y en el formulario del proveedor, el navegador ejecuta funciones de ayuda en JavaScript solo para llenar los campos.

**Envía, siempre con tu intervención:**
- **Al proveedor**: el texto del reclamo, que tú envías con su formulario.
- **A INDECOPI (Reclama Virtual)**: tus datos, los del proveedor, el motivo, la solicitud y los adjuntos. El portal transmite cada adjunto en cuanto se selecciona, así que el plugin te confirma la lista antes de subirlos. El reclamo lo envías tú.
- **Al modelo de Claude**: el contenido que procesa en la conversación, según las condiciones de tu cuenta.

**Nunca:** envía reclamos ni correos por su cuenta, ingresa contraseñas, resuelve captchas, descarga archivos sin tu permiso ni guarda en memoria tu DNI o tus números de cuenta o tarjeta.

Detalles en la [política de privacidad (Privacy)](https://github.com/ByronArriolaO/reclamos-consumo-peru/blob/main/plugins/reclamos-consumo-peru/PRIVACY.md).

## Requisitos

- Claude con soporte de plugins (Cowork, Claude Code o chat). Algunas funciones requieren subagentes y un navegador.
- **Navegador**: el integrado de Claude o Claude in Chrome. Con Claude in Chrome, el plugin puede subir los adjuntos; con el integrado, los eliges tú.
- **Python 3** en el entorno donde corre Claude (sin dependencias externas).
- **Opcional**: correo, almacenamiento en la nube y gestor de tareas conectados. Sin correo, guarda en la carpeta del caso las respuestas y notificaciones que recibas.

## Conocimiento propio (opcional y privado)

Puedes guardar tus propias lecciones y perfiles de proveedores en `<carpeta de casos>/_conocimiento-propio/`, por ejemplo `lecciones-propias.md` o `perfiles-propios.md`. El plugin los lee si existen y les da prioridad sobre las referencias generales. Esos archivos quedan en tu carpeta y nunca forman parte del plugin.

## Solución de problemas

| Síntoma | Qué hacer |
|---|---|
| El plugin dice que no puede pasar de paso | Revisa lo que lista `estado.py compuerta`: suele faltar tu decisión sobre el petitorio, una pregunta sin responder o la constancia del reclamo |
| El portal de Reclama Virtual se ve distinto | El portal cambió. El plugin se detiene y describe la diferencia; avísale para continuar paso a paso |
| El portal bloquea el texto | Hay una palabra que el portal no acepta. El plugin propone una redacción equivalente. Si el bloqueo indica que el tema es de otra entidad (OSIPTEL, OSINERGMIN, SUNASS, SUSALUD), corresponde acudir a esa entidad |
| No se pueden subir los adjuntos | Con el navegador integrado, elige tú el archivo en "Cargar archivo". Revisa que pese menos de 5,25 MB y que su nombre no se repita |
| Los scripts no encuentran los archivos | Si la carpeta está en tu equipo y Claude trabaja en la nube, el plugin copia los archivos a la sesión y los devuelve. Confirma que la carpeta del caso esté conectada |

## Limitaciones

- La mecánica del portal y la lista de palabras bloqueadas se relevaron del comportamiento observable de Reclama Virtual el 23/09/2026 y pueden cambiar.
- Las referencias normativas (Ley 29571, Reglamento del Libro de Reclamaciones, Res. SBS 04036-2022) se revisaron en septiembre de 2026. Antes de citarlas, confirma que sigan vigentes.
- El cómputo de plazos usa los feriados nacionales del Perú. Los días no laborables del sector público se agregan con una opción y deben actualizarse cada año.
- No cubre la denuncia administrativa ni el arbitraje de consumo.

## Estructura

```
.claude-plugin/plugin.json
skills/
  gestionar-reclamo/        orquestador; referencias de proceso, lecciones, palancas y perfiles; scripts estado, plazos y legajo
  paso-0-preparar-caso/     expediente, preguntas y requerimientos; validar_requerimientos.py
  paso-1-reclamo-proveedor/ guía y plantilla del reclamo al proveedor
  paso-2-reclama-virtual/   ficha, mecánica del portal, catálogos; validar_ficha.py
  paso-2-formulario/        llenado del portal por categoría
agents/                     8 subagentes
```

## Licencia, privacidad y contacto

Licencia [MIT](LICENSE). [Privacy](https://github.com/ByronArriolaO/reclamos-consumo-peru/blob/main/plugins/reclamos-consumo-peru/PRIVACY.md): política de privacidad. Reporta problemas o sugerencias en GitHub Issues: https://github.com/ByronArriolaO/reclamos-consumo-peru/issues
