# -*- coding: utf-8 -*-
"""
SVAJ Functions Calculator - Servidor web (Flask) para Render

Este servidor NO modifica los scripts de la carpeta "algoritmos".
Cada vez que el usuario pide un calculo:
  1. Lee el script original.
  2. Cambia SOLO el valor de h en memoria (la linea "h = 25.4").
  3. Lo ejecuta en una carpeta temporal (proceso aparte).
  4. Recoge lo que imprime (Max/Min) y los archivos que genera (.png y .xlsx).
  5. Se los regresa a la pagina web.

@author: JMG
"""

import base64
import glob
import os
import re
import subprocess
import sys
import tempfile

from flask import Flask, jsonify, request, send_from_directory

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ALGO_DIR = os.path.join(BASE_DIR, "algoritmos")
WEB_DIR = os.path.join(BASE_DIR, "web")

# Clave que usa la pagina  ->  nombre del script original
ALGORITMOS = {
    "cycloidal":   "2 - Cycloidal displacement - Final.py",
    "trapezoidal": "3 - Modified Trapezoidal Acceleration - Final.py",
    "sine":        "4 - Modified Sine Acceleration - Final.py",
    "poly345":     "5 - 3-4-5 Polynomial - Final.py",
    "poly4567":    "6 - 4-5-6-7 Polynomial - Final.py",
    "singledwell": "7 - Single dwell Polynomial - Final.py",
}

# Limites para el valor de h (mm)
H_MIN = 0.001
H_MAX = 1000.0

# Pequeno programa que corre en un proceso aparte: lee el script,
# reemplaza la linea de h y lo ejecuta tal cual.
RUNNER = r'''
import re, sys
ruta, h = sys.argv[1], sys.argv[2]
src = open(ruta, encoding="utf-8").read()
src, n = re.subn(r"(?m)^h\s*=\s*[0-9.]+\s*$", "h = " + h, src, count=1)
if n != 1:
    sys.exit("No se encontro la linea de h en el script")
exec(compile(src, ruta, "exec"), {"__name__": "__main__"})
'''

# Nombre que heredan la imagen y el Excel cuando el usuario no escribe uno
NOMBRES_DEFAULT = {
    "cycloidal":   "SVAJ Cycloidal",
    "trapezoidal": "SVAJ Modified trapezoidal",
    "sine":        "SVAJ Modified sine",
    "poly345":     "SVAJ 3-4-5 Polynomial",
    "poly4567":    "SVAJ 4-5-6-7 Polynomial",
    "singledwell": "SVAJ Single dwell Polynomial",
}

NOMBRE_MAX = 60


def limpiar_nombre(texto, defecto):
    """Deja solo caracteres seguros para un nombre de archivo.
    Si no queda nada, regresa el nombre por defecto."""
    texto = str(texto or "")[:200]
    texto = re.sub(r"[^\w\s\-().]", "", texto)      # quita / \ : * ? " < > | etc.
    texto = re.sub(r"\s+", " ", texto).strip(" .")   # espacios y puntos en los extremos
    texto = texto[:NOMBRE_MAX].strip(" .")
    return texto or defecto


ETIQUETAS = ["Max_Velocity", "Min_Velocity", "Max_Acceleration",
             "Min_Acceleration", "Max_Jerk", "Min_Jerk"]

app = Flask(__name__, static_folder=WEB_DIR, static_url_path="")


@app.route("/")
def inicio():
    return send_from_directory(WEB_DIR, "index.html")


@app.route("/api/calcular", methods=["POST"])
def calcular():
    datos = request.get_json(silent=True) or {}
    clave = datos.get("algoritmo")

    if clave not in ALGORITMOS:
        return jsonify(error="Algoritmo no valido."), 400

    try:
        h = float(datos.get("h"))
    except (TypeError, ValueError):
        return jsonify(error="h debe ser un numero."), 400

    if not (H_MIN <= h <= H_MAX):
        return jsonify(error=f"h debe estar entre {H_MIN} y {H_MAX} mm."), 400

    nombre_analisis = limpiar_nombre(datos.get("nombre"), NOMBRES_DEFAULT[clave])

    script = os.path.join(ALGO_DIR, ALGORITMOS[clave])

    with tempfile.TemporaryDirectory() as tmp:
        env = dict(os.environ, MPLBACKEND="Agg")
        try:
            proc = subprocess.run(
                [sys.executable, "-c", RUNNER, script, repr(h)],
                cwd=tmp, env=env, capture_output=True, text=True, timeout=120,
            )
        except subprocess.TimeoutExpired:
            return jsonify(error="El calculo tardo demasiado."), 504

        if proc.returncode != 0:
            app.logger.error(proc.stderr)
            return jsonify(error="Ocurrio un error al ejecutar el algoritmo."), 500

        # Valores Max/Min impresos por el script
        valores = {}
        for linea in proc.stdout.splitlines():
            if ":" in linea:
                nombre, valor = linea.split(":", 1)
                nombre = nombre.strip()
                if nombre in ETIQUETAS:
                    valores[nombre] = float(valor)

        # Archivos generados por el script
        pngs = glob.glob(os.path.join(tmp, "*.png"))
        xlsxs = glob.glob(os.path.join(tmp, "*.xlsx"))
        if not pngs or not xlsxs:
            return jsonify(error="El script no genero la imagen o el Excel."), 500

        # La imagen y el Excel heredan el nombre del analisis
        png_final = os.path.join(tmp, nombre_analisis + ".png")
        xlsx_final = os.path.join(tmp, nombre_analisis + ".xlsx")
        os.replace(pngs[0], png_final)
        os.replace(xlsxs[0], xlsx_final)

        def a_base64(ruta):
            with open(ruta, "rb") as f:
                return base64.b64encode(f.read()).decode("ascii")

        return jsonify(
            h=h,
            valores=valores,
            imagen=a_base64(png_final),
            imagen_nombre=os.path.basename(png_final),
            excel=a_base64(xlsx_final),
            excel_nombre=os.path.basename(xlsx_final),
        )


if __name__ == "__main__":
    # Para probar en tu computadora: python app.py  ->  http://127.0.0.1:5000
    app.run(debug=True)
