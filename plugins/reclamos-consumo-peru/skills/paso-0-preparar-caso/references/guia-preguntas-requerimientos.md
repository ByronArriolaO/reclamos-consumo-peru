# Preguntas de investigación y requerimientos al proveedor

Regla central de la v0.5: **las preguntas se formulan y se responden en el Paso 0; al proveedor no se le hacen preguntas, se le formulan requerimientos.**

Motivo (experiencia práctica en reclamos de consumo y recomendación de funcionarios de INDECOPI):
- Casi ningún proveedor contestó una pregunta abierta ("¿por qué…?", "¿cuál es la tasa…?"). Respondió con fórmulas genéricas o la ignoró.
- Los funcionarios de INDECOPI insisten en una solicitud **precisa y concisa**. Un pliego largo de preguntas diluye el pedido y facilita una respuesta genérica.
- Un requerimiento bien formulado obliga al proveedor a una de tres salidas, y todas sirven: **lo entrega** (se obtiene la información que el consumidor no tenía), **no lo entrega** (el proveedor no acreditó lo que le tocaba probar) o **entrega algo que no cuadra** (contradicción documentada).

## 1. El ciclo pregunta → consumidor → requerimiento

```
Brechas del expediente (03: B##, hechos Afirmados o sin prueba, carga de la prueba)
   │
   ▼
06 Preguntas de investigación (Q##) ── formuladas para el CONSUMIDOR
   │
   ├─ Claude busca primero la respuesta (correo, almacenamiento en la nube, carpeta, fuentes públicas)
   ├─ Lo que no encuentra se lo pregunta al consumidor (1–2 rondas, máx. 4 en AskUserQuestion por ronda)
   │
   ▼
Cada Q## queda en uno de estos estados:
   Respondida (E##)   → se registra la evidencia (nuevo E##) y se actualiza el hecho
   Afirmada           → el consumidor lo sabe, pero no tiene prueba
   Sin respuesta      → nadie del lado del consumidor lo sabe
   Descartada         → ya no importa para el pedido
   │
   ▼
Si está Afirmada o Sin respuesta, y el poseedor del dato es el proveedor:
   → se convierte en un requerimiento S## (07 Estrategia y petitorio)
```

Solo se trasladan al proveedor los datos que **él tiene** y que **cambian el resultado del caso**. Lo que tiene un tercero o una fuente pública se busca por otra vía.

## 2. Cómo formular las preguntas al consumidor (Q##)

- Una pregunta, un dato. Cerrada y en lenguaje llano: "¿Tienes el correo o SMS en que el banco te avisó del cambio de tasa?".
- Pedir siempre la prueba junto con la respuesta: "¿Recuerdas la fecha? ¿Tienes una captura o el voucher?".
- Enlazar cada Q## al hecho o brecha que resuelve (H##, B##) e indicar el **poseedor probable**: Consumidor · Proveedor · Tercero · Pública.
- Priorizar: primero las que sostienen el monto, las fechas del reclamo y la conducta del proveedor.
- Si la respuesta del consumidor contradice un documento, registrarla como error a corregir en el relato, no como hecho.

## 3. Cómo formular un requerimiento al proveedor (S##)

**Estructura**: `Requiero` + **objeto** (qué documento o demostración) + **alcance** (monto, fecha, periodo, operación) + `, de forma que se verifique` + **conformidad concreta** que se quiere comprobar.

Objetos que funcionan:

| Objeto | Cuándo usarlo | Ejemplo de objeto |
|---|---|---|
| Base contractual o cláusula | Cobros, comisiones, bloqueos, cambios de condiciones | "la cláusula del contrato que habilita el cobro de la comisión X" |
| Demostración matemática | Intereses, cuotas, diferencias en el EECC | "la liquidación con la tasa, los días y el saldo base aplicados a mis cifras" |
| Documento o registro que solo tiene el proveedor | Consumos no reconocidos, llamadas, entregas, avisos | "el registro de autenticación de la operación del DD/MM/AAAA", "la grabación de la llamada del DD/MM/AAAA", "la constancia de envío del aviso de modificación" |
| Identificación del responsable | Beneficios de marca, intermediarios, seguros | "la razón social y el RUC de la empresa que otorga el beneficio X" |
| Constancia de un hecho propio | Caídas de plataforma, atención en agencia | "la constancia de la indisponibilidad de la banca por internet el DD/MM/AAAA" |

**Antes y después**:

