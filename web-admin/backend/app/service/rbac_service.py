from ..conf.extensions import db
from ..const.permissions import DEFAULT_PERMISSION_CODES
from ..database.models import Permission, Role, User


def seed_rbac(admin_username, admin_email, admin_password):
    created_permissions = 0
    for code in DEFAULT_PERMISSION_CODES:
        permission = Permission.query.filter_by(code=code).first()
        if permission is None:
            permission = Permission(
                name=code.replace(":", " ").title(),
                code=code,
                description=f"{code} permission",
            )
            db.session.add(permission)
            created_permissions += 1

    db.session.flush()

    all_permissions = Permission.query.order_by(Permission.id.asc()).all()
    admin_role = Role.query.filter_by(name="admin").first()
    if admin_role is None:
        admin_role = Role(name="admin", description="System administrator")
        db.session.add(admin_role)
        db.session.flush()
    admin_role.permissions = all_permissions

    admin_user = User.query.filter_by(username=admin_username).first()
    if admin_user is None:
        admin_user = User(
            username=admin_username,
            email=admin_email,
            is_active=True,
        )
        admin_user.set_password(admin_password)
        db.session.add(admin_user)
        db.session.flush()
    else:
        if admin_user.email != admin_email:
            admin_user.email = admin_email
        if admin_password:
            admin_user.set_password(admin_password)

    if admin_role not in admin_user.roles:
        admin_user.roles.append(admin_role)

    db.session.commit()
    return {
        "permissions_created": created_permissions,
        "permissions_total": len(all_permissions),
        "admin_user_id": admin_user.id,
        "admin_role_id": admin_role.id,
    }