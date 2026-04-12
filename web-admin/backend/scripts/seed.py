import argparse
import getpass
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app
from app.service import seed_rbac
from app.conf.extensions import db
from app.utils import logger


def parse_args():
    parser = argparse.ArgumentParser(description="Seed RBAC baseline data.")
    parser.add_argument("--username", default="admin", help="Admin username")
    parser.add_argument("--email", default="admin@example.com", help="Admin email")
    parser.add_argument(
        "--password",
        default=None,
        help="Admin password (if omitted, interactive prompt is used)",
    )
    parser.add_argument(
        "--create-tables",
        action="store_true",
        help="Create tables before seeding (for fresh local setup)",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    password = args.password
    if not password:
        password = getpass.getpass("Admin password (min 8 chars): ").strip()
    if len(password) < 8:
        raise SystemExit("Password must be at least 8 characters.")

    app = create_app()
    with app.app_context():
        if args.create_tables:
            db.create_all()
        result = seed_rbac(
            admin_username=args.username,
            admin_email=args.email,
            admin_password=password,
        )

    logger.info("Seed completed:")
    logger.info("permissions_created: {}", result["permissions_created"])
    logger.info("permissions_total:   {}", result["permissions_total"])
    logger.info("admin_user_id:       {}", result["admin_user_id"])
    logger.info("admin_role_id:       {}", result["admin_role_id"])


if __name__ == "__main__":
    main()
