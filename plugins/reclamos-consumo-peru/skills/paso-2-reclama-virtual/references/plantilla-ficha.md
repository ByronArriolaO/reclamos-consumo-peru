# Ficha Reclama Virtual
<!-- Una ficha por reclamo. Guardarla en la carpeta del caso como "Ficha Reclama Virtual - <Proveedor>.md".
     Formato: "clave: valor". Listas: clave vacía seguida de líneas "- ...". Textos largos en las secciones ## MOTIVO y ## SOLICITUD.
     Borrar las líneas que no apliquen a la categoría. Validar con scripts/validar_ficha.py antes de ir al portal. -->

caso: r#
categoria: bancario            <!-- bancario | transporte | colegios | otros | llamadas -->
oficina: Lima - Sede Central   <!-- nombre exacto de catalogos.json > oficinas -->

## Etapa 1 — Cuéntanos tu reclamo

<!-- Solo colegios -->
anonimo: no                    <!-- si | no. "si" omite la Etapa 3 -->

<!-- Todas salvo llamadas -->
expuso_al_proveedor: si        <!-- si | no -->
medio_reclamo: Libro de reclamaciones   <!-- Personal | Telefónico | Virtual | Libro de reclamaciones | Otros -->
medio_reclamo_otro:            <!-- solo si medio_reclamo = Otros (máx. 150) -->
medio_compra: Virtual          <!-- Presencial | Telefónico | Virtual | No compré/ No contraté -->
recuerda_fecha: si             <!-- si | no -->
fecha_hecho: DD/MM/AAAA        <!-- DD/MM/AAAA, no futura, desde 2016 -->
fecha_aproximada:              <!-- solo si recuerda_fecha = no (máx. 150). Ej.: quincena de enero de 2026 -->

<!-- Solo bancario -->
producto_financiero: Tarjeta de crédito  <!-- Créditos comerciales | Crédito de consumo | Cuenta corriente | Depósito de ahorros | Depósito CTS | Arrendamiento financiero | Depósito a plazo | Tarjeta de crédito | Tarjeta de débito | Crédito hipotecario | Otros -->
numero_cuenta:                 <!-- opcional; solo dígitos (salvo producto Otros), máx. 30 -->

<!-- Solo llamadas -->
cese_solicitado: no            <!-- ¿pidió al proveedor que deje de llamar? si | no -->
telefono_propio: 999999999     <!-- número donde RECIBIÓ las llamadas, 7-12 dígitos -->
autorizo_publicidad: no        <!-- si | no -->
llamadas:
- 01XXXXXXX | DD/MM/AAAA | HH:MM   <!-- número que LLAMÓ | fecha | hora 24 h. Una línea por llamada -->

<!-- Adjuntos (opcional; máx. 5; ≤ 5,25 MB c/u; pdf jpg jpeg png doc docx xls xlsx ppt pptx mp3 mp4; nombres únicos y sin emojis).
     Tipo = uno de los permitidos para la categoría (catalogos.json > tipos_documento_adjunto). Ruta = ruta en el equipo del usuario. -->
adjuntos:
- Hoja de reclamación | C:\ruta\del\caso\Reclamo 000000 - Proveedor.pdf
- Hoja de reclamación | C:\ruta\del\caso\Respuesta 000000 - Proveedor.pdf

## MOTIVO
Hechos probados + bloque del Paso 1 con lo admitido (A##), lo contradicho (C##) y lo no acreditado (O##). Apuntar a ≤ 2000. Texto plano, máx. 4000 caracteres, sin emojis ni Markdown, sin palabras bloqueadas (ver palabras-bloqueadas.json). No aplica a llamadas (texto fijo del portal).

## SOLICITUD
Solo los requerimientos no atendidos ("Requiero …, de forma que se verifique …") y la pretensión pendiente. Apuntar a ≤ 1000. Texto plano, máx. 3000 caracteres, mismas reglas. No aplica a llamadas (requerimiento fijo del portal).

## Etapa 2 — Identifica al reclamado

reclamado_tipo_persona: juridica   <!-- natural | juridica -->
reclamado_tipo_documento: RUC      <!-- juridica: RUC. natural: DNI | CE | RUC -->
reclamado_documento: 20XXXXXXXXX
reclamado_nombre_esperado: Proveedor Ejemplo S.A.C.   <!-- para cotejar con lo que autocompleta el portal -->
reclamado_sin_documento: no        <!-- si = marcar "No cuento con esa información" y llenar a mano: -->
reclamado_nombre:                  <!-- razón social / nombre comercial (jurídica sin RUC) -->
reclamado_nombres:                 <!-- natural sin documento -->
reclamado_apellido_paterno:
reclamado_apellido_materno:
reclamado_direccion:               <!-- obligatoria si no autocompleta o no hay documento (máx. 200) -->
reclamado_correo:                  <!-- opcional -->
reclamado_telefono:                <!-- opcional -->

## Etapa 3 — Completa tus datos

reclamante_tipo_persona: natural   <!-- natural | juridica -->
reclamante_tipo_documento: DNI     <!-- natural: DNI | CE | RUC | Pasaporte. juridica: RUC -->
reclamante_documento:              <!-- si se deja vacío, Claude lo pide al llenar; no se guarda en memoria -->
reclamante_mantener_direccion: si  <!-- si = "Mantengo la dirección de mi documento" -->
reclamante_direccion:              <!-- obligatoria si mantener_direccion = no (máx. 200) -->
reclamante_correo: correo@dominio.com
reclamante_telefono: 999999999
reclamante_discapacidad:           <!-- opcional: vacío (no se marca) | no | visual | auditiva | motora | cognitiva. Solo si el usuario lo indica -->

<!-- Solo si reclamante_tipo_persona = juridica -->
representante_tipo_documento: DNI
representante_documento:
representante_mantener_direccion: si
representante_direccion:
representante_correo:
representante_telefono:
