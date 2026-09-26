#!/usr/bin/env python3
"""Estado legible por el plugin (caso.json) y compuertas entre pasos.

Uso:
  python3 estado.py init      CARPETA --caso r1 --proveedor "Proveedor Ejemplo S.A.C."
  python3 estado.py ver       CARPETA
  python3 estado.py set       CARPETA CLAVE VALOR     (clave con puntos: reclamo.codigo; VALOR se lee como JSON si se puede)
  python3 estado.py sync      CARPETA                 (relee 00, 06, 07, 08, 08b y 09)
  python3 estado.py compuerta CARPETA 0-1|1-2|cierre  (alias: 2-cierre; código de salida 1 si no se cumple)

CARPETA = r#_<prov>_expediente/ o la carpeta del caso r#_<prov>_<tema>/ (si contiene una subcarpeta
*_expediente, se usa esa). Las carpetas hermanas *_reclamo-proveedor y *_conciliacion-indecopi se
ubican solas. Códigos de salida: 0 correcto · 1 compuerta no cumplida · 2 entrada inválida.

Campos de caso.json que se registran con set (no están en los archivos):
  paso                0 | 1 | 2 | "cerrado"
  petitorio_aceptado  true | "original" | false | null   (alias de lectura: reencuadre_aceptado)
  excepcion           null | "llamadas" | "urgencia"
  reclamo             {"canal", "codigo", "fecha", "vence"}
  oferta_rechazada    true | false
  rv                  {"id", "fecha", "categoria", "oficina"}
  audiencia.fecha, piso, cierre_paso (1 si el caso se cierra en el Paso 1)
  resultado           "acuerdo" | "sin acuerdo" | "incumplido"
Campos que llena sync: dictamen y prescripcion (00); Q y q_tabla_ok (06); S, P, palanca,
forma_pretension y sin_requerimientos_justificado (07); respuesta.clasificacion, respuesta.en_plazo,
respuesta.fecha y A/C/O (08, 08b); audiencia.fecha (línea "fecha_audiencia:" de 09, si existe).
No usa dependencias externas.
"""
import glob
import json
import os
import re
import subprocess
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

AQUI = os.path.dirname(os.path.abspath(__file__))
VALIDADOR = os.path.normpath(os.path.join(AQUI, '..', '..', 'paso-0-preparar-caso', 'scripts', 'validar_requerimientos.py'))

PLANTILLA = {
    "caso": None, "proveedor": None, "paso": 0, "situacion": "Preparación",
    "dictamen": None, "reencuadre": False, "petitorio_aceptado": None, "excepcion": None,
    "palanca": None, "forma_pretension": None,
    "reclamo": {"canal": None, "codigo": None, "fecha": None, "vence": None},
    "respuesta": {"fecha": None, "clasificacion": None, "en_plazo": None},
    "oferta_rechazada": None,
    "rv": {"id": None, "fecha": None, "categoria": None, "oficina": None},
    "audiencia": {"fecha": None}, "piso": None, "cierre_paso": None,
    "resultado": None, "prescripcion": None,
    "sin_requerimientos_justificado": False, "q_tabla_ok": None,
    "Q": {}, "S": {}, "P": {}, "A": [], "C": [], "O": [],
    "actualizado": None,
}
ESTADOS_Q = ('pendiente', 'respondida', 'afirmada', 'sin respuesta', 'descartada')
CLASIFICACIONES = ('favorable', 'oferta', 'parcial', 'desfavorable', 'desfavorable fundada', 'sin respuesta')
VALORES = {
    'paso': (0, 1, 2, 'cerrado'),
    'petitorio_aceptado': (True, 'original', False, None),
    'excepcion': (None, 'llamadas', 'urgencia'),
    'resultado': (None, 'acuerdo', 'sin acuerdo', 'incumplido'),
}
FECHA = re.compile(r'\b(\d{2}/\d{2}/\d{4})\b')


class ErrorEntrada(Exception):
    """Entrada inválida: se informa sin traceback y con código 2."""


# ---------------------------------------------------------------- carpetas y archivos

def resolver_carpeta(d):
    """Acepta la carpeta del expediente o la del caso (usa su subcarpeta *_expediente)."""
    d = os.path.abspath(d.rstrip('/\\') or d)
    if not d.lower().endswith('_expediente') and os.path.isdir(d):
        subs = sorted(p for p in glob.glob(os.path.join(glob.escape(d), '*_expediente')) if os.path.isdir(p))
        if subs:
            return subs[0]
    return d


def ruta_json(d):
    return os.path.join(d, 'caso.json')


def completar(c, base):
    """Agrega las claves de la plantilla que falten (compatibilidad con caso.json antiguos)."""
    for k, v in base.items():
        if k not in c:
            c[k] = json.loads(json.dumps(v))
        elif isinstance(v, dict) and isinstance(c[k], dict):
            completar(c[k], v)
        elif isinstance(v, dict) and c[k] is None:
            c[k] = json.loads(json.dumps(v))
    return c


def cargar(d):
    p = ruta_json(d)
    if not os.path.exists(p):
        raise ErrorEntrada(f'No existe {p}. Ejecutar primero: estado.py init "{d}" --caso r# --proveedor "..."')
    try:
        with open(p, encoding='utf-8-sig') as fh:
            c = json.load(fh)
        if not isinstance(c, dict):
            raise ValueError
    except (ValueError, UnicodeDecodeError):
        raise ErrorEntrada('caso.json dañado: restáuralo o vuelve a crearlo con init')
    # alias antiguo: reencuadre_aceptado -> petitorio_aceptado
    if c.get('petitorio_aceptado') is None and c.get('reencuadre_aceptado') is not None:
        c['petitorio_aceptado'] = c['reencuadre_aceptado']
    c.pop('reencuadre_aceptado', None)
    return completar(c, PLANTILLA)


def guardar(d, c):
    c['actualizado'] = datetime.now().strftime('%d/%m/%Y %H:%M')
    tmp = ruta_json(d) + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as fh:
        json.dump(c, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, ruta_json(d))


def hermana(d, sufijo):
    base = os.path.dirname(os.path.abspath(d))
    hits = sorted(p for p in glob.glob(os.path.join(glob.escape(base), '*' + sufijo)) if os.path.isdir(p))
    return hits[0] if hits else None


def archivo(d, prefijo, ext='.md'):
    if not d:
        return None
    hits = sorted(glob.glob(os.path.join(glob.escape(d), glob.escape(prefijo) + '*' + ext)))
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
    """Minúsculas, sin tildes, sin **, _ ni espacios (para comparar etiquetas de tabla)."""
    s = unicodedata.normalize('NFD', (s or '').lower())
    s = ''.join(ch for ch in s if unicodedata.category(ch) != 'Mn')
    return re.sub(r'[\s*_`]+', '', s)


def limpiar_celda(s):
    return re.sub(r'[*_`]+', '', s or '').strip()


def filas(texto, patron, descartar=False):
    """Filas de tabla markdown cuya primera celda coincide con el patrón (p. ej. Q\\d{2}).
    Se queda con la primera aparición de cada ID (la tabla principal)."""
    out, vistos = [], set()
    for linea in sin_comentarios(texto).splitlines():
        m = re.match(r'^\s*\|\s*\**(' + patron + r')\**\s*\|(.*?)\|?\s*$', linea)
        if not m or m.group(1) in vistos:
            continue
        if descartar and '(descartado)' in linea.lower():
            vistos.add(m.group(1))
            continue
        vistos.add(m.group(1))
        out.append([m.group(1)] + [x.strip() for x in m.group(2).split('|')])
    return out


def lineas_id(texto, patron, descartar=False):
    out = []
    for linea in sin_comentarios(texto).splitlines():
        m = re.match(r'^\s*[-*]?\s*(' + patron + r')\s*\|(.*)$', linea)
        if m:
            if descartar and '(descartado)' in linea.lower():
                continue
            out.append([m.group(1)] + [x.strip() for x in m.group(2).split('|')])
    return out


def linea_clave(texto, clave):
    m = re.search(r'^\s*[-*]?\s*`?' + clave + r'`?\s*:\s*(.*?)\s*$', sin_comentarios(texto), re.M | re.I)
    if not m:
        return None
    v = limpiar_celda(m.group(1)).strip()
    return v or None


def norm_clasificacion(v):
    if not v:
        return None
    v = ' '.join(re.sub(r'[*_`.]+', ' ', v.lower()).split())
    return v or None


def fila_ficha(texto, etiqueta):
    """Valor de la fila '| etiqueta | valor |' de una tabla (compara sin **, _ ni espacios)."""
    obj = normal(etiqueta)
    for linea in sin_comentarios(texto).splitlines():
        celdas = [x for x in linea.strip().strip('|').split('|')]
        if len(celdas) >= 2 and linea.strip().startswith('|') and normal(celdas[0]) == obj:
            return limpiar_celda(celdas[1])
    return None


# ---------------------------------------------------------------- sync

def sync(d):
    c = cargar(d)
    # 00: dictamen y prescripción
    p00 = archivo(d, '00 ')
    if p00:
        t00 = leer(p00)
        dic = fila_ficha(t00, 'Dictamen de viabilidad')
        c['dictamen'] = dic if dic and ' / ' not in dic else None
        c['reencuadre'] = bool(c['dictamen'] and 'reencuadre' in c['dictamen'].lower())
        pres = fila_ficha(t00, 'Fecha límite de prescripción')
        m = FECHA.search(pres or '')
        if m:
            c['prescripcion'] = m.group(1)
    # Reinicio de lo que se lee de 06 y 07 (no conservar valores viejos)
    c['Q'], c['S'], c['P'] = {}, {}, {}
    c['A'], c['C'], c['O'] = [], [], []
    c['palanca'] = None
    c['forma_pretension'] = None
    c['sin_requerimientos_justificado'] = False
    # 06: preguntas
    p06 = archivo(d, '06 ')
    if p06:
        for f in filas(leer(p06), r'Q\d{2}', descartar=True):
            c['Q'][f[0]] = {"pregunta": f[1] if len(f) > 1 else '', "resuelve": f[2] if len(f) > 2 else '',
                            "poseedor": limpiar_celda(f[3]) if len(f) > 3 else '',
                            "estado": limpiar_celda(f[4]) if len(f) > 4 else ''}
        c['q_tabla_ok'] = bool(c['Q']) or bool(filas(leer(p06), r'Q\d{2}'))
    else:
        c['q_tabla_ok'] = None
    # 07: requerimientos y pretensión
    t07 = leer(archivo(d, '07 '))
    if t07:
        c['S'] = {f[0]: {"vinculo": f[1] if len(f) > 2 else '', "texto": f[-1]} for f in lineas_id(t07, r'S\d{2}', descartar=True)}
        c['P'] = {f[0]: f[-1] for f in lineas_id(t07, r'P\d{2}', descartar=True)}
        m = re.search(r'^\s*forma:\s*(\w+)', sin_comentarios(t07), re.M | re.I)
        if m:
            c['forma_pretension'] = m.group(1).lower()
        m = re.search(r'^##\s*Palanca[^\n]*\n+([^\n#]+)', sin_comentarios(t07), re.M)
        if m and m.group(1).strip():
            c['palanca'] = m.group(1).strip()
        c['sin_requerimientos_justificado'] = bool(re.search(r'^\s*sin_requerimientos\s*:\s*\S', sin_comentarios(t07), re.M | re.I))
    # 08 y 08b: resultados
    for carpeta, pref, etapa in ((hermana(d, '_reclamo-proveedor'), '08 ', 1), (hermana(d, '_conciliacion-indecopi'), '08b', 2)):
        t = leer(archivo(carpeta, pref))
        if not t:
            continue
        for f in filas(t, r'S\d{2}'):
            if f[0] in c['S']:
                c['S'][f[0]][f'resultado_paso{etapa}'] = f[1] if len(f) > 1 else ''
        if etapa == 1:
            c['respuesta']['clasificacion'] = norm_clasificacion(linea_clave(t, 'clasificacion'))
            c['respuesta']['en_plazo'] = linea_clave(t, 'en_plazo')
            fr = linea_clave(t, 'fecha_respuesta')
            m = FECHA.search(fr or '')
            c['respuesta']['fecha'] = m.group(1) if m else None
        c['A'] += [{"id": f[0], "paso": etapa, "texto": ' | '.join(f[1:])} for f in lineas_id(t, r'A\d{2}')]
        c['C'] += [{"id": f[0], "paso": etapa, "texto": ' | '.join(f[1:])} for f in lineas_id(t, r'C\d{2}')]
        c['O'] += [{"id": f[0], "paso": etapa, "texto": ' | '.join(f[1:])} for f in lineas_id(t, r'O\d{2}')]
    # 09: fecha de audiencia (opcional)
    t09 = leer(archivo(hermana(d, '_conciliacion-indecopi'), '09 '))
    m = FECHA.search(linea_clave(t09, 'fecha_audiencia') or '') if t09 else None
    if m:
        c['audiencia']['fecha'] = m.group(1)
    guardar(d, c)
    return c


