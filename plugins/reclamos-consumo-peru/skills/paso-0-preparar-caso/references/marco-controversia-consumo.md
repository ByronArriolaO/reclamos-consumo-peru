# Marco para preparar una controversia de consumo (Perú)

Base de conocimiento de los subagentes del Paso 0. El caso se prepara con rigor de expediente para dos instancias: el **reclamo directo al proveedor** (Paso 1) y el **reclamo en Reclama Virtual** (Paso 2). La denuncia administrativa está fuera del alcance del plugin.

> Fuentes: Ley 29571, Código de Protección y Defensa del Consumidor (texto consolidado con modificaciones de los D. Leg. 1308 y 1390); Ley 31435 (2022); D.S. 011-2011-PCM, Reglamento del Libro de Reclamaciones, y sus modificatorias (D.S. 006-2014-PCM, 058-2017-PCM, 101-2022-PCM); Res. SBS 04036-2022, Reglamento de Gestión de Reclamos y Requerimientos; D.S. 301-2025-EF (UIT 2026 = S/ 5 500). Revisado el 23/09/2026. Antes de citar una norma en un reclamo, confirmar que siga vigente (SPIJ: spij.minjus.gob.pe).

## 1. Lo que hay que poder demostrar (elementos del caso)

| # | Elemento | Pregunta que responde | Prueba típica |
|---|---|---|---|
| 1 | **Consumidor** | ¿El reclamante es destinatario final? (art. IV.1). También un microempresario con asimetría informativa respecto de productos ajenos a su giro (IV.1.2). En caso de duda, se le considera consumidor (IV.1.3) | DNI/RUC; explicación del uso personal o fuera del giro |
| 2 | **Proveedor** | ¿Quién ofrece habitualmente el producto o servicio? (IV.2). Razón social y RUC exactos | Comprobante, contrato, consulta RUC en SUNAT |
| 3 | **Relación de consumo** | ¿Hubo adquisición, contratación u oferta? (IV.5). En llamadas no autorizadas basta la oferta dirigida al consumidor | Boleta/factura, contrato, estado de cuenta, publicidad recibida |
| 4 | **Conducta del proveedor** | ¿Qué hizo u omitió que no corresponde a lo ofrecido o a la ley? | Documentos del proveedor, comunicaciones, capturas |
| 5 | **Afectación** | ¿Qué perdió o dejó de recibir el consumidor? Montos, prestación, tiempo | Estados de cuenta, comprobantes, fotos |
| 6 | **Gestión previa** | ¿Se reclamó al proveedor (Paso 1)? ¿Respondió, en plazo, y qué ofreció? | Hoja de reclamación con código, constancia, respuesta, correos |

Idoneidad (arts. 18–19): lo que el consumidor recibe debe corresponder a lo que razonablemente esperaba según lo ofrecido, la publicidad, el precio y las circunstancias. Responsabilidad (art. 104): el proveedor responde por falta de idoneidad o de información. Se exime solo si **él** acredita caso fortuito, fuerza mayor, hecho de un tercero o imprudencia del consumidor. **Al consumidor le toca mostrar el defecto; al proveedor, la causa que lo exime.**

## 2. Derechos y deberes que se invocan con más frecuencia

| Materia | Base | Qué hay que acreditar |
|---|---|---|
| Idoneidad | arts. 18, 19 | Lo ofrecido (oferta, publicidad, contrato) frente a lo recibido |
| Información | arts. 1.1.b, 2 | Información omitida, falsa, poco clara o tardía; pedido del consumidor y respuesta insuficiente |
| Atención de reclamos | art. 24 (Ley 31435): respuesta en máx. **15 días hábiles**; no puede condicionarse a pagos previos | Código y fecha del reclamo; fecha y contenido de la respuesta, o su ausencia |
| Libro de reclamaciones | arts. 150–152; D.S. 011-2011-PCM y mod. | Ver `guia-reclamo-proveedor.md` en la skill del Paso 1 |
| Servicios financieros | Res. SBS 04036-2022: reclamos en **15 días hábiles**; la respuesta desfavorable debe fundamentarse y poner a disposición la documentación de sustento (art. 9.6.g) | Contrato, hoja resumen, estados de cuenta, código del reclamo y respuesta |
| Métodos comerciales agresivos | art. 58.1.d (proposiciones persistentes o que ignoran el pedido de cese), **58.1.e** (call center, SMS o mensajes masivos sin consentimiento previo, informado, expreso e inequívoco; revocable) | Registro de llamadas o mensajes, titularidad de la línea, pedido de cese |
| Reparación, reposición o devolución | art. 97 (defectos, entrega tardía, oferta incumplida, garantía ineficaz) | Comprobante, garantía, informe técnico, intentos de reparación |
| Cobros indebidos | devolución más intereses (art. 115.1.g como referencia) | Estado de cuenta con el cargo; contrato que no lo autoriza |

