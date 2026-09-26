#!/usr/bin/env python3
"""Pruebas de los scripts del plugin reclamos-consumo-peru.

Uso (desde la raíz del repositorio):
  python3 tests/run_tests.py

Solo usa la biblioteca estándar (unittest + subprocess). Cada prueba copia el caso sintético de
tests/fixtures/ a una carpeta temporal cuyo nombre tiene espacios, tildes y corchetes, y trabaja
sobre la copia. Todos los datos son ficticios (Proveedor Ejemplo S.A.C., RUC 20000000001).
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = os.path.join(RAIZ, 'plugins', 'reclamos-consumo-peru', 'skills')
ESTADO = os.path.join(PLUGIN, 'gestionar-reclamo', 'scripts', 'estado.py')
LEGAJO = os.path.join(PLUGIN, 'gestionar-reclamo', 'scripts', 'legajo.py')
PLAZOS = os.path.join(PLUGIN, 'gestionar-reclamo', 'scripts', 'plazos.py')
VREQ = os.path.join(PLUGIN, 'paso-0-preparar-caso', 'scripts', 'validar_requerimientos.py')
VFICHA = os.path.join(PLUGIN, 'paso-2-reclama-virtual', 'scripts', 'validar_ficha.py')
PLANTILLA_FICHA = os.path.join(PLUGIN, 'paso-2-reclama-virtual', 'references', 'plantilla-ficha.md')
FIXTURES = os.path.join(RAIZ, 'tests', 'fixtures')
NOMBRE_CASO = 'r1_proveedor-ejemplo_cobro-intereses'


def correr(script, *args, cwd=None):
    env = dict(os.environ, PYTHONIOENCODING='utf-8')
    r = subprocess.run([sys.executable, script] + [str(a) for a in args], capture_output=True,
                       text=True, encoding='utf-8', errors='replace', cwd=cwd, env=env)
    return r


PDFS_FICTICIOS = [
    ('r1_proveedor-ejemplo_conciliacion-indecopi', 'Cargo Reclama Virtual.pdf'),
    ('r1_proveedor-ejemplo_conciliacion-indecopi', 'Acta de audiencia.pdf'),
    ('r1_proveedor-ejemplo_conciliacion-indecopi', 'Constancia de pago.pdf'),
    ('r1_proveedor-ejemplo_reclamo-proveedor', 'Reclamo 0001 - Proveedor Ejemplo.pdf'),
    ('r1_proveedor-ejemplo_reclamo-proveedor', 'Respuesta 0001 - Proveedor Ejemplo.pdf'),
]


class BaseCaso(unittest.TestCase):
    """Copia el caso sintético a un directorio temporal con un nombre 'difícil'."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='pruebas reclamos ')
        self.raiz_casos = os.path.join(self.tmp, 'Mis casos [2026] ñandú')
        os.makedirs(self.raiz_casos)
        self.caso = os.path.join(self.raiz_casos, NOMBRE_CASO)
        shutil.copytree(os.path.join(FIXTURES, NOMBRE_CASO), self.caso)
        self.exp = os.path.join(self.caso, 'r1_proveedor-ejemplo_expediente')
        self.p1 = os.path.join(self.caso, 'r1_proveedor-ejemplo_reclamo-proveedor')
        self.p2 = os.path.join(self.caso, 'r1_proveedor-ejemplo_conciliacion-indecopi')
        # Los PDF de prueba se generan aquí (el repositorio no versiona archivos .pdf).
        for carpeta, nombre in PDFS_FICTICIOS:
            ruta = os.path.join(self.caso, carpeta, nombre)
            if not os.path.exists(ruta):
                with open(ruta, 'wb') as f:
                    f.write(b'%PDF-1.4\n% documento ficticio de prueba\n%%EOF\n')

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    # utilidades
    def ruta(self, carpeta, prefijo):
        for n in sorted(os.listdir(carpeta)):
            if n.startswith(prefijo):
                return os.path.join(carpeta, n)
        return os.path.join(carpeta, prefijo)

    def leer(self, p):
        with open(p, encoding='utf-8') as fh:
            return fh.read()

    def escribir(self, p, texto):
        with open(p, 'w', encoding='utf-8') as fh:
            fh.write(texto)

    def reemplazar(self, p, viejo, nuevo):
        t = self.leer(p)
        self.assertIn(viejo, t, f'el fixture no contiene: {viejo!r}')
        self.escribir(p, t.replace(viejo, nuevo))

    def caso_json(self):
        with open(os.path.join(self.exp, 'caso.json'), encoding='utf-8') as fh:
            return json.load(fh)

    def estado(self, *args):
        return correr(ESTADO, *args)

    def set(self, clave, valor):
        r = self.estado('set', self.exp, clave, valor)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return r

    def assertSinTraceback(self, r):
        self.assertNotIn('Traceback', r.stderr + r.stdout)


