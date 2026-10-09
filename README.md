# Jill's Sandwich — API Backend

**Grupo:** Dillinger Systems  
**Integrantes:** Emiliano García · Giuliana Fragapane · Hiro Cruz  
**Trabajo Práctico Integrador** — Gestión de Desarrollo de Software · Tecnicatura en Programación (4° Semestre)

API REST para el panel de administración de un restaurante. Expone endpoints para gestionar pedidos, clientes, menú, mesas, ventas y autenticación con doble nivel de seguridad (token de acceso + token de ventas).

---

## Informe Técnico

[https://drive.google.com/file/d/15zjwHGHLNEHQWSPfXynZBopaJh3G1IA7/view?usp=drive_link](https://drive.google.com/file/d/15zjwHGHLNEHQWSPfXynZBopaJh3G1IA7/view?usp=drive_link)

---

## Demo en línea


| Recurso            | URL                                                     |
| ------------------ | ------------------------------------------------------- |
| **App desplegada** | `https://proyecto-de-gestion-de-restaurante.vercel.app` |


**Repositorios:** [Backend](https://github.com/EmiG4rcia/ProyectoDeGestionDeRestaurante-Back) · [Frontend](https://github.com/EmiG4rcia/ProyectoDeGestionDeRestaurante-Front)

### Credenciales para probar la demo (panel de administración)


| Campo                | Valor        |
| -------------------- | ------------ |
| Usuario              | `admin`      |
| Contraseña           | `admin1234`  |
| Contraseña de ventas | `ventas1234` |


> **Contraseña de ventas:** credencial adicional del administrador. El frontend la solicita al crear/eliminar pedidos, gestionar clientes o registrar pagos. Se valida con `POST /auth/sales-verify` y devuelve un **sales_token** JWT válido 15 minutos. No reemplaza la contraseña de login (`POST /auth/login`).

---

## Descripción

Este backend es la capa de servicios del sistema **Jill's Sandwich**. Persiste la información en **MySQL** mediante **SQLAlchemy** y expone una API tipada con **FastAPI** que consume el panel de administración (React).

Los módulos principales cubren:


| Módulo        | Descripción                                                             |
| ------------- | ----------------------------------------------------------------------- |
| **Auth**      | Login JWT, verificación de ventas, cambio de contraseñas y recuperación |
| **Orders**    | CRUD de pedidos, filtros, resumen del día y flujo de estados            |
| **Customers** | Alta, edición y baja de clientes                                        |
| **Menu**      | Gestión de platos con precio, categoría y disponibilidad                |
| **Tables**    | Control de mesas y generación de QR                                     |
| **Sales**     | Resumen de ingresos y registro de pagos                                 |


---

## Ejecución local

### Requisitos previos

- [Python](https://www.python.org/) ≥ 3.11
- [MySQL](https://www.mysql.com/) ≥ 8.0 (local o servicio en la nube)
- [Git](https://git-scm.com/) (opcional, para clonar el repo)

> En una instalación nueva, `setup_db.py` crea la base de datos, las tablas y los datos iniciales. No hace falta crear las tablas manualmente.

### Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/EmiG4rcia/ProyectoDeGestionDeRestaurante-Back.git
cd ProyectoDeGestionDeRestaurante-Back

# 2. Crear entorno virtual
python -m venv .venv

# Windows
.venv\Scripts\Activate.ps1

# Linux / macOS
source .venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tu DATABASE_URL y SECRET_KEY

# 5. Crear la base de datos y el primer administrador
# Solo es necesario correr este comando UNA SOLA VEZ en una instalación nueva.
# Crea la base de datos, las tablas, el menú inicial, las mesas
# y solicita interactivamente las credenciales del administrador.
python setup_db.py

# 6. Iniciar el servidor
fastapi dev main.py
```

La API estará disponible en **[http://127.0.0.1:8000](http://127.0.0.1:8000)**.  
Documentación Swagger: **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

### Credenciales en entorno local

Si usaste `setup_db.py`, las credenciales son las que definiste al crear el admin. Como referencia para desarrollo (y demo en producción):


| Campo                | Valor sugerido |
| -------------------- | -------------- |
| Usuario              | `admin`        |
| Contraseña           | `admin1234`    |
| Contraseña de ventas | `ventas1234`   |


Alternativa rápida (solo admin, sin seed completo):

```bash
python scripts/seed_admin.py
```

> El **token de ventas** no es una credencial fija en el header: se obtiene en runtime vía `POST /auth/sales-verify` al ingresar la contraseña de ventas (válido 15 minutos).

Para desarrollo local con el frontend, incluir `http://localhost:5173` en `CORS_ORIGINS`.

---

## Stack tecnológico


| Tecnología                                                                        | Uso                                   |
| --------------------------------------------------------------------------------- | ------------------------------------- |
| [FastAPI](https://fastapi.tiangolo.com/)                                          | Framework web y documentación OpenAPI |
| [SQLAlchemy 2](https://www.sqlalchemy.org/)                                       | ORM y mapeo de entidades              |
| [MySQL](https://www.mysql.com/)                                                   | Base de datos relacional              |
| [PyMySQL](https://pypi.org/project/PyMySQL/)                                      | Driver de conexión                    |
| [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) | Configuración vía `.env`              |
| [python-jose](https://python-jose.readthedocs.io/)                                | Tokens JWT                            |
| [passlib + bcrypt](https://passlib.readthedocs.io/)                               | Hash de contraseñas                   |
| [Uvicorn](https://www.uvicorn.org/)                                               | Servidor ASGI                         |


---

## Variables de entorno


| Variable                      | Descripción                              | Ejemplo                                                                       |
| ----------------------------- | ---------------------------------------- | ----------------------------------------------------------------------------- |
| `DATABASE_URL`                | Cadena de conexión SQLAlchemy            | `mysql+pymysql://root@localhost:3306/jills_sandwich`                          |
| `SECRET_KEY`                  | Clave para firmar JWT                    | Clave larga y aleatoria                                                       |
| `ALGORITHM`                   | Algoritmo JWT                            | `HS256`                                                                       |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Duración del token de acceso             | `480`                                                                         |
| `SALES_TOKEN_EXPIRE_MINUTES`  | Duración del token de ventas             | `15`                                                                          |
| `CORS_ORIGINS`                | Orígenes permitidos (separados por coma) | `http://localhost:5173,https://proyecto-de-gestion-de-restaurante.vercel.app` |


---

## Modelo de datos

Entidades principales en MySQL:


| Tabla                       | Descripción                                                        |
| --------------------------- | ------------------------------------------------------------------ |
| `admin_users`               | Usuarios del panel con contraseña y contraseña de ventas hasheadas |
| `customers`                 | Clientes identificados por teléfono                                |
| `tables`                    | Mesas con estado y token QR                                        |
| `menu_items`                | Platos del menú                                                    |
| `orders` / `order_items`    | Pedidos y sus ítems                                                |
| `payments`                  | Pagos asociados a pedidos                                          |
| `sessions` / `message_logs` | Sesiones y logs del canal conversacional (proyecto base)           |


Arquitectura por **features**: cada módulo contiene `models.py`, `schemas.py`, `service.py` y `router.py`. El esquema se crea con `Base.metadata.create_all` (ver `setup_db.py` y `main.py` → `initialize_database()`).

---

## Autenticación

El sistema usa **dos tokens JWT**:

1. `**access_token`** — Se obtiene con `POST /auth/login`. Protege operaciones de lectura y administración general.
2. `**sales_token**` — Se obtiene con `POST /auth/sales-verify` (requiere `access_token` activo). Protege operaciones sensibles: crear/eliminar pedidos, clientes y pagos.

En las peticiones protegidas, enviar el header:

```
Authorization: Bearer <token>
```

Algunos endpoints usan `get_current_admin` y otros `get_sales_access` dentro del mismo router, según el nivel de acceso requerido.

---

## Endpoints principales


| Método                | Ruta                  | Auth           | Descripción              |
| --------------------- | --------------------- | -------------- | ------------------------ |
| GET                   | `/health`             | —              | Health check             |
| POST                  | `/auth/login`         | —              | Iniciar sesión           |
| POST                  | `/auth/sales-verify`  | access         | Obtener token de ventas  |
| GET                   | `/orders`             | access         | Listar pedidos (filtros) |
| GET                   | `/orders/summary`     | access         | KPIs del día             |
| POST                  | `/orders`             | sales          | Crear pedido             |
| PATCH                 | `/orders/{id}/status` | access         | Cambiar estado           |
| GET/POST/PATCH/DELETE | `/customers`          | access / sales | CRUD clientes            |
| GET/POST/PUT/DELETE   | `/menu-items`         | access         | CRUD menú                |
| GET/POST/PUT/DELETE   | `/tables`             | access         | CRUD mesas               |
| GET                   | `/tables/{id}/qr`     | access         | QR de mesa               |
| GET                   | `/sales/summary`      | sales          | Resumen de ventas        |
| GET/POST/PATCH        | `/sales/payments`     | sales          | Gestión de pagos         |


Documentación completa e interactiva en `**/docs**`: `https://proyectodegestionderestaurante-back-production.up.railway.app/docs` (producción) o `http://127.0.0.1:8000/docs` (local).

---

## Estructura del proyecto

```
ProyectoDeGestionDeRestaurante-Back/
├── .github/workflows/  # Pipeline CI (GitHub Actions)
├── core/               # Config, DB, seguridad, dependencias
├── features/
│   ├── auth/           # Autenticación JWT
│   ├── customers/      # Clientes
│   ├── menu/           # Menú
│   ├── orders/         # Pedidos
│   ├── sales/          # Ventas y pagos
│   └── tables/         # Mesas y QR
├── scripts/
│   └── seed_admin.py   # Crear admin (alternativa a setup_db.py)
├── shared/
│   └── uow.py          # Unit of Work (transacciones)
├── main.py             # Punto de entrada FastAPI
├── setup_db.py         # Setup inicial: BD, tablas, seed y admin
├── Procfile            # Comando de inicio en Railway
├── ruff.toml           # Configuración del linter
├── requirements.txt
└── .env.example
```

---

## Despliegue

### Backend — Railway

Este backend está desplegado en [Railway](https://railway.com/) con **deploy automático** al detectar un push a `main`.

1. Conectar el repositorio de GitHub en Railway
2. Runtime: **Python 3.11**
3. Railway detecta `requirements.txt` e instala dependencias
4. El `Procfile` define el comando de inicio: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Configurar variables de entorno: `DATABASE_URL`, `SECRET_KEY`, `CORS_ORIGINS`, etc.
6. Usar MySQL en la nube (Railway MySQL u otro servicio compatible)

**Demo en producción:** `https://proyectodegestionderestaurante-back-production.up.railway.app/docs`

**Health check:** `https://proyectodegestionderestaurante-back-production.up.railway.app/health`

### Frontend — Vercel

El panel React se despliega por separado en Vercel. Configurar `VITE_API_URL` con la URL pública de este backend.

**Demo en producción:** `https://proyecto-de-gestion-de-restaurante.vercel.app`

Repositorio frontend: [ProyectoDeGestionDeRestaurante-Front](https://github.com/EmiG4rcia/ProyectoDeGestionDeRestaurante-Front)

---

## CI — GitHub Actions

En cada **push** o **pull request** a `main`/`master`, el pipeline en `.github/workflows/ci.yml` ejecuta **tres jobs en paralelo**:


| Job                           | Herramienta                                      | Qué valida                                                     |
| ----------------------------- | ------------------------------------------------ | -------------------------------------------------------------- |
| **Lint & Format**             | [Ruff](https://docs.astral.sh/ruff/)             | Estilo de código y errores estáticos (Python 3.11 y 3.12)      |
| **Import & App Verification** | Smoke test                                       | Que la app FastAPI inicialice sin errores (Python 3.11 y 3.12) |
| **Dependency Security Audit** | [pip-audit](https://pypi.org/project/pip-audit/) | Vulnerabilidades conocidas en dependencias (Python 3.12)       |


Si cualquier job falla, el pipeline se marca como fallido.

**Ejecutar checks localmente:**

```bash
pip install ruff
ruff check .
ruff format --check .
```

---

## Herramientas de IA utilizadas


| Herramienta                 | Rol en el proyecto                                                                                      |
| --------------------------- | ------------------------------------------------------------------------------------------------------- |
| **Claude Code** (navegador) | Generación del código backend: modelos, servicios, routers, autenticación JWT y estructura por features |
| **Cursor**                  | Documentación, depuración, scripts de seed, CI/CD y preparación para despliegue                         |


---

## Repositorios relacionados


| Repo                    | Enlace                                                                                                    | Demo                                                                         |
| ----------------------- | --------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| **Frontend**            | [ProyectoDeGestionDeRestaurante-Front](https://github.com/EmiG4rcia/ProyectoDeGestionDeRestaurante-Front) | `https://proyecto-de-gestion-de-restaurante.vercel.app`                      |
| **Backend** (este repo) | [ProyectoDeGestionDeRestaurante-Back](https://github.com/EmiG4rcia/ProyectoDeGestionDeRestaurante-Back)   | `https://proyectodegestionderestaurante-back-production.up.railway.app/docs` |


---

## Licencia

Este proyecto es de código abierto con fines académicos.