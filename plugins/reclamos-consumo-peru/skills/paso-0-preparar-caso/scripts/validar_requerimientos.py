#!/usr/bin/env python3
"""Valida que los requerimientos al proveedor sean precisos y concisos.

Uso:
  python3 validar_requerimientos.py ARCHIVO.md [--json]

Acepta tres tipos de archivo:
  - 07 Estrategia y petitorio.md   -> líneas "S01 | Q01, H04 | Requiero ..." y "P01 | ..."
                                      (se ignoran las líneas marcadas "(descartado)")
  - Reclamo proveedor - X.md       -> ítems con la marca [S01] / [P01] en la sección PEDIDO; un ítem
                                      puede ocupar varias líneas hasta el siguiente ítem numerado o marca
  - Ficha Reclama Virtual - X.md   -> oraciones que empiezan con "Requiero" en la sección SOLICITUD
                                      (con "categoria: llamadas" no se valida: la solicitud es fija)

Reglas (ver guia-preguntas-requerimientos.md §3):
  error: 0 o más de 4 requerimientos (0 se acepta en la ficha, con sin_requerimientos en 07
         y en un reclamo que solo tiene pretensión [P##])
  error: requerimiento de más de 350 caracteres
  error: signos de interrogación o fórmulas abiertas (por qué, cuál, cómo, explique, indique si);
         en la ficha se revisa toda la sección SOLICITUD
  error: no empieza con "Requiero" (o "Solicito que se remita/entregue")
  error: sin finalidad verificable ("de forma que se verifique", "a fin de verificar", "para verificar")
  error: sin un dato concreto (monto, fecha, mes, periodo, ciclo, n.º de operación o de reclamo,
         RUC, razón social, tarjeta o cuenta "terminada en 1234")
  error: palabra bloqueada por Reclama Virtual (palabras-bloqueadas.json)
  aviso: más de una oración en un requerimiento
  aviso: sin pretensión (P##) o pretensión condicionada mal formulada
  aviso: en la ficha, oraciones que no son requerimiento ni pretensión
Sale con código 1 si hay errores y con código 2 si el archivo no se puede leer.
"""
import json
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    try:
        sys.stdout.reconfigure(errors='replace')
        sys.stderr.reconfigure(errors='replace')
    except Exception:
        pass

MAX_REQ = 4
MAX_LEN = 350
AQUI = os.path.dirname(os.path.abspath(__file__))
BLOQ = os.path.normpath(os.path.join(AQUI, '..', '..', 'paso-2-reclama-virtual', 'references', 'palabras-bloqueadas.json'))

ABIERTAS = re.compile(r'(\bpor qué\b|\bcuál(es)?\b|\bcómo\b|\bexpl[ií]que(n)?\b|\bind[ií]que(n)? si\b|\bqué pasó\b|\ba qué se debe\b)', re.I)
INICIO = re.compile(r'^\s*(requiero|solicito que (se )?(me )?(remita|remitan|entregue|entreguen|proporcione|proporcionen))\b', re.I)
INICIO_REQ = re.compile(r'^(requiero|solicito que (se )?(me )?(remit|entreg|proporcion))', re.I)
INICIO_PRET = re.compile(r'^(solicito|de no acreditarse)', re.I)
FINALIDAD = re.compile(r'(de forma que se verifique|de modo que se verifique|a fin de verificar|para verificar|que permita verificar|de forma que se acredite)', re.I)
MESES = r'\b(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|setiembre|octubre|noviembre|diciembre)\b'
DATO = re.compile(
    r'(S/\s?\d|US\$\s?\d|\$\s?\d|\d{1,2}/\d{1,2}/\d{2,4}|\b\d{4,}\b|\bciclo\s+\d+|\bEECC\s*\d+|' + MESES +
    r'|\b\d+[.,]\d{2}\b|\bRUC\b|\braz[oó]n social\b|\bterminad[ao] en\s+\d{4}\b'
    r'|\b(c[oó]digo|n[uú]mero|n\.[º°]|nro\.?)\s+(de(l)?\s+)?(reclamo|operaci[oó]n|pedido|contrato)\b'
    r'|\b(reclamo|operaci[oó]n)\s+(n\.[º°]|nro\.?|n[uú]m\.?)\s*\S*\d)', re.I)

# Abreviaturas que no cierran oración. Las de SIEMPRE nunca terminan una oración (van antes de un
# número o un nombre); las de FINAL pueden cerrar la oración si les sigue una mayúscula.
ABREV_SIEMPRE = [r'N\.º', r'N\.°', r'n\.º', r'n\.°', r'Nro\.', r'arts\.', r'art\.', r'Res\.', r'D\.S\.',
                 r'Sra\.', r'Sr\.', r'pp\.', r'p\.', r'inc\.', r'núm\.']
