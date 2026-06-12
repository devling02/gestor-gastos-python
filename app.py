import os
import uuid
from datetime import date

import psycopg
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, session

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "clave-secreta-desarrollo")

DATABASE_URL = os.getenv("DATABASE_URL")

print("DATABASE_URL cargada:", DATABASE_URL is not None, flush=True)


def obtener_conexion():
    return psycopg.connect(DATABASE_URL, autocommit=True)


def obtener_usuario_id():
    if "usuario_id" not in session:
        session["usuario_id"] = str(uuid.uuid4())

    return session["usuario_id"]


def cargar_movimientos(usuario_id):
    with obtener_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, tipo, descripcion, cantidad, categoria, fecha
                FROM movimientos
                WHERE usuario_id = %s
                ORDER BY id DESC
                """,
                (usuario_id,)
            )

            filas = cursor.fetchall()

    movimientos = []

    for fila in filas:
        movimiento = {
            "id": fila[0],
            "tipo": fila[1],
            "descripcion": fila[2],
            "cantidad": float(fila[3]),
            "categoria": fila[4],
            "fecha": fila[5]
        }

        movimientos.append(movimiento)

    return movimientos


def guardar_movimiento(usuario_id, tipo, descripcion, cantidad, categoria):
    with obtener_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO movimientos
                (usuario_id, tipo, descripcion, cantidad, categoria, fecha)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    usuario_id,
                    tipo,
                    descripcion,
                    cantidad,
                    categoria,
                    date.today()
                )
            )


def eliminar_movimiento_bd(usuario_id, movimiento_id):
    with obtener_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM movimientos
                WHERE id = %s AND usuario_id = %s
                """,
                (movimiento_id, usuario_id)
            )


@app.route("/test-db")
def test_db():
    with obtener_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM movimientos")
            total = cursor.fetchone()[0]

    return f"Conexión correcta. Movimientos en la base de datos: {total}"


@app.route("/", methods=["GET", "POST"])
def index():
    usuario_id = obtener_usuario_id()

    if request.method == "POST":
        tipo = request.form["tipo"]
        descripcion = request.form["descripcion"]
        cantidad = float(request.form["cantidad"])
        categoria = request.form["categoria"]

        guardar_movimiento(
            usuario_id,
            tipo,
            descripcion,
            cantidad,
            categoria
        )

        return redirect("/")

    movimientos = cargar_movimientos(usuario_id)

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


@app.route("/eliminar/<int:movimiento_id>", methods=["POST"])
def eliminar_movimiento(movimiento_id):
    usuario_id = obtener_usuario_id()
    eliminar_movimiento_bd(usuario_id, movimiento_id)

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5050)