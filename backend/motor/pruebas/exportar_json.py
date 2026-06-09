"""
Exportador de resultados de tests a JSON sin modificar los tests originales.
Ejecuta los tests, captura la salida de terminal y la guarda como JSON.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import json
import re
from datetime import datetime
from io import StringIO
from contextlib import redirect_stdout

from motor.pruebas.test_engine import (
    test_implication_chain,
    test_disjunctive_syllogism,
    test_contradictory_evidence,
    test_de_morgan,
    test_constructive_dilemma,
    test_medical_reasoning
)


def ejecutar_y_capturar(func):
    """Ejecuta un test y captura toda su salida"""
    buffer = StringIO()
    with redirect_stdout(buffer):
        try:
            func()
            exito = True
            error = None
        except Exception as e:
            exito = False
            error = str(e)
    return buffer.getvalue(), exito, error


def extraer_variables(texto):
    """Extrae las variables de la sección RESULTADO FINAL"""
    variables = []
    patron = r'([A-Za-z0-9_→∧∨¬]+)\s+([TNFB])\s+([TNFB])\s+([✓]?)'

    seccion = re.search(r'RESULTADO FINAL.*?\n(.*?)(?:\n\n|\Z)', texto, re.DOTALL)
    if seccion:
        for linea in seccion.group(1).split('\n'):
            match = re.search(patron, linea)
            if match:
                variables.append({
                    "nombre": match.group(1).strip(),
                    "inicial": match.group(2),
                    "final": match.group(3),
                    "es_premisa": match.group(4) == "✓"
                })
    return variables


def extraer_conectivos(texto):
    """Extrae los conectivos de la sección CONECTIVOS"""
    conectivos = []
    patron = r'(\w+)\s+(\w+)\s+\[(.*?)\]\s+(\w+)'

    seccion = re.search(r'CONECTIVOS\n=+\n.*?\n-+\n(.*?)(?:\n\n|\Z)', texto, re.DOTALL)
    if seccion:
        for linea in seccion.group(1).split('\n'):
            match = re.search(patron, linea)
            if match:
                conectivos.append({
                    "id": match.group(1),
                    "tipo": match.group(2),
                    "entradas": [x.strip().strip("'") for x in match.group(3).split(',')],
                    "salida": match.group(4)
                })
    return conectivos


def extraer_traza(texto):
    """Extrae la traza de propagación"""
    traza = []

    seccion = re.search(r'TRAZA DE PROPAGACIÓN.*?\n=+\n(.*?)(?:\n\nRESULTADO FINAL|\Z)', texto, re.DOTALL)
    if seccion:
        pasos = re.findall(
            r'── Paso (\d+).*?Iteración (\d+).*?\n     (.*?)\n     Variable.*?\n     -+\n(.*?)(?=\n  ── Paso|\n\n=|$)',
            seccion.group(1),
            re.DOTALL
        )

        for num, iteracion, detalles, bloque in pasos:
            paso = {
                "paso": int(num),
                "iteracion": int(iteracion),
                "detalles": detalles.strip(),
                "cambios": []
            }

            for linea in bloque.split('\n'):
                cambio = re.search(r'(\w+)\s+(\{.*?\})\s+(\{.*?\})(?: ◄)?', linea)
                if cambio and cambio.group(2) != cambio.group(3):
                    paso["cambios"].append({
                        "variable": cambio.group(1),
                        "antes": cambio.group(2),
                        "despues": cambio.group(3)
                    })

            if paso["cambios"]:
                traza.append(paso)

    return traza


def extraer_resultado(texto):
    """Extrae el resultado final (stable, iteraciones)"""
    resultado = {"stable": False, "iteraciones": 0}

    stable = re.search(r'estable=(\w+)', texto)
    if stable:
        resultado["stable"] = stable.group(1) == "True"

    iteraciones = re.search(r'iteraciones=(\d+)', texto)
    if iteraciones:
        resultado["iteraciones"] = int(iteraciones.group(1))

    return resultado


def extraer_descripcion(texto):
    """Extrae la descripción del test desde el header"""
    match = re.search(r'TEST \d+: (.+?)\n  (.+?)\n', texto)
    if match:
        return f"{match.group(1)} - {match.group(2)}"
    return ""


tests = [
    ("cadena_implicaciones", test_implication_chain),
    ("silogismo_disyuntivo", test_disjunctive_syllogism),
    ("evidencia_contradictoria", test_contradictory_evidence),
    ("de_morgan", test_de_morgan),
    ("dilema_constructivo", test_constructive_dilemma),
    ("razonamiento_medico", test_medical_reasoning),
]

resultados = []
pasaron = 0
fallaron = 0

print("=" * 80)
print("  EJECUTANDO TESTS Y CAPTURANDO RESULTADOS")
print("=" * 80)
print()

for nombre, test_func in tests:
    salida, exito, error = ejecutar_y_capturar(test_func)

    print(salida)

    if exito:
        resultado = {
            "test_id": nombre,
            "descripcion": extraer_descripcion(salida),
            "resultado": extraer_resultado(salida),
            "variables": extraer_variables(salida),
            "conectivos": extraer_conectivos(salida),
            "traza": extraer_traza(salida)
        }
        resultados.append(resultado)
        pasaron += 1
    else:
        print(f"[ERROR] {nombre}: {error}")
        resultados.append({
            "test_id": nombre,
            "error": error,
            "resultado": {"stable": False}
        })
        fallaron += 1

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
archivo_json = f"resultados_tests_{timestamp}.json"

with open(archivo_json, 'w', encoding='utf-8') as f:
    json.dump({
        "timestamp": datetime.now().isoformat(),
        "resumen": {
            "total": len(tests),
            "pasaron": pasaron,
            "fallaron": fallaron
        },
        "tests": resultados
    }, f, indent=2, ensure_ascii=False)

print(f"\n  Resultados guardados en: {archivo_json}")
print(f"\n{'=' * 80}")
print(f"  {pasaron} pasaron  |  {fallaron} fallaron")
print(f"{'=' * 80}")
