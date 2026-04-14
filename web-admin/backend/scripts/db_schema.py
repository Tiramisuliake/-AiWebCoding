from __future__ import annotations

import argparse
import keyword
import re
import sys
from pathlib import Path
from typing import Any

from sqlalchemy import MetaData, create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.sql.sqltypes import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    Float,
    Integer,
    JSON,
    LargeBinary,
    Numeric,
    SmallInteger,
    String,
    Text,
    Time,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app
from app.database import create_all
from app.utils import logger

DEFAULT_MODELS_PATH = PROJECT_ROOT / "app" / "rbac" / "models_reflected.py"


def _quote_mysql(name: str) -> str:
    return f"`{name.replace('`', '``')}`"


def _quote_postgres(name: str) -> str:
    escaped = name.replace('"', '""')
    return f'"{escaped}"'


def _resolve_uri(uri: str | None, env: str) -> str:
    if uri:
        return uri
    app = create_app(config_name=env)
    value = app.config.get("SQLALCHEMY_DATABASE_URI")
    if not value:
        raise RuntimeError("SQLALCHEMY_DATABASE_URI is empty. Pass --uri or configure env.")
    return value


def ensure_database_exists(uri: str) -> None:
    url = make_url(uri)

    if not url.database and not url.drivername.startswith("sqlite"):
        raise RuntimeError("Database name is missing in URI.")

    if url.drivername.startswith("sqlite"):
        if url.database and url.database != ":memory:":
            Path(url.database).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
        return

    if url.drivername.startswith("mysql"):
        admin_url = url.set(database="mysql")
        with create_engine(admin_url).begin() as conn:
            conn.execute(
                text(
                    f"CREATE DATABASE IF NOT EXISTS {_quote_mysql(url.database)} "
                    "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                )
            )
        return

    if url.drivername.startswith("postgresql"):
        admin_url = url.set(database="postgres")
        with create_engine(admin_url, isolation_level="AUTOCOMMIT").connect() as conn:
            exists = conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :name"), {"name": url.database}
            ).scalar()
            if not exists:
                conn.execute(text(f"CREATE DATABASE {_quote_postgres(url.database)}"))
        return

    raise RuntimeError(f"Unsupported driver for create-db: {url.drivername}")


def init_db_from_orm(uri: str, env: str) -> None:
    overrides = {"SQLALCHEMY_DATABASE_URI": uri}
    app = create_app(config_name=env, config_overrides=overrides)
    with app.app_context():
        import app.database.models  # noqa: F401
        import app.rbac.models  # noqa: F401

        create_all()


def _snake_to_camel(name: str) -> str:
    return "".join(part.capitalize() for part in re.split(r"[^a-zA-Z0-9]+", name) if part) or "Model"


def _safe_attr(name: str) -> str:
    value = re.sub(r"\W+", "_", name)
    if not value:
        value = "field"
    if value[0].isdigit():
        value = f"f_{value}"
    if keyword.iskeyword(value):
        value = f"{value}_"
    return value


def _type_expr(col_type: Any) -> str:
    if isinstance(col_type, String):
        return f"String({col_type.length})" if col_type.length else "String"
    if isinstance(col_type, Text):
        return "Text"
    if isinstance(col_type, BigInteger):
        return "BigInteger"
    if isinstance(col_type, SmallInteger):
        return "SmallInteger"
    if isinstance(col_type, Integer):
        return "Integer"
    if isinstance(col_type, Boolean):
        return "Boolean"
    if isinstance(col_type, DateTime):
        return "DateTime"
    if isinstance(col_type, Date):
        return "Date"
    if isinstance(col_type, Time):
        return "Time"
    if isinstance(col_type, Float):
        return "Float"
    if isinstance(col_type, Numeric):
        if col_type.precision is not None and col_type.scale is not None:
            return f"Numeric({col_type.precision}, {col_type.scale})"
        return "Numeric"
    if isinstance(col_type, JSON):
        return "JSON"
    if isinstance(col_type, LargeBinary):
        return "LargeBinary"
    return "String"


def _is_association_table(table: Any) -> bool:
    cols = list(table.columns)
    return len(cols) == 2 and all(col.primary_key and col.foreign_keys for col in cols)