# ---------------------------------------------------------------- compuertas

def compuerta(d, g):
    if g == '2-cierre':
        g = 'cierre'
    if g not in ('0-1', '1-2', 'cierre'):
        raise ErrorEntrada('Compuerta no reconocida: use 0-1, 1-2 o cierre (alias: 2-cierre).')
    c = sync(d)
    falta, avisos = [], []
    if g == '0-1':
        dic = (c.get('dictamen') or '').lower()
        if not dic.startswith('procede'):
            falta.append(f'Dictamen favorable en 00, fila "Dictamen de viabilidad" (actual: {c.get("dictamen")}).')
        pa = c.get('petitorio_aceptado')
        if pa not in (True, 'original'):
            falta.append('Aceptación del petitorio por el usuario: set … petitorio_aceptado true, o \'"original"\' si mantiene su pedido original.')
        elif pa == 'original':
            avisos.append('Aviso: el usuario mantiene su pedido original; dejar la advertencia en la bitácora.')
        for pref in ('00 ', '04 ', '05 ', '06 ', '07 '):
            if not archivo(d, pref):
                falta.append(f'Archivo {pref.strip()} del expediente.')
        if archivo(d, '06 ') and c.get('q_tabla_ok') is False:
            falta.append('06 no tiene la tabla de preguntas (filas "| Q01 | … |"); ver el formato en plantilla-expediente.md.')
        pend = [k for k, v in c['Q'].items() if v.get('estado', '').lower().startswith('pendiente') or not v.get('estado')]
        if pend:
            falta.append('Preguntas de 06 sin resolver con el consumidor (Pendiente o sin estado): ' + ', '.join(pend))
        cubiertas = ' '.join(v.get('vinculo', '') for v in c['S'].values())
        sueltas = [k for k, v in c['Q'].items()
                   if v.get('poseedor', '').lower().startswith('proveedor')
                   and v.get('estado', '').lower().startswith(('afirmada', 'sin respuesta'))
                   and not re.search(r'\b' + k + r'\b', cubiertas)]
        if sueltas:
            falta.append('Datos en poder del proveedor sin requerimiento: ' + ', '.join(sueltas) + ' (citarlos en el vínculo de un S## o marcarlos Descartada con motivo en 06).')
        n = len(c['S'])
        if n == 0 and not c.get('sin_requerimientos_justificado'):
            falta.append('Requerimientos S## en 07 (o la línea "sin_requerimientos: <motivo>" en 07).')
        if n > 4:
            falta.append(f'{n} requerimientos: máximo 4.')
        if not c['P']:
            falta.append('Pretensión P## en 07.')
        p07 = archivo(d, '07 ')
        if p07 and os.path.exists(VALIDADOR):
            env = dict(os.environ, PYTHONIOENCODING='utf-8')
            r = subprocess.run([sys.executable, VALIDADOR, p07, '--json'], capture_output=True,
                               text=True, encoding='utf-8', errors='replace', env=env)
            try:
                res = json.loads(r.stdout)
                for e in res['errores']:
                    falta.append('validar_requerimientos: ' + e)
            except Exception:
                falta.append('No se pudo ejecutar validar_requerimientos.py sobre 07: ' + (r.stderr.strip().splitlines() or ['sin detalle'])[-1])
    elif g == '1-2':
        exc = c.get('excepcion')
        rc = c.get('reclamo') or {}
        if exc == 'llamadas':
            avisos.append('Excepción "llamadas": Reclama Virtual no exige reclamo previo; se puede pasar al Paso 2.')
        elif exc == 'urgencia':
            avisos.append('Excepción "urgencia": se pasa al Paso 2 sin esperar la respuesta; dejar constancia en la bitácora.')
            if not (rc.get('codigo') and rc.get('fecha')):
                falta.append('Constancia del reclamo al proveedor (reclamo.codigo y reclamo.fecha).')
        else:
            if not (rc.get('codigo') and rc.get('fecha')):
                falta.append('Constancia del reclamo al proveedor (reclamo.codigo y reclamo.fecha).')
            if not archivo(hermana(d, '_reclamo-proveedor'), '08 '):
                falta.append('08 Análisis de respuesta en la carpeta del Paso 1.')
            clas = c['respuesta'].get('clasificacion') or ''
            if clas and clas not in CLASIFICACIONES:
                avisos.append(f'Aviso: clasificacion "{clas}" no reconocida ({" | ".join(CLASIFICACIONES)}).')
            if clas.startswith('favorable'):
                falta.append('La respuesta fue favorable: corresponde cerrar (resultado acuerdo), no elevar.')
            elif clas == 'desfavorable fundada':
                falta.append('La respuesta es desfavorable pero fundada: corresponde cerrar, no elevar (salvo hecho nuevo).')
            elif clas == 'oferta':
                if c.get('oferta_rechazada') is not True:
                    falta.append('Hay una oferta del proveedor: el usuario debe decidir (si la rechaza: set … oferta_rechazada true).')
            elif not (c['A'] or c['C'] or c['O'] or clas in ('parcial', 'desfavorable', 'sin respuesta')):
                falta.append('Motivo para elevar: clasificacion parcial, desfavorable o sin respuesta en 08, o A##/C##/O## registrados.')
    else:
        res = (c.get('resultado') or '').lower() if isinstance(c.get('resultado'), str) else ''
        if res not in ('acuerdo', 'sin acuerdo', 'incumplido'):
            falta.append('resultado = acuerdo | sin acuerdo | incumplido (set … resultado \'"sin acuerdo"\').')
        cierre_p1 = (str(c.get('cierre_paso')) == '1'
                     or (c['respuesta'].get('clasificacion') or '') in ('favorable', 'desfavorable fundada'))
        if res == 'sin acuerdo' and not cierre_p1 and not (c.get('rv') or {}).get('id'):
            falta.append('ID del reclamo en Reclama Virtual (rv.id).')
        if res in ('sin acuerdo', 'incumplido') and not archivo(d, '10 '):
            falta.append('10 Legajo habilitante (legajo.py).')
    return falta, avisos


