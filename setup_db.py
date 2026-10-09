import psycopg2
from core.database import engine, Base
from core.config import settings


def create_database():
    url = settings.DATABASE_URL
    parts = url.replace("postgresql://", "").split("/")
    db_name = parts[-1]
    conn_part = parts[0]

    if "@" in conn_part:
        user_pass, host_port = conn_part.split("@")
    else:
        user_pass = conn_part
        host_port = "localhost:5432"

    if ":" in user_pass:
        user, password = user_pass.split(":", 1)
    else:
        user = user_pass
        password = ""

    if ":" in host_port:
        host, port = host_port.split(":")
        port = int(port)
    else:
        host = host_port
        port = 5432

    conn = psycopg2.connect(
        host=host, port=port, user=user, password=password, dbname="postgres"
    )
    conn.autocommit = True
    cursor = conn.cursor()
    cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
    exists = cursor.fetchone()
    if not exists:
        cursor.execute(f'CREATE DATABASE "{db_name}"')
        print(f"Base de datos '{db_name}' creada.")
    else:
        print(f"Base de datos '{db_name}' ya existe.")
    cursor.close()
    conn.close()


def create_tables():
    from features.auth.models import User
    from features.raw_materials.models import RawMaterial
    from features.products.models import Product, ProductRecipe
    from features.production.models import ProductionLog, ProductionLogInput
    from features.stock.models import StockMovement
    from features.destinations.models import Destination
    from features.scheduled_orders.models import ScheduledOrder, ScheduledOrderItem
    from features.deliveries.models import Delivery, DeliveryProduct

    Base.metadata.create_all(bind=engine)
    print("Todas las tablas creadas.")


def create_first_user(db):
    from features.auth.models import User
    from passlib.context import CryptContext
    import getpass

    if db.query(User).first():
        print("Ya existe un usuario — omitiendo.")
        return

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    print("\n=== CREAR USUARIO DUEÑO ===")
    username = input("Username (default: admin): ").strip() or "admin"
    password = getpass.getpass("Contraseña: ")

    user = User(
        username=username,
        password_hash=pwd_context.hash(password),
        role="owner",
        is_active=True,
    )
    db.add(user)
    db.commit()
    print(f"\nUsuario '{username}' creado con rol 'owner'.")


if __name__ == "__main__":
    print("\n=== Gestión de Negocio — Setup ===\n")

    create_database()
    create_tables()

    from core.database import SessionLocal
    db = SessionLocal()
    try:
        create_first_user(db)
    finally:
        db.close()

    print("\n=== Setup completo. Corré 'fastapi dev main.py' para iniciar. ===\n")