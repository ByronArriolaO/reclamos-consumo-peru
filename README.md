# reclamos-consumo-peru

Repositorio del plugin **Reclamos de consumo Perú** para Claude. Prepara reclamos de consumo, redacta el reclamo al proveedor con requerimientos precisos y llena el formulario de Reclama Virtual (INDECOPI) hasta el resumen, para que el usuario lo revise y lo envíe. No afiliado a INDECOPI; no brinda asesoría legal.

*English: Marketplace repository for a Claude plugin that helps consumers in Peru prepare and file consumer complaints (provider complaint book / SBS channel and INDECOPI's Reclama Virtual, stopping at the summary so the user submits). Spanish content. MIT license.*

- Plugin: [`plugins/reclamos-consumo-peru`](plugins/reclamos-consumo-peru/README.md): qué hace, qué lee, qué envía, requisitos y ejemplos.
- Privacidad: [`PRIVACY.md`](plugins/reclamos-consumo-peru/PRIVACY.md)
- Cambios: [`CHANGELOG.md`](plugins/reclamos-consumo-peru/CHANGELOG.md)

## Instalación como marketplace

En Claude (Cowork): **Customize → Plugins → Add marketplace**, ingresa `ByronArriolaO/reclamos-consumo-peru` e instala **reclamos-consumo-peru**.

En Claude Code:

```
/plugin marketplace add ByronArriolaO/reclamos-consumo-peru
/plugin install reclamos-consumo-peru@byronarriolao-plugins
```

## Desarrollo

- Pruebas de los scripts: `python3 tests/run_tests.py` (usan solo un caso ficticio en `tests/fixtures/`).
- Validación del plugin: `claude plugin validate ./plugins/reclamos-consumo-peru`.
- Antes de cada versión, sube `version` en `plugins/reclamos-consumo-peru/.claude-plugin/plugin.json` y en `.claude-plugin/marketplace.json`, y registra los cambios en el `CHANGELOG.md`.
- Nunca subas expedientes reales: el `.gitignore` excluye las carpetas de casos, los PDF y `_conocimiento-propio/`.

Licencia [MIT](LICENSE).