ABREV_FINAL = [r'E\.I\.R\.L\.', r'S\.A\.C\.', r'S\.R\.L\.', r'S\.A\.', r'etc\.']
PUNTO = '․'   # marcador temporal para los puntos protegidos


def proteger(txt):
    """Reemplaza los puntos de las abreviaturas por un marcador para no partir oraciones en ellas."""
    for a in ABREV_SIEMPRE:
        txt = re.sub(r'(?<![\wÁÉÍÓÚáéíóúñÑ])' + a, lambda m: m.group(0).replace('.', PUNTO), txt, flags=re.I)
    for a in ABREV_FINAL:
        def rep(m):
            s = m.group(1)
            sigue = m.group(2)
            if sigue is not None and re.match(r'\s+[A-ZÁÉÍÓÚÑ¿(\d]', sigue):
                return s[:-1].replace('.', PUNTO) + '.' + sigue      # cierra la oración
            return s.replace('.', PUNTO) + (sigue or '')
        txt = re.sub(r'(?<![\wÁÉÍÓÚáéíóúñÑ])(' + a + r')(\s+\S)?', rep, txt, flags=re.I)
    return txt


def restaurar(txt):
    return txt.replace(PUNTO, '.')


def cargar_bloqueadas():
    try:
        with open(BLOQ, encoding='utf-8') as fh:
            d = json.load(fh)
    except Exception:
        return []
    out = []
    for k, v in d.items():
        if k.startswith('_') or not isinstance(v, list):
            continue
        out += [x for x in v if isinstance(x, str) and x.strip()]
    return out


def seccion(texto, nombre):
    m = re.search(r'^##\s*' + nombre + r'[^\n]*\n(.*?)(?=^##\s|\Z)', texto, re.S | re.M | re.I)
    return m.group(1) if m else ''


def sin_comentarios(t):
    return re.sub(r'<!--.*?-->', '', t, flags=re.S)


def es_descartado(linea):
    return '(descartado)' in linea.lower()


def items_reclamo(t):
    """Ítems del PEDIDO de un reclamo. Un ítem empieza en una línea numerada o con viñeta, o en una
    línea con una marca [S##]/[P##] cuando el ítem actual ya tiene la suya; termina en una línea en
    blanco, un encabezado o una línea "Clave: valor" (p. ej., "Plazo y canal: ...")."""
    zona = seccion(t, 'PEDIDO') or t
    bloques, actual = [], None
    for linea in zona.splitlines():
        s = linea.strip()
        if not s or s.startswith('#') or re.match(r'^[A-Za-zÁÉÍÓÚáéíóúÑñ ]{2,40}:\s', s) and not re.search(r'\[[SP]\d{2}\]', s):
            actual = None
            continue
        tiene_marca = bool(re.search(r'\[[SP]\d{2}\]', s))
        nuevo = re.match(r'^(\(?\d+[.)]|[-*•])\s+', s)
        if actual is None or nuevo or (tiene_marca and re.search(r'\[[SP]\d{2}\]', ' '.join(actual))):
            actual = [s]
            bloques.append(actual)
        else:
            actual.append(s)
    reqs, prets = [], []
    for b in bloques:
        txt = ' '.join(b)
        if es_descartado(txt):
            continue
        ms = re.search(r'\[(S\d{2})\]', txt)
        mp = re.search(r'\[(P\d{2})\]', txt)
        limpio = re.sub(r'\[[SP]\d{2}\]', '', txt)
        limpio = re.sub(r'^\s*(\(?\d+[.)]|[-*•])\s*', '', limpio)
        limpio = ' '.join(limpio.split())
        if ms:
            reqs.append((ms.group(1), limpio))
        elif mp:
            prets.append((mp.group(1), limpio))
    return reqs, prets


def oraciones_solicitud(sol):
    """Parte la sección SOLICITUD en oraciones (protegiendo abreviaturas). También corta tras '; '
    cuando sigue un requerimiento o una pretensión, y quita el prefijo 'Por favor, '."""
    lineas = [re.sub(r'^\s*(\(?\d{1,2}[.)]|[-*•])\s+', '', x) for x in sol.splitlines()]
    plano = ' '.join(' '.join(lineas).split())
    plano = re.sub(r'(?<=[.;:])\s+\(?\d{1,2}[.)]\s+(?=[A-ZÁÉÍÓÚÑ])', ' ', plano)
    plano = proteger(plano)
    partes = re.split(r'(?<=[.!?])\s+(?=[¿(]?[A-ZÁÉÍÓÚÑ\d])|;\s+(?=(?:por favor,\s*)?(?:requiero|solicito|de no acreditarse))', plano, flags=re.I)
    out = []
    for p in partes:
        p = restaurar(p).strip()
        p = re.sub(r'^por favor,\s*', '', p, flags=re.I).strip()
        if p:
            out.append(p[0].upper() + p[1:])
    return out