# =================================================================== estado.py

class TestCompuerta01(BaseCaso):
    def test_pasa_con_el_caso_completo(self):
        r = self.estado('compuerta', self.exp, '0-1')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn('se cumple', r.stdout)

    def test_acepta_la_carpeta_del_caso(self):
        r = self.estado('compuerta', self.caso, '0-1')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_falla_sin_petitorio_aceptado(self):
        c = self.caso_json()
        del c['petitorio_aceptado']
        self.escribir(os.path.join(self.exp, 'caso.json'), json.dumps(c))
        r = self.estado('compuerta', self.exp, '0-1')
        self.assertEqual(r.returncode, 1)
        self.assertIn('petitorio_aceptado', r.stdout)

    def test_falla_con_petitorio_rechazado(self):
        self.set('petitorio_aceptado', 'false')
        r = self.estado('compuerta', self.exp, '0-1')
        self.assertEqual(r.returncode, 1)

    def test_alias_reencuadre_aceptado(self):
        c = self.caso_json()
        del c['petitorio_aceptado']
        c['reencuadre_aceptado'] = True
        self.escribir(os.path.join(self.exp, 'caso.json'), json.dumps(c))
        r = self.estado('compuerta', self.exp, '0-1')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIs(self.caso_json()['petitorio_aceptado'], True)

    def test_original_pasa_con_aviso(self):
        self.set('petitorio_aceptado', 'original')
        r = self.estado('compuerta', self.exp, '0-1')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn('Aviso', r.stdout)

    def test_falla_con_dictamen_desfavorable(self):
        self.reemplazar(self.ruta(self.exp, '00 '), '**Procede**', 'No procede ante INDECOPI')
        r = self.estado('compuerta', self.exp, '0-1')
        self.assertEqual(r.returncode, 1)
        self.assertIn('Dictamen', r.stdout)

    def test_falla_sin_05(self):
        os.remove(self.ruta(self.exp, '05 '))
        r = self.estado('compuerta', self.exp, '0-1')
        self.assertEqual(r.returncode, 1)
        self.assertIn('Archivo 05', r.stdout)

    def test_falla_06_sin_tabla(self):
        self.escribir(self.ruta(self.exp, '06 '), '# 06 Preguntas\n\nQ01: ¿Tienes el aviso? Sin respuesta.\n')
        r = self.estado('compuerta', self.exp, '0-1')
        self.assertEqual(r.returncode, 1)
        self.assertIn('tabla', r.stdout)
        self.assertIs(self.caso_json()['q_tabla_ok'], False)

    def test_falla_con_pregunta_pendiente(self):
        self.reemplazar(self.ruta(self.exp, '06 '), '| Consumidor | Respondida (E02) |', '| Consumidor | Pendiente |')
        r = self.estado('compuerta', self.exp, '0-1')
        self.assertEqual(r.returncode, 1)
        self.assertIn('Q02', r.stdout)

    def test_q_descartada_no_bloquea(self):
        # Q03 está Pendiente pero marcada "(descartado)": no debe aparecer
        r = self.estado('compuerta', self.exp, '0-1')
        self.assertNotIn('Q03', r.stdout)
        self.assertNotIn('Q03', self.caso_json()['Q'])

    def test_falla_dato_del_proveedor_sin_requerimiento(self):
        self.reemplazar(self.ruta(self.exp, '07 '), 'S01 | Q01, H03 |', 'S01 | H03 |')
        r = self.estado('compuerta', self.exp, '0-1')
        self.assertEqual(r.returncode, 1)
        self.assertIn('Q01', r.stdout)

    def test_falla_si_07_tiene_errores_de_validacion(self):
        self.reemplazar(self.ruta(self.exp, '07 '), 'Requiero la base contractual',
                        '¿Cuál es la base contractual')
        r = self.estado('compuerta', self.exp, '0-1')
        self.assertEqual(r.returncode, 1)
        self.assertIn('validar_requerimientos', r.stdout)

    def test_sin_requerimientos_declarado(self):
        p07 = self.ruta(self.exp, '07 ')
        t = re.sub(r'^S0\d \|.*$\n', '', self.leer(p07), flags=re.M)
        t = t.replace('## Requerimientos al proveedor\n', '## Requerimientos al proveedor\nsin_requerimientos: el consumidor ya tiene toda la información\n')
        self.escribir(p07, t)
        self.reemplazar(self.ruta(self.exp, '06 '), '| Proveedor | Sin respuesta |', '| Proveedor | Descartada |')
        r = self.estado('compuerta', self.exp, '0-1')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