def _column_code(column: Any, with_name: bool) -> str:
    args: list[str] = []
    if with_name:
        args.append(f'"{column.name}"')
    args.append(_type_expr(column.type))

    first_fk = next(iter(column.foreign_keys), None)
    if first_fk is not None:
        target = str(first_fk.column)
        fk_code = f'ForeignKey("{target}"'
        ondelete = getattr(first_fk, "ondelete", None)
        if ondelete:
            fk_code += f', ondelete="{ondelete}"'
        fk_code += ")"
        args.append(fk_code)

    kwargs: list[str] = []
    if column.primary_key:
        kwargs.append("primary_key=True")
    elif not column.nullable:
        kwargs.append("nullable=False")

    if column.unique:
        kwargs.append("unique=True")
    if column.index:
        kwargs.append("index=True")

    return f"Column({', '.join(args + kwargs)})"


def _plural_table_attr(table_name: str) -> str:
    return table_name if table_name.endswith("s") else f"{table_name}s"


def _render_models_file(metadata: MetaData) -> str:
    tables = sorted(metadata.tables.values(), key=lambda t: t.name)
    assoc_tables = [t for t in tables if _is_association_table(t)]
    entity_tables = [t for t in tables if not _is_association_table(t)]

    class_map = {table.name: _snake_to_camel(table.name) for table in entity_tables}
    relationships: dict[str, list[str]] = {table.name: [] for table in entity_tables}

    assoc_vars: dict[str, str] = {}
    for table in assoc_tables:
        assoc_var = _safe_attr(table.name)
        assoc_vars[table.name] = assoc_var
        targets = [next(iter(col.foreign_keys)).column.table.name for col in table.columns]
        if len(targets) != 2:
            continue
        left_table, right_table = targets[0], targets[1]
        if left_table not in class_map or right_table not in class_map:
            continue

        left_attr = _plural_table_attr(right_table)
        right_attr = _plural_table_attr(left_table)

        left_code = (
            f'    {left_attr} = relationship('
            f'"{class_map[right_table]}", secondary={assoc_var}, back_populates="{right_attr}")'
        )
        right_code = (
            f'    {right_attr} = relationship('
            f'"{class_map[left_table]}", secondary={assoc_var}, back_populates="{left_attr}")'
        )

        if left_code not in relationships[left_table]:
            relationships[left_table].append(left_code)
        if right_code not in relationships[right_table]:
            relationships[right_table].append(right_code)

    lines: list[str] = [
        "from __future__ import annotations",
        "",
        "from sqlalchemy import (",
        "    BigInteger,",
        "    Boolean,",
        "    Column,",
        "    Date,",
        "    DateTime,",
        "    Float,",
        "    ForeignKey,",
        "    Integer,",
        "    JSON,",
        "    LargeBinary,",
        "    Numeric,",
        "    SmallInteger,",
        "    String,",
        "    Table,",
        "    Text,",
        "    Time,",
        ")",
        "from sqlalchemy.orm import relationship",
        "",
        "from ..conf.extensions import bcrypt",
        "from ..database.base import Base",
        "",
    ]

    for table in assoc_tables:
        assoc_var = assoc_vars[table.name]
        lines.append(f"{assoc_var} = Table(")
        lines.append(f'    "{table.name}",')
        lines.append("    Base.metadata,")
        for column in table.columns:
            lines.append(f"    {_column_code(column, with_name=True)},")
        lines.append(")")
        lines.append("")

    for table in entity_tables:
        class_name = class_map[table.name]
        lines.append(f"class {class_name}(Base):")
        lines.append(f'    __tablename__ = "{table.name}"')
        lines.append("")

        for column in table.columns:
            attr = _safe_attr(column.name)
            lines.append(f"    {attr} = {_column_code(column, with_name=False)}")

        rels = relationships[table.name]
        if rels:
            lines.append("")
            lines.extend(rels)

        if table.name == "permissions":
            lines.append("")
            lines.append("    def to_dict(self):")
            lines.append("        return {")
            lines.append('            "id": self.id,')
            lines.append('            "name": self.name,')
            lines.append('            "code": self.code,')
            lines.append('            "description": self.description,')
            lines.append("        }")
        elif table.name == "roles":
            lines.append("")
            lines.append("    def to_dict(self, include_permissions=False):")
            lines.append("        data = {")
            lines.append('            "id": self.id,')
            lines.append('            "name": self.name,')
            lines.append('            "description": self.description,')
            lines.append('            "created_at": self.created_at.isoformat() if self.created_at else None,')
            lines.append('            "permission_count": len(getattr(self, "permissions", [])),')
            lines.append("        }")
            lines.append("        if include_permissions:")
            lines.append('            data["permissions"] = [item.to_dict() for item in self.permissions]')
            lines.append("        return data")
        elif table.name == "users":
            lines.append("")
            lines.append("    def set_password(self, plain_password):")
            lines.append("        self.password_hash = bcrypt.generate_password_hash(plain_password).decode(\"utf-8\")")
            lines.append("")
            lines.append("    def check_password(self, plain_password):")
            lines.append("        try:")
            lines.append("            return bcrypt.check_password_hash(self.password_hash, plain_password)")
            lines.append("        except (TypeError, ValueError):")
            lines.append("            return False")
            lines.append("")
            lines.append("    def has_permission(self, permission_code):")
            lines.append("        if any(role.name == \"admin\" for role in getattr(self, \"roles\", [])):")
            lines.append("            return True")
            lines.append("        permission_codes = {")
            lines.append("            permission.code")
            lines.append("            for role in getattr(self, \"roles\", [])")
            lines.append("            for permission in getattr(role, \"permissions\", [])")
            lines.append("        }")
            lines.append("        return permission_code in permission_codes")
            lines.append("")
            lines.append("    def to_dict(self, include_roles=True):")
            lines.append("        data = {")
            lines.append('            "id": self.id,')
            lines.append('            "username": self.username,')
            lines.append('            "email": self.email,')
            lines.append('            "is_active": self.is_active,')
            lines.append('            "created_at": self.created_at.isoformat() if self.created_at else None,')
            lines.append("        }")
            lines.append("        if include_roles:")
            lines.append('            data["roles"] = [role.name for role in getattr(self, \"roles\", [])]')
            lines.append("        return data")

        lines.append("")

    exported = [class_map[name] for name in sorted(class_map)] + [
        assoc_vars[name] for name in sorted(assoc_vars)
    ]
    lines.append("__all__ = [")
    for name in exported:
        lines.append(f'    "{name}",')
    lines.append("]")
    lines.append("")

    return "\n".join(lines)


