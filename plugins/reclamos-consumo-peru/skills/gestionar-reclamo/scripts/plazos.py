#!/usr/bin/env python3
"""Cómputo de plazos para expedientes de consumo (Perú).

Uso:
  python3 plazos.py habiles DD/MM/AAAA N [--extra DD/MM/AAAA,...] [--no-laborables]
      -> fecha en que vence un plazo de N días hábiles contados desde el día siguiente.
  python3 plazos.py transcurridos DD/MM/AAAA DD/MM/AAAA [--extra ...] [--no-laborables]
      -> días hábiles transcurridos entre dos fechas (excluye la inicial, incluye la final).
  python3 plazos.py prescripcion DD/MM/AAAA [ANIOS]
      -> fecha límite de prescripción (art. 121 del Código: 2 años por defecto) y días calendario restantes.

Días hábiles: excluye sábados, domingos y feriados nacionales del Perú (Jueves y Viernes Santo incluidos).
--no-laborables suma los días no laborables del sector público que figuran en NO_LABORABLES (útil para
plazos ante INDECOPI). --extra agrega otras fechas a excluir, separadas por comas.
Verificar cada año los feriados nuevos y los días no laborables decretados, y actualizar este archivo.
No usa dependencias externas.
"""
import sys
from datetime import date, datetime, timedelta

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    try:
        sys.stdout.reconfigure(errors='replace')
        sys.stderr.reconfigure(errors='replace')
    except Exception:
        pass

# Días no laborables del sector público (decretos supremos). Formato: año -> ["DD/MM", ...].
# IMPORTANTE: verificar cada año en el diario oficial y agregar el año nuevo aquí.
NO_LABORABLES = {
    2026: ["02/01", "27/07"],
}


class ErrorEntrada(Exception):
    """Argumento inválido: se informa sin traceback."""


def pascua(y):
    a = y % 19; b = y // 100; c = y % 100; d = b // 4; e = b % 4
    f = (b + 8) // 25; g = (b - f + 1) // 3; h = (19 * a + b - d - g + 15) % 30
    i = c // 4; k = c % 4; l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mes = (h + l - 7 * m + 114) // 31; dia = ((h + l - 7 * m + 114) % 31) + 1
    return date(y, mes, dia)


_CACHE = {}


def feriados(y):
    if y in _CACHE:
        return _CACHE[y]
    fijos = [(1, 1), (5, 1), (6, 29), (7, 28), (7, 29), (8, 30), (10, 8), (11, 1), (12, 8), (12, 25)]
    if y >= 2022:
        fijos += [(8, 6), (12, 9)]    # Batalla de Junín y Batalla de Ayacucho (incorporados en 2022)
    if y >= 2023:
        fijos += [(6, 7), (7, 23)]    # Batalla de Arica y Día de la Fuerza Aérea (incorporados en 2023)
    s = {date(y, m, d) for m, d in fijos}
    p = pascua(y)
    s |= {p - timedelta(days=3), p - timedelta(days=2)}   # Jueves y Viernes Santo
    _CACHE[y] = s
    return s


def no_laborables(y):
    out = set()
    for dm in NO_LABORABLES.get(y, []):
        d, m = dm.split('/')
        out.add(date(y, int(m), int(d)))
    return out


def parse(s, nombre='fecha'):
    try:
        return datetime.strptime(s.strip(), "%d/%m/%Y").date()
    except (ValueError, AttributeError):
        raise ErrorEntrada(f"{nombre} '{s}' no es válida: use el formato DD/MM/AAAA (p. ej., 01/10/2026).")


def entero_positivo(s, nombre):
    try:
        n = int(s)
    except (ValueError, TypeError):
        raise ErrorEntrada(f"{nombre} '{s}' debe ser un número entero mayor o igual que 1.")
    if n < 1:
        raise ErrorEntrada(f"{nombre} debe ser mayor o igual que 1 (recibido: {n}).")
    return n