class TestSync(BaseCaso):
    def test_sync_reinicia_valores(self):
        r = self.estado('sync', self.exp)
        self.assertEqual(r.returncode, 0, r.stderr)
        c = self.caso_json()
        self.assertEqual(sorted(c['S']), ['S01', 'S02'])       # S03 (descartado) ignorado
        self.assertEqual(c['prescripcion'], '05/06/2028')
        self.assertEqual(c['respuesta'], {'fecha': '20/07/2026', 'clasificacion': 'parcial', 'en_plazo': 'si'})
        self.assertEqual(c['audiencia']['fecha'], '15/09/2026')
        # Se quita S02 y se vacía 08 de A/O; se vacía 06
        self.reemplazar(self.ruta(self.exp, '07 '), 'S02 | H01 |', 'X02 | H01 |')
        self.reemplazar(self.ruta(self.exp, '07 '), 'carga de la prueba en el proveedor', '')
        p08 = self.ruta(self.p1, '08 ')
        t = re.sub(r'^[AO]0\d \|.*$\n', '', self.leer(p08), flags=re.M)
        self.escribir(p08, t)
        self.escribir(self.ruta(self.exp, '06 '), '')
        self.estado('sync', self.exp)
        c = self.caso_json()
        self.assertEqual(sorted(c['S']), ['S01'])
        self.assertEqual(c['A'], [])
        self.assertEqual(c['O'], [])
        self.assertEqual(c['Q'], {})
        self.assertIsNone(c['palanca'])
        self.assertIs(c['q_tabla_ok'], False)

    def test_json_danado(self):
        self.escribir(os.path.join(self.exp, 'caso.json'), '{"caso": "r1", ')
        r = self.estado('ver', self.exp)
        self.assertEqual(r.returncode, 2)
        self.assertIn('caso.json dañado: restáuralo o vuelve a crearlo con init', r.stderr)
        self.assertSinTraceback(r)

    def test_init_y_ver(self):
        nueva = os.path.join(self.tmp, 'r2 [nuevo] ñ', 'r2_proveedor-ejemplo_expediente')
        r = self.estado('init', nueva, '--caso', 'r2', '--proveedor', 'Proveedor Ejemplo S.A.C.')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.estado('set', nueva, 'paso', 'cerrado').returncode, 0)
        self.assertEqual(self.estado('set', nueva, 'excepcion', 'urgencia').returncode, 0)
        r = self.estado('ver', nueva)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('r2 — Proveedor Ejemplo S.A.C.', r.stdout)
        self.assertIn('cerrado', r.stdout)
        self.assertIn('petitorio aceptado: null', r.stdout)
        self.assertIn('excepción: urgencia', r.stdout)

    def test_set_valor_invalido(self):
        r = self.estado('set', self.exp, 'paso', '7')
        self.assertEqual(r.returncode, 2)
        self.assertSinTraceback(r)
        r = self.estado('set', self.exp, 'excepcion', 'otra')
        self.assertEqual(r.returncode, 2)

    def test_compuerta_desconocida(self):
        r = self.estado('compuerta', self.exp, '3-4')
        self.assertEqual(r.returncode, 2)
        self.assertSinTraceback(r)