# ---------------------------------------------------------------- set

def valor(v):
    try:
        return json.loads(v)
    except Exception:
        return v


def normalizar_set(clave, v):
    if clave == 'reencuadre_aceptado':
        clave = 'petitorio_aceptado'
    if isinstance(v, str):
        low = v.strip().lower()
        if clave in VALORES and low in ('null', 'none', ''):
            v = None
        elif clave == 'petitorio_aceptado' and low in ('true', 'si', 'sí'):
            v = True
        elif clave == 'petitorio_aceptado' and low in ('false', 'no'):
            v = False
        elif clave in VALORES:
            v = low
    if clave == 'paso' and isinstance(v, str) and v.isdigit():
        v = int(v)
    if clave == 'petitorio_aceptado':
        invalido = not (v is None or isinstance(v, bool) or v == 'original')
    elif clave in VALORES:
        invalido = isinstance(v, bool) or v not in VALORES[clave]
    else:
        invalido = False
    if invalido:
        permitidos = ' | '.join('null' if x is None else json.dumps(x, ensure_ascii=False) for x in VALORES[clave])
        raise ErrorEntrada(f'Valor no válido para {clave}: {v!r}. Valores permitidos: {permitidos}.')
    if clave in ('reclamo.fecha', 'reclamo.vence', 'rv.fecha', 'audiencia.fecha', 'respuesta.fecha', 'prescripcion') \
            and v is not None and not (isinstance(v, str) and re.fullmatch(r'\d{2}/\d{2}/\d{4}', v)):
        raise ErrorEntrada(f'{clave}: use el formato DD/MM/AAAA (recibido: {v!r}).')
    return clave, v


# ---------------------------------------------------------------- CLI

