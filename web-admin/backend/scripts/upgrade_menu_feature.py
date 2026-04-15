import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app
from app.database.conn import create_all
from app.service import seed_rbac
from app.utils import logger


def parse_args():
    parser = argparse.ArgumentParser(
        description="Upgrade existing RBAC schema/data for menu management feature."
    )
    parser.add_argument("--env", default="development", help="App config env name.")
    parser.add_argument("--username", default="admin", help="Admin username for seed sync.")
    parser.add_argument("--email", default="admin@example.com", help="Admin email for seed sync.")
    parser.add_argument(
        "--password",
        default="password123",
        help="Admin password for seed sync (min 8 chars).",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    if len(args.password) < 8:
        raise SystemExit("Password must be at least 8 characters.")

    app = create_app(config_name=args.env)
    with app.app_context():
        create_all()
        result = seed_rbac(
            admin_username=args.username,
            admin_email=args.email,
            admin_password=args.password,
        )

    logger.info("Menu feature upgrade completed:")
    logger.info("permissions_created: {}", result["permissions_created"])
    logger.info("permissions_total:   {}", result["permissions_total"])
    logger.info("menus_created:       {}", result["menus_created"])
    logger.info("menus_total:         {}", result["menus_total"])
    logger.info("admin_user_id:       {}", result["admin_user_id"])
    logger.info("admin_role_id:       {}", result["admin_role_id"])


if __name__ == "__main__":
    main()