class TestCompuerta12(BaseCaso):
    def test_pasa_con_respuesta_parcial(self):
        r = self.estado('compuerta', self.exp, '1-2')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_falla_sin_08(self):
        os.remove(self.ruta(self.p1, '08 '))
        r = self.estado('compuerta', self.exp, '1-2')
        self.assertEqual(r.returncode, 1)
        self.assertIn('08', r.stdout)

    def test_falla_sin_constancia(self):
        self.set('reclamo.codigo', 'null')
        r = self.estado('compuerta', self.exp, '1-2')
        self.assertEqual(r.returncode, 1)
        self.assertIn('reclamo.codigo', r.stdout)

    def test_favorable_corresponde_cerrar(self):
        self.reemplazar(self.ruta(self.p1, '08 '), 'clasificacion: parcial', 'clasificacion: favorable')
        r = self.estado('compuerta', self.exp, '1-2')
        self.assertEqual(r.returncode, 1)
        self.assertIn('cerrar', r.stdout)

    def test_desfavorable_fundada_corresponde_cerrar(self):
        self.reemplazar(self.ruta(self.p1, '08 '), 'clasificacion: parcial', 'clasificacion: desfavorable fundada')
        r = self.estado('compuerta', self.exp, '1-2')
        self.assertEqual(r.returncode, 1)
        self.assertIn('cerrar', r.stdout)

    def test_oferta_sin_decidir_falla(self):
        self.reemplazar(self.ruta(self.p1, '08 '), 'clasificacion: parcial', 'clasificacion: oferta')
        r = self.estado('compuerta', self.exp, '1-2')
        self.assertEqual(r.returncode, 1)
        self.assertIn('oferta_rechazada', r.stdout)

    def test_oferta_rechazada_pasa_sin_aco(self):
        p08 = self.ruta(self.p1, '08 ')
        t = re.sub(r'^[AO]0\d \|.*$\n', '', self.leer(p08), flags=re.M)
        self.escribir(p08, t.replace('clasificacion: parcial', 'clasificacion: oferta'))
        self.set('oferta_rechazada', 'true')
        r = self.estado('compuerta', self.exp, '1-2')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.caso_json()['A'], [])

    def test_sin_motivo_para_elevar(self):
        p08 = self.ruta(self.p1, '08 ')
        t = re.sub(r'^[AO]0\d \|.*$\n', '', self.leer(p08), flags=re.M)
        self.escribir(p08, t.replace('clasificacion: parcial', 'clasificacion: pendiente'))
        r = self.estado('compuerta', self.exp, '1-2')
        self.assertEqual(r.returncode, 1)
        self.assertIn('Motivo para elevar', r.stdout)

    def test_excepcion_llamadas_pasa_sin_requisitos(self):
        self.set('reclamo', '{}')
        os.remove(self.ruta(self.p1, '08 '))
        self.set('excepcion', 'llamadas')
        r = self.estado('compuerta', self.exp, '1-2')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_excepcion_urgencia_solo_constancia(self):
        os.remove(self.ruta(self.p1, '08 '))
        self.set('excepcion', 'urgencia')
        r = self.estado('compuerta', self.exp, '1-2')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.set('reclamo.fecha', 'null')
        r = self.estado('compuerta', self.exp, '1-2')
        self.assertEqual(r.returncode, 1)
        self.assertIn('reclamo.codigo y reclamo.fecha', r.stdout)


