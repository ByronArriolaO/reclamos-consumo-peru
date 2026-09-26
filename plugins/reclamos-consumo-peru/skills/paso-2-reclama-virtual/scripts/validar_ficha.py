#!/usr/bin/env python3
"""Valida una ficha de Reclama Virtual (INDECOPI) antes de llevarla al portal.

Uso:
  python3 validar_ficha.py FICHA.md            # valida la ficha completa
  python3 validar_ficha.py FICHA.md --json     # salida JSON (para Claude)
  python3 validar_ficha.py --texto ARCHIVO.txt # solo revisa un texto libre
  python3 validar_ficha.py --limpiar ARCHIVO   # imprime el texto sin sintaxis Markdown

Replica las reglas del portal relevadas de su comportamiento observable (23/09/2026):
- palabras que bloquean el paso a la Etapa 2 (subcadena, sin distinguir mayusculas),
- limites de caracteres, emojis, restos de Markdown,
- campos obligatorios por categoria, formatos de fecha, documentos y adjuntos.
Ademas detecta marcadores de la plantilla sin reemplazar (caso: r#, "Apuntar a", "Texto plano",
comentarios <!-- --> dentro de MOTIVO o SOLICITUD, "…" como texto, RUC de ejemplo, rutas C:\\ruta\\),
IDs internos del expediente (E##, H##, S##, [E03 p.2]…) en los textos que van al portal y campos
"clave: valor" escritos dentro de MOTIVO o SOLICITUD. Las rutas relativas de los adjuntos se resuelven
contra la carpeta de la ficha.
Salida: lista de ERRORES (bloquean) y AVISOS (revisar). Codigo de salida 1 si hay errores y 2 si la
ficha no se puede leer.
"""
import json
import os
import re
import sys
import unicodedata
from datetime import date, datetime

UTF8 = True
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    UTF8 = False
    try:
        sys.stdout.reconfigure(errors="replace")
        sys.stderr.reconfigure(errors="replace")
    except Exception:
        pass
MARCA_ERROR = "\u2717" if UTF8 else "x"

BASE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(BASE, "..", "references")
try:
    with open(os.path.join(REF, "palabras-bloqueadas.json"), encoding="utf-8") as fh:
        BLOQ = json.load(fh)
    with open(os.path.join(REF, "catalogos.json"), encoding="utf-8") as fh:
        CAT = json.load(fh)
except (OSError, ValueError) as exc:
    print(f"Error: no se pudieron leer los catalogos de references/ ({exc}).", file=sys.stderr)
    sys.exit(2)

RUC_EJEMPLO = {"20000000000", "20123456789", "12345678901", "10000000000"}
ID_INTERNO = re.compile(r"\b[EHBPQRSACON]\d{2}\b|\[[EHBPQRSACON]\d{2}[^\]]*\]")
CLAVE_EN_TEXTO = re.compile(r"^\s*([a-z][a-z0-9]*(?:_[a-z0-9]+)+|caso|categoria|oficina|anonimo|adjuntos|llamadas)\s*:(\s|$)")
MARCADORES_TEXTO = ("Apuntar a", "Texto plano")

SI_NO = {"si": True, "sí": True, "no": False}
EMOJI_RE = re.compile(
    "[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U0001F900-\U0001F9FF\U00002B00-\U00002BFF\uFE0F\u200D]"
)
MD_RE = [
    (re.compile(r"\\([\[\]\.\-\*_#()!+>`])"), "escape de Markdown (\\x)"),
    (re.compile(r"(?<!\\)\*\*|(?<!\\)__"), "negrita Markdown (** o __)"),
    (re.compile(r"^\s{0,3}#{1,6}\s", re.M), "encabezado Markdown (#)"),
    (re.compile(r"^\s*[*+]\s+", re.M), "viñeta Markdown (* +)"),
    (re.compile(r"\[[^\]]+\]\([^)]+\)"), "enlace Markdown [texto](url)"),
]


def norm_key(k):
    k = unicodedata.normalize("NFD", k.strip().lower())
    k = "".join(c for c in k if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "_", k).strip("_")