def reflect_models(uri: str, output: Path) -> None:
    url = make_url(uri)
    engine = create_engine(url)
    metadata = MetaData()
    metadata.reflect(bind=engine)

    content = _render_models_file(metadata)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Database bootstrap and ORM model generation helper."
    )
    subparsers = parser.add_subparsers(dest="command", required=False)

    init_cmd = subparsers.add_parser(
        "init-db", help="Ensure database exists and create tables from app ORM models."
    )
    init_cmd.add_argument("--uri", help="SQLAlchemy URI, overrides env config.")
    init_cmd.add_argument("--env", default="development", help="App config env name.")

    reflect_cmd = subparsers.add_parser(
        "reflect-models",
        help="Reflect current database schema and generate SQLAlchemy Base models.",
    )
    reflect_cmd.add_argument("--uri", help="SQLAlchemy URI, overrides env config.")
    reflect_cmd.add_argument("--env", default="development", help="App config env name.")
    reflect_cmd.add_argument(
        "--output",
        default=str(DEFAULT_MODELS_PATH),
        help="Target file path for generated models file.",
    )

    args = parser.parse_args()
    command = args.command or "init-db"
    env = getattr(args, "env", "development")
    uri = _resolve_uri(getattr(args, "uri", None), env)

    if command == "init-db":
        ensure_database_exists(uri)
        init_db_from_orm(uri, env)
        logger.info("Database initialized from ORM successfully.")
        return

    if command == "reflect-models":
        output = Path(args.output).expanduser().resolve()
        reflect_models(uri, output)
        logger.info("Models reflected to: {}", output)
        return

    raise RuntimeError(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
