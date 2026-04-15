from __future__ import annotations


def permission_to_dict(permission) -> dict:
    return {
        "id": permission.id,
        "name": permission.name,
        "code": permission.code,
        "description": permission.description,
    }


def role_to_dict(role, include_permissions: bool = False) -> dict:
    data = {
        "id": role.id,
        "name": role.name,
        "description": role.description,
        "created_at": role.created_at.isoformat() if role.created_at else None,
        "permission_count": len(role.permissions),
    }
    if include_permissions:
        data["permissions"] = [permission_to_dict(item) for item in role.permissions]
    return data


def user_to_dict(user, include_roles: bool = True) -> dict:
    data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }
    if include_roles:
        data["roles"] = [role.name for role in user.roles]
    return data


def menu_to_dict(menu) -> dict:
    return {
        "id": menu.id,
        "name": menu.name,
        "parent_id": menu.parent_id,
        "route_path": menu.route_path,
        "icon": menu.icon,
        "sort": menu.sort,
        "is_visible": menu.is_visible,
        "is_enabled": menu.is_enabled,
        "permission_code": menu.permission_code,
        "created_at": menu.created_at.isoformat() if menu.created_at else None,
        "updated_at": menu.updated_at.isoformat() if menu.updated_at else None,
    }


__all__ = ["menu_to_dict", "permission_to_dict", "role_to_dict", "user_to_dict"]
