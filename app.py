import os
import calendar
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


def convertir_filas_a_movimientos(filas):
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


def cargar_movimientos(usuario_id, filtro_tipo=None, busqueda=None, filtro_categoria=None):
    condiciones = ["usuario_id = %s"]
    parametros = [usuario_id]

    if filtro_tipo in ["ingreso", "gasto"]:
        condiciones.append("tipo = %s")
        parametros.append(filtro_tipo)

    if busqueda:
        condiciones.append("descripcion ILIKE %s")
        parametros.append(f"%{busqueda}%")

    if filtro_categoria:
        condiciones.append("categoria = %s")
        parametros.append(filtro_categoria)

    where_sql = " AND ".join(condiciones)

    with obtener_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT id, tipo, descripcion, cantidad, categoria, fecha
                FROM movimientos
                WHERE {where_sql}
                ORDER BY fecha DESC, id DESC
                """,
                parametros
            )
            filas = cursor.fetchall()

    return convertir_filas_a_movimientos(filas)


def cargar_todos_los_movimientos(usuario_id):
    with obtener_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, tipo, descripcion, cantidad, categoria, fecha
                FROM movimientos
                WHERE usuario_id = %s
                ORDER BY fecha ASC, id ASC
                """,
                (usuario_id,)
            )
            filas = cursor.fetchall()

    return convertir_filas_a_movimientos(filas)


def guardar_movimiento(usuario_id, tipo, descripcion, cantidad, categoria, fecha):
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
                    fecha
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


def calcular_totales(movimientos):
    ingresos = 0
    gastos = 0

    for movimiento in movimientos:
        if movimiento["tipo"] == "ingreso":
            ingresos += movimiento["cantidad"]
        elif movimiento["tipo"] == "gasto":
            gastos += movimiento["cantidad"]

    balance = ingresos - gastos

    return ingresos, gastos, balance


def calcular_totales_mes_actual(movimientos):
    hoy = date.today()

    ingresos_mes = 0
    gastos_mes = 0

    for movimiento in movimientos:
        fecha = movimiento["fecha"]

        if isinstance(fecha, str):
            fecha = date.fromisoformat(fecha)

        if fecha.year == hoy.year and fecha.month == hoy.month:
            if movimiento["tipo"] == "ingreso":
                ingresos_mes += movimiento["cantidad"]
            elif movimiento["tipo"] == "gasto":
                gastos_mes += movimiento["cantidad"]

    balance_mes = ingresos_mes - gastos_mes

    return ingresos_mes, gastos_mes, balance_mes


def preparar_categorias(movimientos):
    gastos_por_categoria = {}

    for movimiento in movimientos:
        if movimiento["tipo"] == "gasto":
            categoria = movimiento["categoria"]
            cantidad = movimiento["cantidad"]

            if categoria not in gastos_por_categoria:
                gastos_por_categoria[categoria] = 0

            gastos_por_categoria[categoria] += cantidad

    if not gastos_por_categoria:
        return [], None, 0

    maximo = max(gastos_por_categoria.values())
    total_gastos_categoria = sum(gastos_por_categoria.values())

    resumen_categorias = []

    for categoria, total in gastos_por_categoria.items():
        porcentaje = 0

        if maximo > 0:
            porcentaje = round((total / maximo) * 100, 2)

        resumen_categorias.append(
            {
                "categoria": categoria,
                "total": total,
                "porcentaje": porcentaje
            }
        )

    resumen_categorias.sort(key=lambda item: item["total"], reverse=True)

    categoria_top = resumen_categorias[0]

    return resumen_categorias, categoria_top, total_gastos_categoria


def preparar_estado_balance(balance):
    if balance > 0:
        return {
            "clase": "positivo",
            "icono": "✅",
            "titulo": "Vas en positivo",
            "mensaje": "Este mes tus ingresos superan tus gastos."
        }

    if balance < 0:
        return {
            "clase": "negativo",
            "icono": "⚠️",
            "titulo": "Cuidado",
            "mensaje": "Este mes estás gastando más de lo que ingresas."
        }

    return {
        "clase": "neutro",
        "icono": "➖",
        "titulo": "Equilibrado",
        "mensaje": "Este mes ingresos y gastos están igualados."
    }


def obtener_anios_disponibles(movimientos):
    hoy = date.today()

    anios = sorted({
        movimiento["fecha"].year
        for movimiento in movimientos
    }, reverse=True)

    if hoy.year not in anios:
        anios.insert(0, hoy.year)

    return anios


