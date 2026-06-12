# 💰 MoneyControl

MoneyControl es una aplicación web full stack desarrollada con **Python, Flask y PostgreSQL** para gestionar ingresos, gastos y balance personal.

El proyecto está enfocado como una aplicación de portfolio, aplicando conceptos de backend, base de datos relacional, Docker, Docker Compose, variables de entorno, despliegue online y control de versiones con Git/GitHub.

## 🌐 Demo online

Puedes probar la aplicación aquí:

[Ver MoneyControl online](https://moneycontrol-cx2j.onrender.com)

> Nota: la demo online puede tardar unos segundos en cargar si el servicio está inactivo.

## Funcionalidades

* Registrar ingresos
* Registrar gastos
* Añadir descripción, cantidad, categoría y fecha
* Ver resumen de ingresos, gastos y balance
* Consultar movimientos en una tabla
* Eliminar movimientos
* Guardar los datos en PostgreSQL
* Separar movimientos por usuario mediante sesión

## Tecnologías utilizadas

* Python
* Flask
* PostgreSQL
* HTML
* CSS
* Docker
* Docker Compose
* Render
* Git
* GitHub

## Objetivo del proyecto

El objetivo de MoneyControl es desarrollar una aplicación web realista y progresiva, empezando desde una versión básica en Python y evolucionando hacia una aplicación más profesional.

Durante el desarrollo se han aplicado conceptos como:

* Creación de rutas con Flask
* Gestión de formularios con métodos GET y POST
* Operaciones CRUD
* Conexión con base de datos PostgreSQL
* Uso de variables de entorno
* Separación de datos por sesión
* Dockerización de una aplicación Flask
* Ejecución local con Docker Compose
* Despliegue online
* Control de versiones con Git y GitHub

## Estructura del proyecto

```text
gestor-gastos-python/
├── app.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .env.example
├── .gitignore
├── README.md
├── sql/
│   └── schema.sql
├── static/
│   └── style.css
└── templates/
    └── index.html
```

## Ejecución con Docker Compose

El proyecto puede ejecutarse localmente con Docker Compose, levantando tanto la aplicación Flask como una base de datos PostgreSQL local.

### 1. Clonar el repositorio

```bash
git clone https://github.com/devling02/gestor-gastos-python.git
```

### 2. Entrar en la carpeta del proyecto

```bash
cd gestor-gastos-python
```

### 3. Levantar los servicios

```bash
docker compose up --build
```

### 4. Abrir la aplicación

```text
http://127.0.0.1:5050
```

Docker Compose levantará dos servicios:

```text
moneycontrol_app  -> Aplicación Flask
moneycontrol_db   -> Base de datos PostgreSQL
```

Los datos se guardan en un volumen de Docker llamado `postgres_data`, por lo que no se pierden al apagar los contenedores.

Para apagar los servicios:

```bash
docker compose down
```

## Ejecución local con Python

También se puede ejecutar la aplicación directamente con Python.

### 1. Clonar el repositorio

```bash
git clone https://github.com/devling02/gestor-gastos-python.git
```

### 2. Entrar en la carpeta

```bash
cd gestor-gastos-python
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Crear un archivo `.env`

Usa como referencia el archivo `.env.example`.

```env
DATABASE_URL=tu_url_de_postgresql
SECRET_KEY=tu_clave_secreta
```

### 5. Ejecutar la aplicación

```bash
python app.py
```

### 6. Abrir en el navegador

```text
http://127.0.0.1:5050
```

## Base de datos

La aplicación utiliza PostgreSQL como base de datos relacional.

La estructura inicial de la tabla principal se encuentra en:

```text
sql/schema.sql
```

Tabla principal:

```text
movimientos
```

Campos principales:

* `id`
* `usuario_id`
* `tipo`
* `descripcion`
* `cantidad`
* `categoria`
* `fecha`

## Variables de entorno

El proyecto utiliza variables de entorno para evitar guardar credenciales directamente en el código.

Ejemplo:

```env
DATABASE_URL=postgresql://postgres:postgres@db:5432/moneycontrol
SECRET_KEY=change-this-secret-key
```

El archivo `.env` no debe subirse al repositorio.

## Docker

El proyecto incluye configuración con Docker para facilitar su ejecución en entornos locales de forma reproducible.

Con Docker Compose se levantan la aplicación y la base de datos en contenedores separados, simulando una arquitectura más cercana a un entorno profesional.

## Estado del proyecto

Proyecto en desarrollo activo como parte de mi portfolio de aprendizaje en desarrollo web.

## Próximas mejoras

* Añadir autenticación real con registro e inicio de sesión
* Cifrar contraseñas de usuario
* Asociar movimientos a usuarios registrados
* Añadir filtros por mes y categoría
* Añadir edición de movimientos
* Crear gráficos de ingresos y gastos
* Mejorar validaciones de formularios
* Añadir tests básicos
* Mejorar la estructura interna del proyecto
* Preparar una versión de producción más robusta

