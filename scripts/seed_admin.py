"""
Script para crear el primer usuario administrador.

Uso:
    python scripts/seed_admin.py
    python scripts/seed_admin.py --username admin --password admin1234 --sales-password ventas1234
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.database import SessionLocal
from features.auth.service import create_first_admin


def main() -> None:
    parser = argparse.ArgumentParser(description="Crear el primer admin del sistema")
    parser.add_argument("--username", default="admin")
    parser.add_argument("--password", default="admin1234")
    parser.add_argument("--sales-password", default="ventas1234")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        admin, recovery_code = create_first_admin(
            db,
            username=args.username,
            password=args.password,
            sales_password=args.sales_password,
        )
        print("Admin creado correctamente.")
        print(f"  Usuario:           {admin.username}")
        print(f"  Contraseña:        {args.password}")
        print(f"  Contraseña ventas: {args.sales_password}")
        print(f"  Código recuperación: {recovery_code}")
    except Exception as exc:
        print(f"Error: {exc}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