class TestCompuertaCierre(BaseCaso):
    def test_falla_sin_resultado(self):
        r = self.estado('compuerta', self.exp, 'cierre')
        self.assertEqual(r.returncode, 1)
        self.assertIn('resultado', r.stdout)

    def test_acuerdo_pasa_con_alias(self):
        self.set('resultado', 'acuerdo')
        r = self.estado('compuerta', self.exp, '2-cierre')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_sin_acuerdo_exige_rv_y_legajo(self):
        self.set('resultado', 'sin acuerdo')
        r = self.estado('compuerta', self.exp, 'cierre')
        self.assertEqual(r.returncode, 1)
        self.assertIn('rv.id', r.stdout)
        self.assertIn('10 Legajo', r.stdout)
        self.set('rv.id', '"RV-0001"')
        self.assertEqual(correr(LEGAJO, self.caso).returncode, 0)
        r = self.estado('compuerta', self.exp, 'cierre')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_sin_acuerdo_cerrado_en_paso_1_no_exige_rv(self):
        self.set('resultado', 'sin acuerdo')
        self.set('cierre_paso', '1')
        correr(LEGAJO, self.caso)
        r = self.estado('compuerta', self.exp, 'cierre')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_incumplido_exige_legajo(self):
        self.set('resultado', 'incumplido')
        r = self.estado('compuerta', self.exp, 'cierre')
        self.assertEqual(r.returncode, 1)
        self.assertIn('10 Legajo', r.stdout)
        self.assertNotIn('rv.id', r.stdout)


# =================================================================== legajo.py

class TestLegajo(BaseCaso):
    def test_legajo_desde_la_carpeta_del_caso(self):
        self.estado('sync', self.exp)
        r = correr(LEGAJO, self.caso)
        self.assertEqual(r.returncode, 0, r.stderr)
        t = self.leer(os.path.join(self.exp, '10 Legajo habilitante.md'))
        prob = t.split('## 2. Cronología probada')[1].split('## 3.')[0]
        self.assertIn('| H01 |', prob)
        self.assertIn('| H02 |', prob)
        self.assertIn('| H04 |', prob)                  # "**Acreditado**" con negrita
        self.assertNotIn('| H03 |', prob)               # Afirmado cuyo texto dice "no acreditado"
        self.assertIn('Plazos computados', t)
        self.assertIn('01/07/2026 + 15 días hábiles = 22/07/2026', t)
        for campo in ('20/07/2026', 'Respuesta en plazo | si', 'parcial', '05/06/2028'):
            self.assertIn(campo, t)
        docs = t.split('## 10. Documentos de la conciliación')[1]
        self.assertIn('Acta de audiencia.pdf', docs)
        self.assertIn('Cargo Reclama Virtual.pdf', docs)
        self.assertNotIn('09 Plan de audiencia', docs)
        self.assertNotIn('Constancia de pago', docs)
        contr = t.split('## 4. Contradicciones')[1].split('## 5.')[0]
        self.assertIn('| C01 |', contr)                 # fila de tabla en 02
        self.assertIn('| C02 |', contr)                 # línea "C02 | …" en 03
        self.assertNotIn('S03', t.split('## 6.')[1].split('## 7.')[0])

    def test_legajo_desde_el_expediente_sin_encabezado(self):
        p02 = self.ruta(self.exp, '02 ')
        t = self.leer(p02).replace('| H## | Fecha y hora | Hecho (una conducta, un actor) | Actor | Canal / lugar | Monto | Estado | Fuente |\n|---|---|---|---|---|---|---|---|\n', '')
        self.escribir(p02, t)
        r = correr(LEGAJO, self.exp)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('3 hechos probados', r.stdout)

    def test_carpeta_inexistente(self):
        r = correr(LEGAJO, os.path.join(self.tmp, 'no existe'))
        self.assertEqual(r.returncode, 2)
        self.assertSinTraceback(r)


# =================================================================== validar_requerimientos.py

