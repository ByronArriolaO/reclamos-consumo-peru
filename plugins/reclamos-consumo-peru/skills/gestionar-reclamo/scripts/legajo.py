#!/usr/bin/env python3
"""Compila el legajo habilitante (10 Legajo habilitante.md) a partir de los archivos del caso.

Uso:
  python3 legajo.py CARPETA [--salida RUTA]

CARPETA = carpeta del caso r#_<prov>_<tema>/ (con *_expediente, *_reclamo-proveedor,
*_conciliacion-indecopi) o directamente la carpeta *_expediente.
No redacta nada nuevo: ordena lo que ya está en 02, 03, 06, 07, 08, 08b, la ficha y caso.json.
"Probado" = hecho de 02 cuya columna Estado empieza con "Acreditado" o "Indiciario".
Es el insumo de una eventual denuncia administrativa, que el plugin no redacta.
Códigos de salida: 0 correcto · 2 entrada inválida.
"""
import glob
import json
import os
import re
import sys
import unicodedata
from datetime import datetime

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    try:
        sys.stdout.reconfigure(errors='replace')
        sys.stderr.reconfigure(errors='replace')
    except Exception:
        pass

DOCS_CONCILIACION = re.compile(r'acta|audiencia|traslado|cargo|respuesta', re.I)


class ErrorEntrada(Exception):
    """Entrada inválida: se informa sin traceback."""


def sub(base, sufijo):
    if not base:
        return None
    hits = sorted(p for p in glob.glob(os.path.join(glob.escape(base), '*' + sufijo)) if os.path.isdir(p))
    return hits[0] if hits else None


def archivo(d, prefijo):
    if not d:
        return None
    hits = sorted(glob.glob(os.path.join(glob.escape(d), glob.escape(prefijo) + '*.md')))
    return hits[0] if hits else None


def leer(p):
    if not p or not os.path.exists(p):
        return ''
    try:
        with open(p, encoding='utf-8-sig') as fh:
            return fh.read()
    except UnicodeDecodeError:
        raise ErrorEntrada(f'"{os.path.basename(p)}" no está en UTF-8: guardarlo como UTF-8 y reintentar.')


def sin_comentarios(t):
    return re.sub(r'<!--.*?-->', '', t, flags=re.S)


def normal(s):
    s = unicodedata.normalize('NFD', (s or '').lower())
    s = ''.join(ch for ch in s if unicodedata.category(ch) != 'Mn')
    return re.sub(r'[\s*_`]+', '', s)


def celdas(linea):
    return [x.strip() for x in linea.strip().strip('|').split('|')]


def filas(texto, patron):
    out, vistos = [], set()
    for linea in sin_comentarios(texto).splitlines():
        m = re.match(r'^\s*\|\s*\**(' + patron + r')\**\s*\|(.*?)\|?\s*$', linea)
        if m and m.group(1) not in vistos:
            vistos.add(m.group(1))
            out.append([m.group(1)] + [x.strip() for x in m.group(2).split('|')])
    return out


def lineas_id(texto, patron):
    out = []
    for linea in sin_comentarios(texto).splitlines():
        m = re.match(r'^\s*[-*]?\s*(' + patron + r')\s*\|(.*)$', linea)
        if m:
            out.append([m.group(1)] + [x.strip() for x in m.group(2).split('|')])
    return out


def columna_estado(texto):
    """Índice de la columna "Estado" en la tabla de hechos de 02 (0 = columna H##). Sin encabezado: 6 (7.ª)."""
    for linea in sin_comentarios(texto).splitlines():
        if not linea.strip().startswith('|'):
            continue
        cs = celdas(linea)
        if not cs or re.match(r'^\**H\d{2}', cs[0]):
            continue
        norm = [normal(c) for c in cs]
        if 'estado' in norm and (re.match(r'^\**H(##)?\**$', cs[0].strip(), re.I) or any(n.startswith('hecho') for n in norm)):
            return norm.index('estado')
    return 6


def es_probado(fila, idx):
    if idx >= len(fila):
        return False
    v = re.sub(r'^[\s*_`]+', '', fila[idx]).lower()
    return v.startswith(('acreditado', 'indiciario'))


def seccion(texto, nombre):
    m = re.search(r'^##\s*' + nombre + r'[^\n]*\n(.*?)(?=^##\s|\Z)', texto, re.S | re.M | re.I)
    return m.group(1).strip() if m else ''


def seccion_por_encabezado(texto, contiene):
    """Copia literal de la sección cuyo encabezado (#, ##, ###…) contiene el texto dado, hasta el
    siguiente encabezado del mismo nivel o superior."""
    lineas = texto.splitlines()
    for i, linea in enumerate(lineas):
        m = re.match(r'^(#{1,6})\s+(.*)$', linea)
        if m and contiene.lower() in m.group(2).lower():
            nivel = len(m.group(1))
            cuerpo = []
            for sig in lineas[i + 1:]:
                m2 = re.match(r'^(#{1,6})\s', sig)
                if m2 and len(m2.group(1)) <= nivel:
                    break
                cuerpo.append(sig)
            return '\n'.join(cuerpo).strip()
    return ''


