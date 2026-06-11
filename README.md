# 💰 MoneyControl

MoneyControl es una aplicación web desarrollada con Flask para gestionar ingresos, gastos y balance personal.

La aplicación permite registrar movimientos, clasificarlos por categoría, eliminarlos y consultar un resumen financiero. Los datos se almacenan en una base de datos PostgreSQL alojada en Supabase.

## 🌐 Demo online

Puedes probar la aplicación aquí:

[Ver MoneyControl online](https://moneycontrol-cx2j.onrender.com)

## Funcionalidades

- Registrar ingresos
- Registrar gastos
- Añadir descripción, cantidad, categoría y fecha
- Ver resumen de ingresos, gastos y balance
- Consultar movimientos en una tabla
- Eliminar movimientos
- Guardar los datos en PostgreSQL
- Separar los movimientos por navegador mediante un identificador de usuario

## Tecnologías utilizadas

- Python
- Flask
- PostgreSQL
- Supabase
- HTML
- CSS
- Render
- Git y GitHub

## Estructura del proyecto

```text
gestor-gastos-python/
├── app.py
├── main.py
├── requirements.txt
├── README.md
├── templates/
│   └── index.html
└── static/
    └── style.css