def ejecutar(a):
    if len(a) < 2:
        print(__doc__)
        return 2
    cmd, d = a[0], a[1]
    if cmd != 'init' or os.path.isdir(d):
        d = resolver_carpeta(d)
    if cmd == 'init':
        d = os.path.abspath(d)
        p = ruta_json(d)
        if os.path.exists(p):
            print(f'Ya existe {p}; no se sobrescribe.')
            return 0
        c = json.loads(json.dumps(PLANTILLA))
        for op in ('--caso', '--proveedor'):
            if op in a:
                i = a.index(op)
                if i + 1 >= len(a) or a[i + 1].startswith('--'):
                    raise ErrorEntrada(f'{op} requiere un valor.')
                c[op[2:]] = a[i + 1]
        os.makedirs(d, exist_ok=True)
        guardar(d, c)
        print(f'Creado {p}')
    elif cmd == 'ver':
        c = cargar(d)
        qs = list(c['Q'].values())
        paso = c.get('paso')
        paso_txt = 'cerrado' if str(paso).lower() == 'cerrado' else f'paso {paso}'
        rsp = c.get('respuesta') or {}
        print(f"{c['caso']} — {c['proveedor']} · {paso_txt} · {c.get('situacion')}")
        print(f"Dictamen: {c['dictamen']} · petitorio aceptado: {json.dumps(c.get('petitorio_aceptado'), ensure_ascii=False)}"
              f" · excepción: {c.get('excepcion') or 'ninguna'} · palanca: {c['palanca']}")
        print(f"Preguntas: {len(c['Q'])} (" + ', '.join(f"{e}: {sum(1 for x in qs if x.get('estado', '').lower().startswith(e))}" for e in ESTADOS_Q) + ')')
        print(f"Requerimientos: {len(c['S'])} · pretensión: {c['forma_pretension']} · A/C/O: {len(c['A'])}/{len(c['C'])}/{len(c['O'])}")
        print(f"Reclamo: {c['reclamo']} · respuesta: {rsp.get('fecha')} · {rsp.get('clasificacion')} · en plazo: {rsp.get('en_plazo')}")
        print(f"RV: {c['rv']} · audiencia: {(c.get('audiencia') or {}).get('fecha')} · resultado: {c['resultado']} · prescripción: {c.get('prescripcion')}")
    elif cmd == 'set':
        if len(a) < 4:
            raise ErrorEntrada('Uso: estado.py set CARPETA CLAVE VALOR')
        c = cargar(d)
        clave, v = normalizar_set(a[2], valor(a[3]))
        obj = c
        claves = clave.split('.')
        for k in claves[:-1]:
            if not isinstance(obj.get(k), dict):
                obj[k] = {}
            obj = obj[k]
        obj[claves[-1]] = v
        guardar(d, c)
        print(f'{clave} = {json.dumps(v, ensure_ascii=False)}')
    elif cmd == 'sync':
        c = sync(d)
        print(f"Sincronizado: {len(c['Q'])} Q · {len(c['S'])} S · {len(c['P'])} P · A/C/O {len(c['A'])}/{len(c['C'])}/{len(c['O'])}"
              f" · clasificación: {c['respuesta'].get('clasificacion')}")
        if c.get('q_tabla_ok') is False:
            print('Aviso: 06 existe pero no tiene filas "| Q## |".')
    elif cmd == 'compuerta':
        if len(a) < 3:
            raise ErrorEntrada('Uso: estado.py compuerta CARPETA 0-1|1-2|cierre')
        falta, avisos = compuerta(d, a[2])
        for x in avisos:
            print(x)
        if falta:
            print(f'Compuerta {a[2]}: NO se cumple. Falta:')
            for f in falta:
                print('  - ' + f)
            return 1
        print(f'Compuerta {a[2]}: se cumple.')
    else:
        print(__doc__)
        return 2
    return 0


def main():
    try:
        sys.exit(ejecutar(sys.argv[1:]))
    except ErrorEntrada as e:
        print(f'Error: {e}', file=sys.stderr)
        sys.exit(2)
    except PermissionError as e:
        print(f'Error: sin permiso para escribir o leer "{e.filename}".', file=sys.stderr)
        sys.exit(2)


if __name__ == '__main__':
    main()