def preparar_datos_grafico(movimientos, periodo, mes_seleccionado, anio_seleccionado):
    nombres_meses = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]

    if periodo == "anual":
        labels = [
            "Ene", "Feb", "Mar", "Abr", "May", "Jun",
            "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"
        ]

        ingresos = [0 for _ in range(12)]
        gastos = [0 for _ in range(12)]

        for movimiento in movimientos:
            fecha = movimiento["fecha"]

            if isinstance(fecha, str):
                fecha = date.fromisoformat(fecha)

            if fecha.year == anio_seleccionado:
                indice = fecha.month - 1

                if movimiento["tipo"] == "ingreso":
                    ingresos[indice] += movimiento["cantidad"]
                elif movimiento["tipo"] == "gasto":
                    gastos[indice] += movimiento["cantidad"]

        titulo = f"Ingresos y gastos de {anio_seleccionado}"

    else:
        periodo = "mensual"

        dias_mes = calendar.monthrange(anio_seleccionado, mes_seleccionado)[1]

        labels = [str(dia) for dia in range(1, dias_mes + 1)]
        ingresos = [0 for _ in range(dias_mes)]
        gastos = [0 for _ in range(dias_mes)]

        for movimiento in movimientos:
            fecha = movimiento["fecha"]

            if isinstance(fecha, str):
                fecha = date.fromisoformat(fecha)

            if fecha.year == anio_seleccionado and fecha.month == mes_seleccionado:
                indice = fecha.day - 1

                if movimiento["tipo"] == "ingreso":
                    ingresos[indice] += movimiento["cantidad"]
                elif movimiento["tipo"] == "gasto":
                    gastos[indice] += movimiento["cantidad"]

        nombre_mes = nombres_meses[mes_seleccionado - 1]
        titulo = f"Ingresos y gastos de {nombre_mes} {anio_seleccionado}"

    return {
        "periodo": periodo,
        "titulo": titulo,
        "labels": labels,
        "ingresos": ingresos,
        "gastos": gastos,
        "mes": mes_seleccionado,
        "anio": anio_seleccionado
    }


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

    categorias = [
        "Comida",
        "Transporte",
        "Casa",
        "Ocio",
        "Mascota",
        "Salud",
        "Estudios",
        "Sueldo",
        "Otros"
    ]

    meses = [
        {"numero": 1, "nombre": "Enero"},
        {"numero": 2, "nombre": "Febrero"},
        {"numero": 3, "nombre": "Marzo"},
        {"numero": 4, "nombre": "Abril"},
        {"numero": 5, "nombre": "Mayo"},
        {"numero": 6, "nombre": "Junio"},
        {"numero": 7, "nombre": "Julio"},
        {"numero": 8, "nombre": "Agosto"},
        {"numero": 9, "nombre": "Septiembre"},
        {"numero": 10, "nombre": "Octubre"},
        {"numero": 11, "nombre": "Noviembre"},
        {"numero": 12, "nombre": "Diciembre"}
    ]

    if request.method == "POST":
        tipo = request.form["tipo"]
        descripcion = request.form["descripcion"].strip()
        cantidad = float(request.form["cantidad"])
        categoria = request.form["categoria"]
        fecha = request.form["fecha"]

        guardar_movimiento(
            usuario_id,
            tipo,
            descripcion,
            cantidad,
            categoria,
            fecha
        )

        return redirect(url_for("index", vista="movimientos"))

    vista = request.args.get("vista", "resumen")
    filtro_tipo = request.args.get("tipo")
    busqueda = request.args.get("busqueda", "").strip()
    filtro_categoria = request.args.get("categoria", "").strip()
    periodo_grafico = request.args.get("grafico", "mensual")

    hoy = date.today()

    try:
        mes_grafico = int(request.args.get("mes", hoy.month))
    except ValueError:
        mes_grafico = hoy.month

    try:
        anio_grafico = int(request.args.get("anio", hoy.year))
    except ValueError:
        anio_grafico = hoy.year

    if mes_grafico < 1 or mes_grafico > 12:
        mes_grafico = hoy.month

    if periodo_grafico not in ["mensual", "anual"]:
        periodo_grafico = "mensual"

    if vista not in ["resumen", "movimientos", "categorias", "graficos"]:
        vista = "resumen"

    movimientos_filtrados = cargar_movimientos(
        usuario_id,
        filtro_tipo,
        busqueda,
        filtro_categoria
    )

    todos_los_movimientos = cargar_todos_los_movimientos(usuario_id)

    ingresos, gastos, balance = calcular_totales(todos_los_movimientos)
    ingresos_mes, gastos_mes, balance_mes = calcular_totales_mes_actual(todos_los_movimientos)

    ultimos_movimientos = sorted(
        todos_los_movimientos,
        key=lambda movimiento: (movimiento["fecha"], movimiento["id"]),
        reverse=True
    )[:5]

    resumen_categorias, categoria_top, total_gastos_categoria = preparar_categorias(
        todos_los_movimientos
    )

    estado_balance_mes = preparar_estado_balance(balance_mes)

    anios_disponibles = obtener_anios_disponibles(todos_los_movimientos)

    if anio_grafico not in anios_disponibles:
        anio_grafico = hoy.year

    datos_grafico = preparar_datos_grafico(
        todos_los_movimientos,
        periodo_grafico,
        mes_grafico,
        anio_grafico
    )

    return render_template(
        "index.html",
        vista=vista,
        movimientos=movimientos_filtrados,
        ultimos_movimientos=ultimos_movimientos,
        ingresos=ingresos,
        gastos=gastos,
        balance=balance,
        ingresos_mes=ingresos_mes,
        gastos_mes=gastos_mes,
        balance_mes=balance_mes,
        filtro_tipo=filtro_tipo,
        busqueda=busqueda,
        filtro_categoria=filtro_categoria,
        categorias=categorias,
        resumen_categorias=resumen_categorias,
        categoria_top=categoria_top,
        total_gastos_categoria=total_gastos_categoria,
        estado_balance_mes=estado_balance_mes,
        datos_grafico=datos_grafico,
        meses=meses,
        anios_disponibles=anios_disponibles,
        email=session.get("email")
    )


@app.route("/eliminar/<int:movimiento_id>", methods=["POST"])
def eliminar_movimiento(movimiento_id):
    usuario_id = usuario_actual()

    if usuario_id is None:
        return redirect(url_for("login"))

    eliminar_movimiento_bd(usuario_id, movimiento_id)

    return redirect(url_for("index", vista="movimientos"))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5050)
    