def tabla(encabezado, rows):
    if not rows:
        return '_Sin registros._\n'
    n = len(encabezado)
    out = '| ' + ' | '.join(encabezado) + ' |\n|' + '---|' * n + '\n'
    for r in rows:
        r = (list(r) + [''] * n)[:n]
        out += '| ' + ' | '.join(re.sub(r'\bNone\b', '—', str(x)).replace('\n', ' ') for x in r) + ' |\n'
    return out


def ubicar(ruta):
    """Devuelve (carpeta_caso, carpeta_expediente) a partir de la carpeta del caso o del expediente."""
    base = os.path.abspath(ruta.rstrip('/\\') or ruta)
    if not os.path.isdir(base):
        raise ErrorEntrada(f'No existe la carpeta "{ruta}".')
    exp = sub(base, '_expediente')
    if exp:
        return base, exp
    if base.lower().endswith('_expediente') or os.path.exists(os.path.join(base, 'caso.json')):
        return os.path.dirname(base), base
    raise ErrorEntrada('No se encontró la carpeta *_expediente: indicar la carpeta del caso o la del expediente.')


def generar(ruta, salida=None):
    base, exp = ubicar(ruta)
    p1 = sub(base, '_reclamo-proveedor')
    p2 = sub(base, '_conciliacion-indecopi')
    caso, aviso = {}, None
    pj = os.path.join(exp, 'caso.json')
    if os.path.exists(pj):
        try:
            with open(pj, encoding='utf-8-sig') as fh:
                caso = json.load(fh)
            if not isinstance(caso, dict):
                raise ValueError
        except (ValueError, UnicodeDecodeError):
            caso, aviso = {}, 'Aviso: caso.json dañado; el resumen queda incompleto (restáuralo o vuelve a crearlo con init).'

    t02, t03 = leer(archivo(exp, '02 ')), leer(archivo(exp, '03 '))
    t06, t07 = leer(archivo(exp, '06 ')), leer(archivo(exp, '07 '))
    t08, t08b = leer(archivo(p1, '08 ')), leer(archivo(p2, '08b'))
    ficha = leer(archivo(p2, 'Ficha Reclama Virtual'))

    hechos = filas(t02, r'H\d{2}')
    idx = columna_estado(t02)
    probados = [h for h in hechos if es_probado(h, idx)]
    brechas = filas(t03, r'B\d{2}') or lineas_id(t03, r'B\d{2}')
    preguntas = filas(t06, r'Q\d{2}')
    reqs = [s for s in lineas_id(t07, r'S\d{2}') if '(descartado)' not in ' '.join(s).lower()]
    prets = [p for p in lineas_id(t07, r'P\d{2}') if '(descartado)' not in ' '.join(p).lower()]
    res1 = {f[0]: f for f in filas(t08, r'S\d{2}')}
    res2 = {f[0]: f for f in filas(t08b, r'S\d{2}')}

    def aco(texto, paso):
        return [[f[0], str(paso)] + f[1:] for f in lineas_id(texto, r'A\d{2}')], \
               [[f[0], str(paso)] + f[1:] for f in lineas_id(texto, r'C\d{2}')], \
               [[f[0], str(paso)] + f[1:] for f in lineas_id(texto, r'O\d{2}')]
    a1, c1, o1 = aco(t08, 1)
    a2, c2, o2 = aco(t08b, 2)
    cprev = [[f[0], '0'] + f[1:] for f in lineas_id(t02 + '\n' + t03, r'C\d{2}')]
    ya = {x[0] for x in cprev}
    cprev += [[f[0], '0'] + f[1:] for f in filas(t02 + '\n' + t03, r'C\d{2}') if f[0] not in ya]

    docs = []
    if p2:
        for p in sorted(glob.glob(os.path.join(glob.escape(p2), '*'))):
            nombre = os.path.basename(p)
            if os.path.isfile(p) and not nombre[:1].isdigit() and DOCS_CONCILIACION.search(nombre):
                docs.append(nombre)

    plazos = seccion_por_encabezado(t02, 'Plazos computados')

    rc, rv = caso.get('reclamo') or {}, caso.get('rv') or {}
    rsp = caso.get('respuesta') or {}
    pa = caso.get('petitorio_aceptado', caso.get('reencuadre_aceptado'))
    L = []
    L.append(f"# Legajo habilitante — {caso.get('caso') or os.path.basename(base)} · {caso.get('proveedor') or ''}")
    L.append(f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')} · por: legajo.py (compilación; sin redacción nueva)\n")
    L.append("> Insumo para una eventual denuncia administrativa, que el plugin no redacta. Cada fila remite a su fuente en el expediente.\n")
    L.append("## 1. Resumen")
    L.append(tabla(['Campo', 'Valor'], [
        ['Dictamen de viabilidad', str(caso.get('dictamen'))],
        ['Petitorio aceptado por el usuario', json.dumps(pa, ensure_ascii=False) if pa is not None else '—'],
        ['Palanca', str(caso.get('palanca'))],
        ['Reclamo al proveedor', f"{rc.get('canal')} · {rc.get('codigo')} · {rc.get('fecha')} · vence {rc.get('vence')}"],
        ['Fecha de respuesta del proveedor', str(rsp.get('fecha'))],
        ['Respuesta en plazo', str(rsp.get('en_plazo'))],
        ['Clasificación de la respuesta', str(rsp.get('clasificacion'))],
        ['Reclama Virtual', f"{rv.get('id')} · {rv.get('fecha')} · {rv.get('categoria')} · {rv.get('oficina')}"],
        ['Audiencia', str((caso.get('audiencia') or {}).get('fecha'))],
        ['Resultado en INDECOPI', str(caso.get('resultado'))],
        ['Fecha límite de prescripción', str(caso.get('prescripcion'))],
    ]))
    L.append("## 2. Cronología probada (Acreditado o Indiciario)")
    L.append(tabla(['H##', 'Fecha', 'Hecho', 'Actor', 'Canal', 'Monto', 'Estado', 'Fuente'], probados))
    L.append(f"Hechos totales en 02: {len(hechos)} · probados: {len(probados)}.\n")
    if plazos:
        L.append("### Plazos computados (copia literal de 02)\n")
        L.append(plazos + '\n')
    L.append("## 3. Admisiones del proveedor (A##)")
    L.append(tabla(['A##', 'Paso', 'S##', 'Cita literal', 'Fuente'], a1 + a2))
    L.append("## 4. Contradicciones (C##)")
    L.append(tabla(['C##', 'Paso', 'Ref.', 'Descripción', 'Fuente'], cprev + c1 + c2))
    L.append("## 5. Omisiones y negativas sin sustento (O##)")
    L.append(tabla(['O##', 'Paso', 'S##', 'Lo que no acreditó', 'Fuente'], o1 + o2))
    L.append("## 6. Trazabilidad de los requerimientos")
    L.append(tabla(['S##', 'Vínculo', 'Requerimiento', 'Resultado Paso 1', 'Resultado Paso 2'],
                   [[s[0], s[1] if len(s) > 2 else '', s[-1], (res1.get(s[0]) or ['', ''])[1], (res2.get(s[0]) or ['', ''])[1]] for s in reqs]))
    L.append("## 7. Pretensiones")
    L.append(tabla(['P##', 'Texto'], [[p[0], p[-1]] for p in prets]))
    sol = seccion(sin_comentarios(ficha), 'SOLICITUD')
    if sol:
        L.append("**Solicitud presentada en Reclama Virtual:**\n")
        L.append('> ' + ' '.join(sol.split()) + '\n')
    L.append("## 8. Preguntas de investigación (Paso 0)")
    L.append(tabla(['Q##', 'Pregunta', 'Resuelve', 'Poseedor', 'Estado', 'Respuesta'], preguntas))
    L.append("## 9. Brechas abiertas (B##)")
    L.append(tabla(['B##', 'Detalle'], [[b[0], ' · '.join(b[1:])] for b in brechas]))
    L.append("## 10. Documentos de la conciliación")
    L.append('\n'.join(f'- {x}' for x in docs) + '\n' if docs else '_Sin documentos._\n')

    salida = salida or os.path.join(exp, '10 Legajo habilitante.md')
    with open(salida, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(L))
    if aviso:
        print(aviso)
    print(f'Escrito {salida}: {len(probados)} hechos probados · A {len(a1 + a2)} · C {len(cprev + c1 + c2)} · O {len(o1 + o2)} · S {len(reqs)}')


def main():
    argv = sys.argv[1:]
    salida = None
    if '--salida' in argv:
        i = argv.index('--salida')
        if i + 1 >= len(argv):
            print('Error: --salida requiere una ruta.', file=sys.stderr)
            sys.exit(2)
        salida = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    a = [x for x in argv if not x.startswith('--')]
    if not a:
        print(__doc__)
        sys.exit(2)
    try:
        generar(a[0], salida)
    except ErrorEntrada as e:
        print(f'Error: {e}', file=sys.stderr)
        sys.exit(2)
    except OSError as e:
        print(f'Error: no se pudo escribir o leer "{e.filename}": {e.strerror}.', file=sys.stderr)
        sys.exit(2)


if __name__ == '__main__':
    main()
