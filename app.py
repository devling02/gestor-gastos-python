from flask import Flask, render_template, request, redirect
import json
import os
from datetime import date

app = Flask(__name__)

ARCHIVO_DATOS = "datos.json"


def cargar_datos():
    if os.path.exists(ARCHIVO_DATOS):
        with open(ARCHIVO_DATOS, "r", encoding="utf-8") as archivo:
            return json.load(archivo)
    return []


def guardar_datos(movimientos):
    with open(ARCHIVO_DATOS, "w", encoding="utf-8") as archivo:
        json.dump(movimientos, archivo, indent=4, ensure_ascii=False)


@app.route("/", methods=["GET", "POST"])
def index():
    movimientos = cargar_datos()

    if request.method == "POST":
        tipo = request.form["tipo"]
        descripcion = request.form["descripcion"]
        cantidad = float(request.form["cantidad"])
        categoria = request.form["categoria"]

        movimiento = {
            "tipo": tipo,
            "descripcion": descripcion,
            "cantidad": cantidad,
            "categoria": categoria,
            "fecha": str(date.today())
        }

        movimientos.append(movimiento)
        guardar_datos(movimientos)

        return redirect("/")

    ingresos = 0
    gastos = 0

    for movimiento in movimientos:
        if movimiento["tipo"] == "ingreso":
            ingresos += movimiento["cantidad"]
        elif movimiento["tipo"] == "gasto":
            gastos += movimiento["cantidad"]

    balance = ingresos - gastos

    return render_template(
        "index.html",
        movimientos=movimientos,
        ingresos=ingresos,
        gastos=gastos,
        balance=balance
    )

@app.route("/eliminar/<int:indice>", methods=["POST"])
def eliminar_movimiento(indice):
    movimientos = cargar_datos()

    if 0 <= indice < len(movimientos):
        movimientos.pop(indice)
        guardar_datos(movimientos)

    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)