def extraer(texto):
    """Devuelve (tipo, requerimientos[(id, texto)], pretensiones[(id, texto)], extra)."""
    t = sin_comentarios(texto)
    reqs, prets, extra = [], [], {}
    lineas_s = re.findall(r'^\s*[-*]?\s*(S\d{2})\s*\|(.*)$', t, re.M)
    lineas_p = re.findall(r'^\s*[-*]?\s*(P\d{2})\s*\|(.*)$', t, re.M)
    prets07 = [(pid, resto.split('|')[-1].strip()) for pid, resto in lineas_p if not es_descartado(resto)]
    if lineas_s:
        reqs = [(sid, resto.split('|')[-1].strip()) for sid, resto in lineas_s if not es_descartado(resto)]
        if not reqs and re.search(r'^\s*sin_requerimientos\s*:\s*\S', t, re.M | re.I):
            return '07-sin', [], prets07, extra
        return '07', reqs, prets07, extra
    if re.search(r'^\s*sin_requerimientos\s*:\s*\S', t, re.M | re.I):
        return '07-sin', [], prets07, extra
    if re.search(r'\[[SP]\d{2}\]', t):
        reqs, prets = items_reclamo(t)
        return ('reclamo' if reqs else 'reclamo-sin'), reqs, prets, extra
    sol = seccion(t, 'SOLICITUD')
    if sol.strip() or re.search(r'^##\s*SOLICITUD', t, re.M | re.I):
        if re.search(r'^\s*categor[ií]a\s*:\s*llamadas\b', t, re.M | re.I):
            return 'ficha-llamadas', [], [], extra
        extra['solicitud'] = sol
        otras = []
        n = 0
        for p in oraciones_solicitud(sol):
            if INICIO_REQ.match(p):
                n += 1
                reqs.append((f'S?{n}', p))
            elif INICIO_PRET.match(p):
                prets.append(('P?', p))
            else:
                otras.append(p)
        extra['otras'] = otras
        return 'ficha', reqs, prets, extra
    return 'desconocido', reqs, prets, extra


def oraciones(txt):
    limpio = proteger(txt.strip())
    return [o for o in re.split(r'(?<=[.!])\s+(?=[A-ZÁÉÍÓÚÑ])', limpio) if o.strip()]


def buscar_bloqueada(txt, bloq):
    for b in bloq:
        try:
            hit = re.search('(' + b + ')', txt, re.I)
        except re.error:
            hit = b.lower() in txt.lower()
        if hit:
            return b
    return None