class TestValidarRequerimientos(BaseCaso):
    def validar(self, texto, nombre='prueba.md'):
        p = os.path.join(self.tmp, nombre)
        self.escribir(p, texto)
        r = correr(VREQ, p, '--json')
        self.assertSinTraceback(r)
        return r, json.loads(r.stdout)

    def test_07_bueno(self):
        r = correr(VREQ, self.ruta(self.exp, '07 '), '--json')
        res = json.loads(r.stdout)
        self.assertEqual(r.returncode, 0, res)
        self.assertEqual(res['requerimientos'], 2)        # S03 (descartado) ignorado

    def test_pregunta_es_error(self):
        r, res = self.validar('S01 | Q01 | Requiero saber ¿cuál es la tasa del EECC de junio de 2026?, de forma que se verifique el cobro.\nP01 | Solicito el extorno de S/ 100.\n')
        self.assertEqual(r.returncode, 1)
        self.assertTrue(any('pregunta' in e for e in res['errores']))

    def test_mayor_no_es_mes(self):
        r, res = self.validar('S01 | Q01 | Requiero el sustento del cobro mayor, de forma que se verifique que es correcto.\nP01 | Solicito el extorno de S/ 100.\n')
        self.assertEqual(r.returncode, 1)
        self.assertTrue(any('dato concreto' in e for e in res['errores']))
        r, res = self.validar('S01 | Q01 | Requiero el sustento del cobro de mayo, de forma que se verifique que es correcto.\nP01 | Solicito el extorno de S/ 100.\n')
        self.assertEqual(r.returncode, 0, res)

    def test_datos_concretos_nuevos(self):
        for dato in ('de la empresa con RUC 20000000001', 'de mi tarjeta terminada en 1234',
                     'del código de reclamo indicado', 'con la razón social del emisor'):
            r, res = self.validar(f'S01 | Q01 | Requiero la constancia {dato}, de forma que se verifique el cobro.\nP01 | Solicito el extorno de S/ 100.\n')
            self.assertEqual(r.returncode, 0, (dato, res))

    def test_abreviaturas_no_parten_oraciones(self):
        r, res = self.validar('S01 | Q01 | Requiero la cláusula del contrato N.º 100 (art. 5, inc. b, p. 3) que suscribió Proveedor Ejemplo S.A.C. con la Sra. Ejemplo, de forma que se verifique el cobro de S/ 100.\nP01 | Solicito el extorno de S/ 100.\n')
        self.assertEqual(r.returncode, 0, res)
        self.assertFalse(any('más de una oración' in a for a in res['avisos']), res['avisos'])

    def test_dos_oraciones_avisa(self):
        r, res = self.validar('S01 | Q01 | Requiero la liquidación de S/ 100. Adjunten el contrato, de forma que se verifique el cobro.\nP01 | Solicito el extorno de S/ 100.\n')
        self.assertTrue(any('más de una oración' in a for a in res['avisos']), res['avisos'])

    def test_reclamo_multilinea(self):
        r = correr(VREQ, self.ruta(self.p1, 'Reclamo proveedor'), '--json')
        res = json.loads(r.stdout)
        self.assertEqual(r.returncode, 0, res)
        self.assertEqual(res['tipo'], 'reclamo')
        self.assertEqual(res['requerimientos'], 2)
        self.assertEqual(res['pretensiones'], 1)

    def test_reclamo_sin_requerimientos(self):
        r, res = self.validar('## PEDIDO\n1. Solicito el extorno de S/ 100 cobrados en exceso. [P01]\nPlazo y canal: correo.\n')
        self.assertEqual(r.returncode, 0, res)
        self.assertEqual(res['tipo'], 'reclamo-sin')
        self.assertTrue(res['avisos'])

    def test_ficha_buena(self):
        r = correr(VREQ, self.ruta(self.p2, 'Ficha Reclama Virtual'), '--json')
        res = json.loads(r.stdout)
        self.assertEqual(r.returncode, 0, res)
        self.assertEqual((res['tipo'], res['requerimientos'], res['pretensiones']), ('ficha', 1, 1))

    def test_ficha_con_pregunta_fuera_de_requiero(self):
        texto = ('categoria: bancario\n\n## SOLICITUD\nRequiero la liquidación de los intereses de S/ 100 del EECC de junio de 2026, '
                 'de forma que se verifique que son conformes. ¿Por qué no respondieron a tiempo? '
                 'De no acreditarse lo requerido, solicito el extorno de S/ 100.\n\n## Etapa 2\n')
        r, res = self.validar(texto)
        self.assertEqual(r.returncode, 1)
        self.assertTrue(any(e.startswith('SOLICITUD') for e in res['errores']), res)

    def test_ficha_requiero_tras_punto_y_coma_y_por_favor(self):
        texto = ('categoria: bancario\n\n## SOLICITUD\nPor favor, requiero la liquidación de los intereses de S/ 100 del EECC de junio de 2026, '
                 'de forma que se verifique que son conformes; requiero la constancia del aviso del cambio de tasa de mayo de 2026, '
                 'de forma que se verifique que se envió. Gracias por su atención. De no acreditarse lo requerido, solicito el extorno de S/ 100.\n')
        r, res = self.validar(texto)
        self.assertEqual(r.returncode, 0, res)
        self.assertEqual(res['requerimientos'], 2)
        self.assertTrue(any('Gracias' in a for a in res['avisos']))

    def test_ficha_sin_pretension_avisa(self):
        texto = ('categoria: otros\n\n## SOLICITUD\nRequiero la liquidación de los intereses de S/ 100 del EECC de junio de 2026, '
                 'de forma que se verifique que son conformes.\n')
        r, res = self.validar(texto)
        self.assertEqual(r.returncode, 0, res)
        self.assertTrue(any('pretensión' in a for a in res['avisos']))

    def test_ficha_llamadas_no_se_valida(self):
        texto = 'categoria: llamadas\n\n## SOLICITUD\n¿Texto cualquiera?\n'
        r, res = self.validar(texto)
        self.assertEqual(r.returncode, 0, res)
        self.assertEqual(res['tipo'], 'ficha-llamadas')

    def test_mas_de_cuatro(self):
        filas = ''.join(f'S0{i} | Q01 | Requiero la constancia {i} del EECC de junio de 2026, de forma que se verifique el cobro.\n' for i in range(1, 6))
        r, res = self.validar(filas + 'P01 | Solicito el extorno de S/ 100.\n')
        self.assertEqual(r.returncode, 1)
        self.assertTrue(any('máximo es 4' in e for e in res['errores']))

    def test_archivo_inexistente(self):
        r = correr(VREQ, os.path.join(self.tmp, 'no existe.md'))
        self.assertEqual(r.returncode, 2)
        self.assertSinTraceback(r)


