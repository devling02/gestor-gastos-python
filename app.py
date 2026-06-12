import os
from datetime import date

import psycopg
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "clave-secreta-desarrollo")

DATABASE_URL = os.getenv("DATABASE_URL")

print("DATABASE_URL cargada:", DATABASE_URL is not None, flush=True)


def obtener_conexion():
    return psycopg.connect(DATABASE_URL, autocommit=True)


def usuario_actual():
    usuario_id = session.get("usuario_id")
    if usuario_id is None:
        return None
    try:
        return int(usuario_id)
    except (ValueError, TypeError):
        session.clear()
        return None

def buscar_usuario_por_email(email):
    with obtener_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, email, password_hash
                FROM usuarios
                WHERE email = %s
                """,
                (email,)
            )
            return cursor.fetchone()


def crear_usuario(email, password):
    password_hash = generate_password_hash(password)

    with obtener_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO usuarios (email, password_hash)
                VALUES (%s, %s)
                RETURNING id
                """,
                (email, password_hash)
            )
            usuario_id = cursor.fetchone()[0]

    return usuario_id


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


@app.route("/register", methods=["GET", "POST"])
def register():
    error = None

    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        if not email or not password:
            error = "Debes completar todos los campos."
        elif len(password) < 6:
            error = "La contraseña debe tener al menos 6 caracteres."
        elif buscar_usuario_por_email(email):
            error = "Ya existe una cuenta con ese email."
        else:
            usuario_id = crear_usuario(email, password)
            session["usuario_id"] = usuario_id
            session["email"] = email
            return redirect(url_for("index"))

    return render_template("register.html", error=error)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        usuario = buscar_usuario_por_email(email)

        if usuario is None:
            error = "Email o contraseña incorrectos."
        else:
            usuario_id = usuario[0]
            usuario_email = usuario[1]
            password_hash = usuario[2]

            if check_password_hash(password_hash, password):
                session["usuario_id"] = usuario_id
                session["email"] = usuario_email
                return redirect(url_for("index"))
            else:
                error = "Email o contraseña incorrectos."

    return render_template("login.html", error=error)


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/", methods=["GET", "POST"])
def index():
    usuario_id = usuario_actual()

    if usuario_id is None:
        return redirect(url_for("login"))

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

        return redirect(url_for("index"))

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
        balance=balance,
        email=session.get("email")
    )


@app.route("/eliminar/<int:movimiento_id>", methods=["POST"])
def eliminar_movimiento(movimiento_id):
    usuario_id = usuario_actual()

    if usuario_id is None:
        return redirect(url_for("login"))

    eliminar_movimiento_bd(usuario_id, movimiento_id)

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5050)