def parse_ficha(text):
    """Claves 'clave: valor' + listas '- ...' bajo una clave + secciones '## MOTIVO' / '## SOLICITUD'.
    Devuelve (data, lists, sections, crudas, claves_en_texto): 'crudas' conserva los comentarios de
    las secciones; 'claves_en_texto' lista las claves halladas dentro de MOTIVO o SOLICITUD (se
    procesan como campos y se avisa)."""
    crudas = {}
    cur = None
    for raw in text.splitlines():
        m_sec = re.match(r"^##\s+(.+)$", raw.rstrip())
        if m_sec:
            name = norm_key(m_sec.group(1))
            cur = name if name in ("motivo", "solicitud") else None
            if cur:
                crudas[cur] = []
            continue
        if cur:
            crudas[cur].append(raw)
    crudas = {k: "\n".join(v).strip() for k, v in crudas.items()}

    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    data, lists, sections = {}, {}, {}
    claves_en_texto = []
    current_list, current_section = None, None
    for raw in text.splitlines():
        line = raw.rstrip()
        m_sec = re.match(r"^##\s+(.+)$", line)
        if m_sec:
            name = norm_key(m_sec.group(1))
            if name in ("motivo", "solicitud"):
                current_section = name
                sections[name] = []
                current_list = None
                continue
            current_section = None
            current_list = None
            continue
        if current_section:
            if CLAVE_EN_TEXTO.match(line) and "".join(sections[current_section]).strip():
                claves_en_texto.append((current_section, line.split(":", 1)[0].strip()))
                current_section = None
            else:
                sections[current_section].append(raw)
                continue
        if line.startswith("#") or not line.strip() or line.strip().startswith("<!--"):
            continue
        m_item = re.match(r"^\s*-\s+(.*)$", line)
        if m_item and current_list:
            lists.setdefault(current_list, []).append(m_item.group(1).strip())
            continue
        m_kv = re.match(r"^\s*([^:]{1,60}):\s*(.*)$", line)
        if m_kv:
            key = norm_key(m_kv.group(1))
            val = re.sub(r"\s*<!--.*?-->\s*", "", m_kv.group(2)).strip()
            data[key] = val
            current_list = key if val == "" else None
    for k, v in sections.items():
        sections[k] = "\n".join(v).strip()
    return data, lists, sections, crudas, claves_en_texto


def check_texto(nombre, texto, limite, errores, avisos):
    if not texto:
        errores.append(f"{nombre}: está vacío.")
        return
    n = len(texto)
    if n > limite:
        errores.append(f"{nombre}: {n} caracteres; el portal acepta {limite}. Recortar {n - limite}.")
    elif n > limite * 0.95:
        avisos.append(f"{nombre}: {n}/{limite} caracteres, muy cerca del límite.")
    for grupo, etiqueta in (("sancion_multa", "amarillo: sanción/indemnización"), ("otra_entidad", "verde: otra entidad")):
        hits = []
        for frase in BLOQ[grupo]:
            try:
                rx = re.compile("(" + frase + ")", re.I)
            except re.error:
                rx = re.compile(re.escape(frase), re.I)
            for m in rx.finditer(texto):
                ini = max(0, m.start() - 30)
                hits.append(f"'{m.group(0)}' (regla '{frase}') en «…{texto[ini:m.end() + 30]}…»")
        if hits:
            uniq = list(dict.fromkeys(hits))
            errores.append(f"{nombre}: palabras que el portal bloquea [{etiqueta}]:\n    - " + "\n    - ".join(uniq))
    emo = EMOJI_RE.findall(texto)
    if emo:
        errores.append(f"{nombre}: contiene emojis/símbolos {''.join(sorted(set(emo)))}; el portal puede rechazar el envío.")
    for rx, desc in MD_RE:
        if rx.search(texto):
            avisos.append(f"{nombre}: posible {desc}; el formulario es texto plano y se verá literal.")


def limpiar(t):
    t = re.sub(r"(?<!\\)\*\*|(?<!\\)__", "", t)
    t = re.sub(r"\\([\[\]\.\-\*_#()!+>`])", r"\1", t)
    t = re.sub(r"^\s{0,3}#{1,6}\s+", "", t, flags=re.M)
    t = re.sub(r"^(\s*)[*+]\s+", r"\1- ", t, flags=re.M)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", t)
    t = EMOJI_RE.sub("", t)
    t = re.sub(r"[ \t]+\n", "\n", t)
    return re.sub(r"\n{3,}", "\n\n", t).strip()


def es_si(v):
    return SI_NO.get((v or "").strip().lower())


def check_fecha(nombre, v, errores):
    try:
        d = datetime.strptime(v.strip(), "%d/%m/%Y").date()
    except Exception:
        errores.append(f"{nombre}: '{v}' no tiene formato DD/MM/AAAA.")
        return None
    if d > date.today():
        errores.append(f"{nombre}: {v} es futura; el calendario del portal no la permite.")
    if d.year < CAT["calendario"]["anio_minimo"]:
        errores.append(f"{nombre}: el calendario del portal empieza en {CAT['calendario']['anio_minimo']}.")
    return d