| Pregunta (no funciona) | Requerimiento (sí funciona) |
|---|---|
| ¿Cuál es la tasa de interés aplicada para llegar a los S/ 100 cobrados por intereses? | Requiero la base contractual que habilita el cobro de intereses y la demostración matemática correspondiente, de forma que se verifique que los S/ 100 de intereses del EECC de junio de 2026 son conformes. |
| ¿Por qué no se hizo el débito automático en la fecha pactada? | Requiero la constancia de la fecha y hora en que se ejecutó el débito automático del estado de cuenta de marzo de 2026 y la condición de la afiliación que fija su fecha de ejecución, de forma que se verifique si se cumplió lo pactado. |
| ¿Quién hizo este consumo? | Requiero el registro de autenticación del consumo de S/ 200,00 del 15/03/2026 (canal, dispositivo y método de validación), de forma que se verifique que fue realizado por el titular. |
| ¿Me avisaron del cambio de tasa? | Requiero la constancia de la comunicación previa del incremento de la tasa de interés aplicado desde el EECC de junio de 2026 (fecha, medio y contenido), de forma que se verifique que se informó con la anticipación exigible. |
| ¿Dónde están mis puntos? | Requiero el estado de los puntos de mi tarjeta terminada en 0000 (acumulados, canjeados, vencidos y transferidos), de forma que se verifique el saldo que debió migrar a la nueva tarjeta. |

**Reglas de concisión** (las verifica `scripts/validar_requerimientos.py`):
- Máximo **4 requerimientos** por reclamo; lo ideal son 1 o 2. Si hay más, agruparlos por objeto. Si no queda nada que requerir, 07 lo declara con `sin_requerimientos: <motivo>`.
- Cada requerimiento en una sola oración, de **350 caracteres como máximo**.
- Sin signos de interrogación ni fórmulas abiertas ("explique", "indique por qué", "cuál", "cómo").
- Con al menos un dato concreto: monto, fecha, periodo, número de operación o de reclamo.
- Con la finalidad verificable ("de forma que se verifique…").
- Sin lenguaje sancionador ni palabras bloqueadas.

## 4. Cómo se une el requerimiento con la pretensión (petitorio escalonado)

El requerimiento **no reemplaza** la pretensión económica. Se elige una de dos formas, según la palanca que identificó el `analista-viabilidad`:

| Forma | Cuándo | Redacción de la pretensión |
|---|---|---|
| **Directa** | Palanca fuerte: carga de la prueba en el proveedor, falla operativa propia documentada, cobro sin base aparente | "Solicito el extorno de S/ X y de los intereses y cargos derivados." + los requerimientos como sustento |
| **Condicionada** | No se sabe si el cobro es correcto; la información la tiene el proveedor | "De no acreditarse lo requerido, solicito el extorno de S/ X y de los cargos derivados." |

En ambas formas, pedir todas las consecuencias: devolución, intereses y cargos derivados, corrección en centrales de riesgo y exoneración de costos asociados (para no tener que abrir un segundo reclamo por las consecuencias).

Orden del PEDIDO en el reclamo:
1. Requerimientos S## (numerados).
2. Pretensión P## (directa o condicionada).
3. Plazo y canal de respuesta.

## 5. Qué hacer con la respuesta

La analiza el `analista-respuesta` (archivo 08). Cada S## queda: **Atendido** · **Parcial** · **Genérico** (fórmulas sin aplicarlas a las cifras del consumidor) · **Omitido** · **Negado sin sustento** · **Negado con sustento** · **Contradice** un documento.
- Lo entregado se convierte en evidencia (E##) y, si admite un hecho, en admisión (A##).
- Lo que contradice otro documento se registra como contradicción (C##).
- Lo omitido, genérico o negado sin sustento se registra como omisión (O##). En el Paso 2 se lee así: "el proveedor no acreditó…".

En el Paso 2 se repiten **solo** los requerimientos no atendidos, con la misma redacción o más corta, junto con la pretensión.

## 6. Banco de requerimientos por materia

| Materia | Requerimientos tipo |
|---|---|
| Intereses y EECC | Base contractual + demostración matemática aplicada a las cifras del EECC del periodo · desglose de los conceptos que componen el total facturado |
| Consumos no reconocidos | Registro de autenticación (canal, dispositivo, método) · constancia del envío de alertas · sustento de la aprobación del consumo por encima de la línea disponible |
| Débito automático o pagos | Constancia de fecha y hora de ejecución · condición de la afiliación · criterio de imputación del pago aplicado |
| Cambio de condiciones (tasas, comisiones) | Constancia de la comunicación previa (fecha, medio, contenido) · cláusula que habilita la modificación |
| Bloqueos y cancelaciones | Grabación de la llamada · sustento del motivo del bloqueo · cláusula aplicada |
| Puntos y recompensas | Estado de puntos (acumulados, canjeados, vencidos, transferidos) · regla de migración entre tarjetas |
| Seguros y beneficios de tarjeta | Razón social y RUC del responsable del beneficio · condicionado aplicable · sustento de la denegatoria |
| Transporte | Informe de incidencia (PIR, reprogramación) · constancia de la comunicación del cambio · política aplicada |
| Llamadas y datos personales | Fuente de obtención del número · constancia del consentimiento previo · atención de la solicitud ARCOP |
| Servicios en general | Constancia de la prestación · política o condición aplicada · sustento del cobro |