def separar(args):
    """Separa opciones (--extra X, --no-laborables) de los argumentos posicionales."""
    pos, ex, nolab = [], set(), False
    i = 0
    while i < len(args):
        x = args[i]
        if x == "--extra":
            if i + 1 >= len(args):
                raise ErrorEntrada("--extra requiere una lista de fechas DD/MM/AAAA separadas por comas.")
            ex |= {parse(v, 'fecha de --extra') for v in args[i + 1].split(",") if v.strip()}
            i += 2
            continue
        if x == "--no-laborables":
            nolab = True
        elif x.startswith("--"):
            raise ErrorEntrada(f"opción no reconocida: {x}")
        else:
            pos.append(x)
        i += 1
    return pos, ex, nolab


def es_habil(d, ex, nolab=False):
    if d.weekday() >= 5 or d in feriados(d.year) or d in ex:
        return False
    return not (nolab and d in no_laborables(d.year))


def fmt(d):
    dias = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
    return f"{d.strftime('%d/%m/%Y')} ({dias[d.weekday()]})"


def nota_nolab(nolab, desde, hasta):
    if not nolab:
        return ""
    faltan = [y for y in range(desde.year, hasta.year + 1) if y not in NO_LABORABLES]
    if faltan:
        return f"\nAviso: no hay días no laborables registrados para {', '.join(map(str, faltan))}; verificar y actualizar NO_LABORABLES."
    return ""


def ejecutar(a):
    if not a:
        print(__doc__)
        return 2
    cmd = a[0]
    pos, ex, nolab = separar(a[1:])
    if cmd == "habiles":
        if len(pos) != 2:
            raise ErrorEntrada("uso: plazos.py habiles DD/MM/AAAA N")
        d0 = parse(pos[0], 'fecha inicial')
        n = entero_positivo(pos[1], 'N (días hábiles)')
        d, c = d0, 0
        while c < n:
            d += timedelta(days=1)
            if es_habil(d, ex, nolab):
                c += 1
        extra = " (con días no laborables del sector público)" if nolab else ""
        print(f"Vence: {fmt(d)} — {n} días hábiles desde el día siguiente a {pos[0]}{extra}{nota_nolab(nolab, d0, d)}")
    elif cmd == "transcurridos":
        if len(pos) != 2:
            raise ErrorEntrada("uso: plazos.py transcurridos DD/MM/AAAA DD/MM/AAAA")
        d1, d2 = parse(pos[0], 'fecha inicial'), parse(pos[1], 'fecha final')
        if d2 < d1:
            raise ErrorEntrada("la fecha final es anterior a la inicial.")
        d, c = d1, 0
        while d < d2:
            d += timedelta(days=1)
            if es_habil(d, ex, nolab):
                c += 1
        print(f"Días hábiles transcurridos entre {pos[0]} y {pos[1]}: {c}{nota_nolab(nolab, d1, d2)}")
    elif cmd == "prescripcion":
        if len(pos) not in (1, 2):
            raise ErrorEntrada("uso: plazos.py prescripcion DD/MM/AAAA [ANIOS]")
        d = parse(pos[0], 'fecha')
        n = entero_positivo(pos[1], 'ANIOS') if len(pos) > 1 else 2
        try:
            lim = d.replace(year=d.year + n)
        except ValueError:
            lim = d.replace(year=d.year + n, day=28)
        rest = (lim - date.today()).days
        alerta = " ALERTA: menos de 90 días" if 0 <= rest < 90 else (" PRESCRITO" if rest < 0 else "")
        print(f"Prescripción: {fmt(lim)} — faltan {rest} días calendario.{alerta}")
    else:
        raise ErrorEntrada(f"comando no reconocido: '{cmd}'. Use habiles, transcurridos o prescripcion.")
    return 0


def main():
    try:
        sys.exit(ejecutar(sys.argv[1:]))
    except ErrorEntrada as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