def check_doc(prefijo, tipo, num, errores):
    tipo = (tipo or "").strip()
    lon = CAT["documentos_identidad"]["longitud"].get(tipo)
    if not lon:
        errores.append(f"{prefijo}_tipo_documento: '{tipo}' no válido (DNI, CE, RUC, Pasaporte).")
        return
    if not num:
        return
    if tipo in ("DNI", "RUC") and not num.isdigit():
        errores.append(f"{prefijo}_documento: {tipo} debe tener solo dígitos.")
    if not (lon[0] <= len(num) <= lon[1]):
        errores.append(f"{prefijo}_documento: {tipo} debe tener entre {lon[0]} y {lon[1]} caracteres (tiene {len(num)}).")
    if tipo == "RUC" and len(num) == 11 and num[:2] not in ("10", "15", "17", "20"):
        errores.append(f"{prefijo}_documento: RUC '{num}' no empieza con 10/15/17/20.")


def es_ruta_absoluta(ruta):
    return os.path.isabs(ruta) or bool(re.match(r"^[A-Za-z]:[\\/]|^\\\\", ruta))


def fmt_bytes(n):
    return f"{n:,}".replace(",", " ") + f" bytes ({n / 1048576:.2f} MiB)".replace(".", ",")


def check_plantilla(d, L, S, crudas, cat, E, A):
    """Marcadores de la plantilla que quedaron sin reemplazar."""
    caso = d.get("caso", "")
    if "caso" in d and (not caso or "#" in caso or "<" in caso):
        E.append(f"caso: '{caso}' es el marcador de la plantilla; poner el número real del caso (p. ej., r1).")
    for k, v in d.items():
        if v.strip() in ("…", "..."):
            E.append(f"{k}: tiene '{v.strip()}' (marcador de la plantilla); completar o borrar la línea.")
    if cat != "llamadas":
        for sec in ("motivo", "solicitud"):
            nombre = sec.upper()
            txt = S.get(sec, "")
            cruda = crudas.get(sec, "")
            for mk in MARCADORES_TEXTO:
                if mk.lower() in txt.lower():
                    E.append(f"{nombre}: contiene el texto de la plantilla ('{mk} …'); reemplazarlo por el texto real.")
            if "<!--" in cruda:
                E.append(f"{nombre}: contiene un comentario <!-- --> de la plantilla; borrarlo (se copiaría al portal).")
            if txt.strip() in ("…", "..."):
                E.append(f"{nombre}: solo tiene '…' (marcador de la plantilla).")
    for k in ("reclamado_documento", "reclamante_documento", "representante_documento"):
        v = d.get(k, "")
        es_marcador = bool(re.search(r"[Xx]{3,}", v)) or v in RUC_EJEMPLO
        if v and es_marcador:
            E.append(f"{k}: '{v}' es un número de ejemplo de la plantilla; poner el número real (RUC en SUNAT).")
    for i, it in enumerate(L.get("adjuntos", []), 1):
        ruta = it.split("|", 1)[-1].strip()
        if re.search(r"^[A-Za-z]:[\\/]ruta[\\/]|(^|[\\/])(\.\.\.|…)([\\/]|$)", ruta, re.I):
            E.append(f"adjuntos #{i}: '{ruta}' es la ruta de ejemplo de la plantilla; poner la ruta real del archivo.")


def check_ids_internos(S, E, A):
    for sec in ("motivo", "solicitud"):
        hits = sorted(set(m.group(0) for m in ID_INTERNO.finditer(S.get(sec, ""))))
        if hits:
            A.append(f"{sec.upper()}: contiene IDs internos del expediente ({', '.join(hits[:8])}); el proveedor e INDECOPI no los conocen. Reemplazarlos por la descripción del documento o del hecho.")


