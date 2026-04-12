from datetime import datetime

from ..conf.extensions import bcrypt
from .base import db

user_roles = db.Table(
    "user_roles",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    db.Column("role_id", db.Integer, db.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)

role_permissions = db.Table(
    "role_permissions",
    db.Column("role_id", db.Integer, db.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    db.Column(
        "permission_id",
        db.Integer,
        db.ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Permission(db.Model):
    __tablename__ = "permissions"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    code = db.Column(db.String(128), nullable=False, unique=True, index=True)
    description = db.Column(db.String(255))

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "description": self.description,
        }


class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True, index=True)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    users = db.relationship("User", secondary=user_roles, back_populates="roles")
    permissions = db.relationship("Permission", secondary=role_permissions, backref="roles")

    def to_dict(self, include_permissions=False):
        data = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "permission_count": len(self.permissions),
        }
        if include_permissions:
            data["permissions"] = [item.to_dict() for item in self.permissions]
        return data


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False, unique=True, index=True)
    email = db.Column(db.String(128), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    roles = db.relationship("Role", secondary=user_roles, back_populates="users")

    def set_password(self, plain_password):
        self.password_hash = bcrypt.generate_password_hash(plain_password).decode("utf-8")

    def check_password(self, plain_password):
        try:
            return bcrypt.check_password_hash(self.password_hash, plain_password)
        except (TypeError, ValueError):
            # Corrupted or legacy plaintext hash should not crash login API.
            return False

    def has_permission(self, permission_code):
        if any(role.name == "admin" for role in self.roles):
            return True
        permission_codes = {
            permission.code for role in self.roles for permission in role.permissions
        }
        return permission_code in permission_codes

    def to_dict(self, include_roles=True):
        data = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
        }
        if include_roles:
            data["roles"] = [role.name for role in self.roles]
        return data


class TokenBlocklist(db.Model):
    __tablename__ = "token_blocklist"

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, unique=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


__all__ = [
    "Permission",
    "Role",
    "TokenBlocklist",
    "User",
    "role_permissions",
    "user_roles",
]