# =================================================================== validar_ficha.py

class TestValidarFicha(BaseCaso):
    def ficha(self):
        return self.ruta(self.p2, 'Ficha Reclama Virtual')

    def validar(self, p):
        r = correr(VFICHA, p, '--json')
        self.assertSinTraceback(r)
        return r, json.loads(r.stdout)

    def test_ficha_buena(self):
        r, res = self.validar(self.ficha())
        self.assertEqual(r.returncode, 0, res)
        # adjuntos relativos resueltos contra la carpeta de la ficha: no hay aviso de "no puedo leer"
        self.assertFalse(any('no puedo leer' in a for a in res['avisos']), res['avisos'])
        # discapacidad vacía no es error
        self.assertFalse(any('discapacidad' in e for e in res['errores']))

    def test_plantilla_sin_tocar_da_error(self):
        p = os.path.join(self.p2, 'Ficha Reclama Virtual - plantilla.md')
        shutil.copy(PLANTILLA_FICHA, p)
        r, res = self.validar(p)
        self.assertEqual(r.returncode, 1)
        self.assertTrue(any('plantilla' in e for e in res['errores']), res['errores'])

    def test_marcadores_de_plantilla(self):
        p = self.ficha()
        self.reemplazar(p, 'caso: r1', 'caso: r#')
        self.reemplazar(p, 'reclamado_documento: 20000000001', 'reclamado_documento: 20XXXXXXXXX')
        self.reemplazar(p, 'cobrados en exceso y de los cargos derivados.', 'cobrados en exceso y de los cargos derivados.\n<!-- nota -->')
        self.reemplazar(p, '- Otros | ../', '- Otros | C:\\ruta\\')
        r, res = self.validar(p)
        self.assertEqual(r.returncode, 1)
        texto = '\n'.join(res['errores'])
        for clave in ('caso:', 'reclamado_documento', 'SOLICITUD: contiene un comentario', 'adjuntos #2'):
            self.assertIn(clave, texto)

    def test_ids_internos_avisan(self):
        p = self.ficha()
        self.reemplazar(p, 'presenté el reclamo N.º 0001', 'presenté el reclamo N.º 0001 [E04 p.1] (ver H04 y A01)')
        r, res = self.validar(p)
        self.assertEqual(r.returncode, 0, res)
        self.assertTrue(any('IDs internos' in a and 'H04' in a for a in res['avisos']), res['avisos'])

    def test_adjunto_grande(self):
        grande = os.path.join(self.p2, 'Estado de cuenta grande.pdf')
        with open(grande, 'wb') as fh:
            fh.write(b'0' * 6000000)
        self.reemplazar(self.ficha(), '- Otros | ../r1_proveedor-ejemplo_reclamo-proveedor/Respuesta 0001 - Proveedor Ejemplo.pdf',
                        '- Otros | Estado de cuenta grande.pdf')
        r, res = self.validar(self.ficha())
        self.assertEqual(r.returncode, 1)
        self.assertTrue(any('6 000 000 bytes' in e and 'MiB' in e for e in res['errores']), res['errores'])

    def test_clave_dentro_de_solicitud(self):
        p = self.ficha()
        self.reemplazar(p, '\n## Etapa 2 — Identifica al reclamado\n', '\n')
        r, res = self.validar(p)
        self.assertTrue(any('encabezado ##' in a for a in res['avisos']), res['avisos'])
        self.assertFalse(any('reclamado_documento' in e for e in res['errores']), res['errores'])

    def test_salida_texto_sin_traceback(self):
        r = correr(VFICHA, self.ficha())
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertSinTraceback(r)
        r = correr(VFICHA, os.path.join(self.tmp, 'no existe.md'))
        self.assertEqual(r.returncode, 2)
        self.assertSinTraceback(r)