## 3. Las instancias que cubre el plugin

```
Paso 0  Preparación: hechos, evidencias, viabilidad, pedido proporcional
Paso 1  Reclamo al proveedor (Libro de Reclamaciones o canal SBS)
          · respuesta en 15 días hábiles
          · si ofrece una solución y el consumidor la acepta expresamente
            ("Acuerdo aceptado para solucionar el reclamo"), el reclamo concluye y lo ofrecido es exigible
Paso 2  Reclama Virtual (SAC INDECOPI): mediación o conciliación con el proveedor
          · acuerdo → registrar literal y verificar su cumplimiento
          · sin acuerdo → legajo habilitante y fin del ciclo del plugin (la denuncia está fuera de alcance)
```

- **Prescripción** (art. 121): la facultad de la autoridad para actuar prescribe a los 2 años desde el hecho, o desde que cesó si es continuado. Anotar la fecha límite: si está cerca, el proceso tiene que avanzar rápido.
- **Referencia de proporcionalidad**: el Código entiende la reparación como volver las cosas a su estado anterior frente a las consecuencias patrimoniales **directas e inmediatas** (art. 115.1): reparar, cambiar, cumplir la prestación, devolver lo pagado o lo cobrado en exceso, pagar los gastos para mitigar. Es la vara para dimensionar el pedido en los Pasos 1 y 2 (ver `viabilidad-reencuadre.md`).
- **Lo que no se pide en estas instancias**: sanciones, multas, investigaciones, indemnización por daño moral o lucro cesante. Reclama Virtual bloquea incluso esas palabras.

## 4. Competencia: descartar antes de invertir

| Tema | Entidad |
|---|---|
| Facturación, calidad o corte de telefonía, internet o cable; contratación no solicitada; incumplimiento de ofertas o promociones de telecomunicaciones | OSIPTEL (reclamo ante la operadora y apelación ante el TRASU). A INDECOPI van la publicidad engañosa y los métodos comerciales agresivos, como las llamadas publicitarias no autorizadas |
| Facturación de luz o gas | OSINERGMIN (JARU) |
| Facturación de agua | SUNASS (reclamo ante la empresa prestadora y apelación ante el TRASS) |
| Atención de salud (calidad asistencial) en IPRESS; coberturas de IAFAS y seguros de salud | SUSALUD (conciliación: CECONAR). En seguros con cobertura de salud, la respuesta de la aseguradora debe remitir a SUSALUD (SBS art. 9.6.f) |
| Bancos, financieras, seguros (salvo coberturas de salud) | Reclamo ante la entidad (canal SBS); luego INDECOPI (consumo). Aspectos del SPP: SBS |
| Transporte | INDECOPI (consumo) |

## 5. La gestión previa como prueba y como fuente de obligaciones

- El código de la hoja de reclamación y su constancia prueban que se reclamó y desde cuándo corre el plazo.
- La respuesta del proveedor fija su posición. Sus contradicciones (p. ej., cifras de la carta frente a las del estado de cuenta) son argumentos centrales para el Paso 2.
- **Todo ofrecimiento del proveedor**, en el Paso 1 o en Reclama Virtual, es exigible. Guardarlo literal, con fecha y medio.
- Sin respuesta en 15 días hábiles: es un hecho que se registra con el cómputo de días.

## 6. Qué cuenta como buena prueba

1. **Documentos del propio proveedor**: contrato, hoja resumen, comprobante, estado de cuenta, respuesta, correos desde su dominio, perfil verificado de su cuenta de empresa. Son los más fuertes.
2. **Registros públicos o de terceros**: SUNAT, OSIPTEL "Checa tus líneas", resoluciones de INDECOPI.
3. **Capturas y grabaciones del consumidor**: con emisor, fecha, hora y contenido completo; acompañadas de la ficha del emisor; conservar el original.
4. **Relato del consumidor**: necesita corroboración.

## 7. Buenas prácticas de preparación

- **Un hecho, una fecha, una fuente.** Cada afirmación remite a su prueba (E##) o se marca como "afirmada sin prueba".
- **Cuantificar** en S/ con un cálculo que se pueda reproducir.
- **Plazos**: días hábiles para la respuesta del proveedor; días calendario para la prescripción (`plazos.py`).
- **Anticipar la respuesta del proveedor** (consentimiento, uso comercial, cláusula del contrato, imprudencia, "ya se solucionó") y preparar la réplica con pruebas.
- **Pedido proporcional y verificable**, con una alternativa razonable.
- **Lenguaje conciliador**: se pide que el proveedor haga algo concreto, no que se le castigue.
