# Cambios

## 0.6.1 — 26/09/2026
- `estado.py` ya no lanza un proceso hijo con una copia de las variables de entorno para validar los requerimientos: importa `validar_requerimientos.py` y lo ejecuta en el mismo proceso. Ningún script lee variables de entorno ni credenciales.
- Icono del plugin (`.claude-plugin/icon.svg`).
- `privacyPolicyUrl` en `plugin.json` y enlace "Privacy" en el README.

## 0.6.0 — 25/09/2026 (primera versión pública)

### Cambios de nombre y estructura
- El plugin pasa a llamarse `reclamos-consumo-peru`, con aviso de no afiliación a INDECOPI.
- Las 5 skills de formulario (`reclama-virtual-bancario`, `-transporte`, `-colegios`, `-otros`, `-llamadas`) se fusionan en `paso-2-formulario`. Los campos por categoría pasan a `formulario-por-categoria.md`.
- Referencias renombradas: `lecciones-casos-reales.md` → `lecciones-practicas.md` y `perfiles-proveedor.md` → `perfiles-por-tipo.md`, ambas anonimizadas y sin marcas. El conocimiento propio del usuario puede guardarse en `<carpeta de casos>/_conocimiento-propio/`.

### Comportamiento
- **El plugin ya no pulsa botones de envío.** Llena el formulario del proveedor y el de Reclama Virtual, muestra el texto literal y el usuario envía.
- El usuario debe aceptar el petitorio siempre (`petitorio_aceptado`), también cuando el dictamen es "Procede", y el archivo de auditoría 05 pasa a ser obligatorio.
- Excepciones del Paso 2 registrables (`excepcion: llamadas | urgencia`).
- Nueva clasificación `desfavorable fundada`: propone el cierre y no deja elevar el caso.
- Nuevas líneas `fecha_respuesta:` (08) y `fecha_audiencia:` (09).
- Conectores opcionales. La carpeta de casos se pregunta al usuario.
- Discapacidad y documento de identidad: no se asumen ni se guardan salvo que el usuario lo pida.
- Se elimina el método alternativo de subida de adjuntos. El plugin no interactúa con captchas.
- Nunca se reformula un texto para pasar el filtro de competencia del portal.

### Correcciones
- Los frontmatter YAML de los 8 subagentes ya parsean. Antes cargaban sin descripción.
- Las rutas a scripts y referencias se escriben con `${CLAUDE_PLUGIN_ROOT}`.
- `legajo.py` solo marca como probados los hechos con Estado "Acreditado" o "Indiciario".
- `estado.py`:
  - reinicia los datos en cada `sync`;
  - acepta la carpeta del caso;
  - valida valores;
  - muestra un mensaje claro si `caso.json` está dañado.
- `validar_requerimientos.py`:
  - revisa toda la SOLICITUD;
  - protege abreviaturas y límites de palabra;
  - acepta ítems en varias líneas y el tipo `reclamo-sin`;
  - omite la validación en la categoría llamadas.
- `validar_ficha.py`:
  - detecta los marcadores de la plantilla;
  - avisa si hay IDs internos en el texto;
  - resuelve rutas relativas de adjuntos;
  - funciona en consolas de Windows.
- `plazos.py`:
  - valida los argumentos;
  - aplica el feriado del 7 de junio desde 2023;
  - agrega la opción `--no-laborables`.
- Precisiones jurídicas:
  - canales mínimos de reclamos de la SBS (art. 8.1);
  - competencia de OSIPTEL en contratación no solicitada;
  - seguros de salud → SUSALUD y CECONAR;
  - la Res. 101-2026/PS0-INDECOPI-SAM se presenta como criterio de primera instancia.

### Documentación
- README con qué lee, ejecuta y envía el plugin, ejemplos, requisitos, solución de problemas y limitaciones. Nuevos PRIVACY.md y LICENSE (MIT).

## 0.5.0 — 25/09/2026 (uso interno)
- Preguntas de investigación respondidas con el consumidor y requerimientos al proveedor. Estado en `caso.json`, compuertas y legajo habilitante.