# =================================================================== plazos.py

class TestPlazos(unittest.TestCase):
    def test_habiles_octubre(self):
        r = correr(PLAZOS, 'habiles', '01/10/2026', '15')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('23/10/2026', r.stdout)

    def test_habiles_fin_de_anio(self):
        r = correr(PLAZOS, 'habiles', '18/12/2026', '15')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('12/01/2027', r.stdout)

    def test_7_de_junio_2022_no_es_feriado(self):
        r = correr(PLAZOS, 'transcurridos', '06/06/2022', '07/06/2022')
        self.assertIn(': 1', r.stdout)
        r = correr(PLAZOS, 'transcurridos', '06/06/2023', '07/06/2023')
        self.assertIn(': 0', r.stdout)

    def test_no_laborables(self):
        r = correr(PLAZOS, 'transcurridos', '24/07/2026', '30/07/2026')
        self.assertIn(': 2', r.stdout)                     # 27/07 y 30/07
        r = correr(PLAZOS, 'transcurridos', '24/07/2026', '30/07/2026', '--no-laborables')
        self.assertIn(': 1', r.stdout)                     # solo 30/07

    def test_argumentos_invalidos(self):
        casos = [
            ('habiles', '32/13/2026', '15'),
            ('habiles', '01/10/2026', 'quince'),
            ('habiles', '01/10/2026', '0'),
            ('habiles', '01/10/2026'),
            ('transcurridos', '01/10/2026', '2026-10-05'),
            ('prescripcion', 'ayer'),
            ('habiles', '01/10/2026', '15', '--extra'),
            ('desconocido', '01/10/2026'),
        ]
        for args in casos:
            r = correr(PLAZOS, *args)
            self.assertNotEqual(r.returncode, 0, args)
            self.assertNotIn('Traceback', r.stderr, args)
            self.assertIn('Error', r.stderr, args)

    def test_prescripcion(self):
        r = correr(PLAZOS, 'prescripcion', '05/06/2026')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('05/06/2028', r.stdout)


# =================================================================== compilación

class TestCompilacion(unittest.TestCase):
    def test_compilan(self):
        # compile() en memoria: no deja __pycache__ dentro del plugin
        for s in (ESTADO, LEGAJO, PLAZOS, VREQ, VFICHA):
            with open(s, encoding='utf-8') as fh:
                compile(fh.read(), s, 'exec')


if __name__ == '__main__':
    unittest.main(verbosity=2)