def validar(path):
    with open(path, encoding="utf-8-sig") as fh:
        text = fh.read()
    d, L, S, crudas, claves_txt = parse_ficha(text)
    E, A = [], []
    carpeta = os.path.dirname(os.path.abspath(path))

    cat = norm_key(d.get("categoria", ""))
    for sec, clave in claves_txt:
        A.append(f"{sec.upper()}: la línea '{clave}: …' está dentro del texto; falta un encabezado ## que cierre la sección. Se leyó como campo, pero revisar la ficha.")
    check_plantilla(d, L, S, crudas, cat, E, A)
    if cat not in CAT["categorias"]:
        E.append("categoria: debe ser bancario, transporte, colegios, otros o llamadas.")
        return E, A, d, S
    ofi = d.get("oficina", "")
    if ofi not in CAT["oficinas"]:
        E.append(f"oficina: '{ofi}' no coincide con una oficina del portal (ver catalogos.json).")

    # ---------- Etapa 1 ----------
    if cat == "llamadas":
        if es_si(d.get("cese_solicitado")) is None:
            E.append("cese_solicitado: indicar si/no.")
        tel = d.get("telefono_propio", "")
        if not (tel.isdigit() and 7 <= len(tel) <= 12):
            E.append("telefono_propio: 7 a 12 dígitos, solo números (número donde se recibieron las llamadas).")
        if es_si(d.get("autorizo_publicidad")) is None:
            E.append("autorizo_publicidad: indicar si/no.")
        elif es_si(d.get("autorizo_publicidad")):
            A.append("autorizo_publicidad = sí: el reclamo por llamadas no autorizadas pierde sustento; confirmar con el usuario.")
        llam = L.get("llamadas", [])
        if not llam:
            E.append("llamadas: registrar al menos una llamada '- número | DD/MM/AAAA | HH:MM'.")
        for i, it in enumerate(llam, 1):
            p = [x.strip() for x in it.split("|")]
            if len(p) != 3:
                E.append(f"llamadas #{i}: formato '- número | DD/MM/AAAA | HH:MM'.")
                continue
            n = p[0]
            if not n.isdigit():
                E.append(f"llamadas #{i}: número '{p[0]}' debe ir solo con dígitos (sin +51, espacios ni guiones).")
            elif not (7 <= len(n) <= 12):
                E.append(f"llamadas #{i}: número '{p[0]}' debe tener 7 a 12 dígitos (solo dígitos; sin +51).")
            check_fecha(f"llamadas #{i} fecha", p[1], E)
            if not re.fullmatch(r"([01]?\d|2[0-3]):[0-5]\d", p[2]):
                E.append(f"llamadas #{i}: hora '{p[2]}' debe ser HH:MM en formato 24 h.")
    else:
        exp = es_si(d.get("expuso_al_proveedor"))
        if exp is None:
            E.append("expuso_al_proveedor: indicar si/no.")
        elif exp:
            mr = d.get("medio_reclamo", "")
            if mr not in CAT["medios_reclamo"]:
                E.append(f"medio_reclamo: '{mr}' no válido ({', '.join(CAT['medios_reclamo'])}).")
            if mr == "Otros":
                o = d.get("medio_reclamo_otro", "")
                if not o.strip():
                    E.append("medio_reclamo_otro: obligatorio si medio_reclamo = Otros.")
                elif len(o) > 150:
                    E.append("medio_reclamo_otro: máximo 150 caracteres.")
        else:
            A.append("expuso_al_proveedor = no: el portal lo acepta, pero sin reclamo previo el proveedor suele pedir que primero se agote su canal; valorar presentar antes el Libro de Reclamaciones.")
        mc = d.get("medio_compra", "")
        if mc not in CAT["medios_compra"]:
            E.append(f"medio_compra: '{mc}' no válido ({', '.join(CAT['medios_compra'])}).")
        rec = es_si(d.get("recuerda_fecha"))
        if rec is None:
            E.append("recuerda_fecha: indicar si/no.")
        elif rec:
            if not d.get("fecha_hecho"):
                E.append("fecha_hecho: obligatoria si recuerda_fecha = si (DD/MM/AAAA).")
            else:
                check_fecha("fecha_hecho", d["fecha_hecho"], E)
        else:
            fa = d.get("fecha_aproximada", "")
            if not fa.strip():
                E.append("fecha_aproximada: obligatoria si recuerda_fecha = no (máx. 150).")
            elif len(fa) > 150:
                E.append("fecha_aproximada: máximo 150 caracteres.")
        check_texto("MOTIVO", S.get("motivo", ""), CAT["limites"]["motivo"], E, A)
        check_texto("SOLICITUD", S.get("solicitud", ""), CAT["limites"]["solicitud"], E, A)
        check_ids_internos(S, E, A)
        if cat == "bancario":
            pf = d.get("producto_financiero", "")
            if pf not in CAT["productos_financieros"]:
                E.append(f"producto_financiero: '{pf}' no válido ({', '.join(CAT['productos_financieros'])}).")
            nc = d.get("numero_cuenta", "")
            if nc:
                if len(nc) > 30:
                    E.append("numero_cuenta: máximo 30 caracteres.")
                if pf != "Otros" and not nc.isdigit():
                    E.append("numero_cuenta: el portal solo admite dígitos (salvo producto 'Otros'). Quitar espacios, guiones y asteriscos.")
                if pf in ("Tarjeta de crédito", "Tarjeta de débito") and len(nc) >= 13:
                    A.append("numero_cuenta: parece un número de tarjeta completo; el campo es opcional y se traslada al proveedor. Preferir omitirlo o usar solo los últimos 4 dígitos.")
        if cat == "colegios":
            an = es_si(d.get("anonimo"))
            if an is None:
                E.append("anonimo: indicar si/no (solo Colegios).")
            elif an:
                A.append("anonimo = sí: el portal omite la Etapa 3 (sin datos del reclamante). INDECOPI no podrá contactar al usuario para la mediación; confirmar que es lo que quiere.")

    # ---------- Adjuntos ----------
    tipos = CAT["tipos_documento_adjunto"][cat]
    adj = L.get("adjuntos", [])
    if len(adj) > CAT["adjuntos"]["max_archivos"]:
        E.append(f"adjuntos: {len(adj)} archivos; el portal acepta máximo {CAT['adjuntos']['max_archivos']}.")
    nombres = []
    for i, it in enumerate(adj, 1):
        p = [x.strip() for x in it.split("|", 1)]
        if len(p) != 2:
            E.append(f"adjuntos #{i}: formato '- Tipo de documento | ruta del archivo'.")
            continue
        tipo, ruta = p
        if tipo not in tipos:
            E.append(f"adjuntos #{i}: tipo '{tipo}' no existe en esta categoría ({', '.join(tipos)}).")
        nombre = re.split(r"[\\/]", ruta)[-1]
        ext = os.path.splitext(nombre)[1].lower()
        if ext not in CAT["adjuntos"]["extensiones"]:
            E.append(f"adjuntos #{i}: extensión '{ext}' no admitida.")
        if EMOJI_RE.search(nombre):
            E.append(f"adjuntos #{i}: el nombre del archivo tiene emojis.")
        if nombre in nombres:
            E.append(f"adjuntos #{i}: nombre repetido '{nombre}'; el portal rechaza archivos con el mismo nombre.")
        nombres.append(nombre)
        real = ruta if es_ruta_absoluta(ruta) else os.path.join(carpeta, ruta)
        maxb = CAT["adjuntos"]["max_bytes"]
        if os.path.isfile(real):
            sz = os.path.getsize(real)
            if sz > maxb:
                E.append(f"adjuntos #{i}: '{nombre}' pesa {fmt_bytes(sz)}; el máximo es {fmt_bytes(maxb)}. Comprimir o dividir.")
        else:
            A.append(f"adjuntos #{i}: no puedo leer '{ruta}' desde aquí; verificar en el equipo del usuario que exista y pese como máximo {fmt_bytes(maxb)}.")

    # ---------- Etapa 2: reclamado ----------
    tp = norm_key(d.get("reclamado_tipo_persona", ""))
    if tp not in ("natural", "juridica"):
        E.append("reclamado_tipo_persona: natural o juridica.")
    else:
        sin_doc = es_si(d.get("reclamado_sin_documento")) is True
        if sin_doc:
            if tp == "juridica" and not d.get("reclamado_nombre"):
                E.append("reclamado_nombre: obligatorio (razón social o nombre comercial) si no hay RUC.")
            if tp == "natural" and not (d.get("reclamado_nombres") and d.get("reclamado_apellido_paterno")):
                E.append("reclamado_nombres y reclamado_apellido_paterno: obligatorios si no hay documento.")
            if not d.get("reclamado_direccion"):
                E.append("reclamado_direccion: obligatoria si no hay documento.")
            A.append("reclamado sin documento: sin RUC/DNI la notificación al proveedor es menos certera; buscar el RUC en SUNAT antes de rendirse.")
        else:
            td = "RUC" if tp == "juridica" else d.get("reclamado_tipo_documento", "RUC")
            if tp == "natural" and td not in CAT["documentos_identidad"]["reclamado_natural"]:
                E.append("reclamado_tipo_documento: DNI, CE o RUC.")
            if not d.get("reclamado_documento"):
                E.append("reclamado_documento: obligatorio (o marcar reclamado_sin_documento: si).")
            check_doc("reclamado", td, d.get("reclamado_documento", ""), E)
        if d.get("reclamado_correo") and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", d["reclamado_correo"]):
            E.append("reclamado_correo: formato inválido.")

    # ---------- Etapa 3: reclamante ----------
    if not (cat == "colegios" and es_si(d.get("anonimo"))):
        tr = norm_key(d.get("reclamante_tipo_persona", ""))
        if tr not in ("natural", "juridica"):
            E.append("reclamante_tipo_persona: natural o juridica.")
        else:
            td = "RUC" if tr == "juridica" else d.get("reclamante_tipo_documento", "DNI")
            check_doc("reclamante", td, d.get("reclamante_documento", ""), E)
            if not d.get("reclamante_documento"):
                A.append("reclamante_documento vacío: pedirlo al usuario al momento de llenar la Etapa 3 (no guardarlo en memoria).")
            if tr == "natural":
                for k in ("reclamante_correo", "reclamante_telefono"):
                    if not d.get(k):
                        E.append(f"{k}: obligatorio para persona natural.")
                if td in ("CE", "Pasaporte", "RUC") and not d.get("reclamante_nombres"):
                    A.append("reclamante con CE/Pasaporte/RUC: el portal puede no autocompletar nombres; tener apellidos y nombres a mano.")
                disc = norm_key(d.get("reclamante_discapacidad", ""))
                if disc and disc not in ("no", "visual", "auditiva", "motora", "cognitiva"):
                    E.append("reclamante_discapacidad: no, visual, auditiva, motora o cognitiva.")
            else:
                if not d.get("representante_documento"):
                    E.append("representante_documento: obligatorio para reclamante persona jurídica (DNI del representante).")
                for k in ("representante_correo", "representante_telefono"):
                    if not d.get(k):
                        E.append(f"{k}: obligatorio para reclamante persona jurídica.")
            if not es_si(d.get("reclamante_mantener_direccion", "si")) and not d.get("reclamante_direccion"):
                E.append("reclamante_direccion: obligatoria si no se mantiene la dirección del documento.")
            c = d.get("reclamante_correo") or d.get("representante_correo")
            if c and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", c):
                E.append("correo del reclamante: formato inválido.")
    return E, A, d, S