def validar_texto(texto, path='(texto)'):
    tipo, reqs, prets, extra = extraer(texto)
    errores, avisos = [], []
    bloq = cargar_bloqueadas()

    if tipo == 'ficha-llamadas':
        avisos.append('Ficha de la categoría llamadas: la SOLICITUD es fija en el portal; no se valida.')
        return {'archivo': path, 'tipo': tipo, 'requerimientos': 0, 'pretensiones': 0,
                'errores': [], 'avisos': avisos, 'ok': True}
    if tipo == '07-sin':
        avisos.append('Sin requerimientos (declarado con sin_requerimientos). Verificar que 06 no tenga datos en poder del proveedor pendientes.')
    if tipo == 'reclamo-sin':
        avisos.append('El PEDIDO solo tiene pretensión [P##], sin requerimientos [S##]. Verificar que 07 declare sin_requerimientos.')
    if tipo == 'desconocido':
        errores.append('No se encontraron requerimientos: use filas "S01 | ... | Requiero ..." (07), marcas [S01] (reclamo) o la sección ## SOLICITUD (ficha).')
    if not reqs and tipo == '07':
        errores.append('No hay requerimientos vigentes. Si de verdad no hace falta ninguno, declarar en 07 la línea "sin_requerimientos: <motivo>".')
    if len(reqs) > MAX_REQ:
        errores.append(f'{len(reqs)} requerimientos: el máximo es {MAX_REQ}. Agrupar por objeto (ideal 1 o 2).')

    if tipo == 'ficha':
        sol = extra.get('solicitud', '')
        if '?' in sol or '¿' in sol:
            errores.append('SOLICITUD: contiene signos de interrogación. Al proveedor no se le pregunta: reformular como "Requiero …, de forma que se verifique …".')
        m = ABIERTAS.search(sol)
        if m:
            errores.append(f'SOLICITUD: fórmula abierta "{m.group(0)}". Pedir un documento o una demostración concreta.')
        for o in extra.get('otras', []):
            corto = o if len(o) <= 80 else o[:77] + '...'
            avisos.append(f'SOLICITUD: la oración «{corto}» no es requerimiento ("Requiero …") ni pretensión ("Solicito …" / "De no acreditarse …"). Verificar que haga falta.')
        if not prets:
            avisos.append('SOLICITUD: no hay pretensión ("Solicito …" o "De no acreditarse lo requerido, solicito …").')

    for rid, txt in reqs:
        if len(txt) > MAX_LEN:
            errores.append(f'{rid}: {len(txt)} caracteres (máx. {MAX_LEN}). Recortar a una sola oración.')
        if tipo != 'ficha':
            if '?' in txt or '¿' in txt:
                errores.append(f'{rid}: contiene una pregunta. Reformular como "Requiero …, de forma que se verifique …".')
            m = ABIERTAS.search(txt)
            if m:
                errores.append(f'{rid}: fórmula abierta "{m.group(0)}". Pedir un documento o una demostración concreta.')
        if not INICIO.search(txt):
            errores.append(f'{rid}: debe empezar con "Requiero".')
        if not FINALIDAD.search(txt):
            errores.append(f'{rid}: falta la finalidad verificable (", de forma que se verifique …").')
        if not DATO.search(txt):
            errores.append(f'{rid}: falta un dato concreto (monto, fecha, mes, periodo, ciclo, n.º de operación o de reclamo, RUC).')
        if len(oraciones(txt)) > 1:
            avisos.append(f'{rid}: tiene más de una oración; dejar una sola.')
        b = buscar_bloqueada(txt, bloq)
        if b:
            errores.append(f'{rid}: palabra bloqueada por Reclama Virtual: "{b}".')

    if tipo in ('07', 'reclamo', '07-sin', 'reclamo-sin'):
        if not prets:
            avisos.append('No hay pretensión (P##). El requerimiento no reemplaza a la pretensión económica.')
        forma = re.search(r'^\s*forma:\s*(\w+)', sin_comentarios(texto), re.M | re.I)
        for pid, txt in prets:
            if forma and forma.group(1).lower() == 'condicionada' and not re.match(r'de no acreditarse', txt, re.I):
                avisos.append(f'{pid}: la forma es "condicionada"; empezar con "De no acreditarse lo requerido, solicito …".')
    for pid, txt in prets:
        b = buscar_bloqueada(txt, bloq)
        if b:
            errores.append(f'{pid}: palabra bloqueada por Reclama Virtual: "{b}".')
    return {'archivo': path, 'tipo': tipo, 'requerimientos': len(reqs), 'pretensiones': len(prets),
            'errores': errores, 'avisos': avisos, 'ok': not errores}


def validar(path):
    with open(path, encoding='utf-8-sig') as fh:
        texto = fh.read()
    return validar_texto(texto, path)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if not args:
        print(__doc__)
        sys.exit(2)
    try:
        r = validar(args[0])
    except FileNotFoundError:
        print(f'Error: no existe el archivo "{args[0]}".', file=sys.stderr)
        sys.exit(2)
    except IsADirectoryError:
        print(f'Error: "{args[0]}" es una carpeta; indicar el archivo .md.', file=sys.stderr)
        sys.exit(2)
    except UnicodeDecodeError:
        print(f'Error: "{args[0]}" no está en UTF-8. Guardarlo como UTF-8 y reintentar.', file=sys.stderr)
        sys.exit(2)
    except OSError as e:
        print(f'Error: no se pudo leer "{args[0]}": {e.strerror}.', file=sys.stderr)
        sys.exit(2)
    if '--json' in sys.argv:
        print(json.dumps(r, ensure_ascii=False, indent=1))
    else:
        print(f"{r['archivo']} ({r['tipo']}): {r['requerimientos']} requerimiento(s), {r['pretensiones']} pretensión(es)")
        for e in r['errores']:
            print('  ERROR ', e)
        for a in r['avisos']:
            print('  AVISO ', a)
        print('  OK' if r['ok'] else f"  {len(r['errores'])} error(es)")
    sys.exit(0 if r['ok'] else 1)


if __name__ == '__main__':
    main()