def leer_texto(ruta):
    with open(ruta, encoding="utf-8-sig") as fh:
        return fh.read()


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(2)
    try:
        if args[0] == "--limpiar":
            if len(args) < 2:
                raise ValueError("uso: validar_ficha.py --limpiar ARCHIVO")
            print(limpiar(leer_texto(args[1])))
            return
        if args[0] == "--texto":
            if len(args) < 2:
                raise ValueError("uso: validar_ficha.py --texto ARCHIVO")
            t = leer_texto(args[1]).strip()
            E, A = [], []
            check_texto("TEXTO", t, 4000, E, A)
            res = {"errores": E, "avisos": A, "caracteres": len(t)}
        else:
            E, A, d, S = validar(args[0])
            res = {"errores": E, "avisos": A, "categoria": d.get("categoria"),
                   "caracteres_motivo": len(S.get("motivo", "")), "caracteres_solicitud": len(S.get("solicitud", ""))}
    except ValueError as exc:
        if isinstance(exc, UnicodeDecodeError):
            print("Error: el archivo no está en UTF-8. Guardarlo como UTF-8 y reintentar.", file=sys.stderr)
        else:
            print(f"Error: {exc}", file=sys.stderr)
        sys.exit(2)
    except FileNotFoundError as exc:
        print(f"Error: no existe el archivo '{exc.filename}'.", file=sys.stderr)
        sys.exit(2)
    except IsADirectoryError as exc:
        print(f"Error: '{exc.filename}' es una carpeta; indicar el archivo de la ficha.", file=sys.stderr)
        sys.exit(2)
    except OSError as exc:
        print(f"Error: no se pudo leer '{exc.filename}': {exc.strerror}.", file=sys.stderr)
        sys.exit(2)
    if "--json" in args:
        print(json.dumps(res, ensure_ascii=False, indent=1))
    else:
        print(f"ERRORES ({len(res['errores'])}):")
        for e in res["errores"]:
            print(f" {MARCA_ERROR}", e)
        print(f"AVISOS ({len(res['avisos'])}):")
        for a in res["avisos"]:
            print(" !", a)
        extra = {k: v for k, v in res.items() if k not in ("errores", "avisos")}
        print(extra)
    sys.exit(1 if res["errores"] else 0)


if __name__ == "__main__":
    main()
