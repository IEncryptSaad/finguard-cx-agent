from fastapi import Depends, Header, HTTPException, status
from app.models.schemas import Role, User
from app.core.config import get_settings
from app.auth.rbac import can_access


def _user_from_headers(x_finguard_role: str | None, x_finguard_actor: str | None) -> User | None:
    if x_finguard_role is None:
        return None
    try:
        role = Role(x_finguard_role)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid role')
    return User(id=x_finguard_actor or role.value, email=f'{x_finguard_actor or role.value}@local', role=role)


def current_user(x_finguard_role: str | None = Header(default=None), x_finguard_actor: str | None = Header(default=None)) -> User:
    user = _user_from_headers(x_finguard_role, x_finguard_actor)
    if user is not None:
        return user
    if not get_settings().auth_required and get_settings().app_env != 'production':
        return User(id='local-admin', email='local-admin@local', role=Role.admin)
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication required')


def require(permission: str):
    def dep(user: User = Depends(current_user)):
        if not can_access(user.role, permission):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Insufficient permissions')
        return user
    return dep


def require_demo_admin_read(permission: str):
    def dep(x_finguard_role: str | None = Header(default=None), x_finguard_actor: str | None = Header(default=None)):
        user = _user_from_headers(x_finguard_role, x_finguard_actor)
        if user is not None:
            if not can_access(user.role, permission):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Insufficient permissions')
            return user
        settings = get_settings()
        if settings.demo_admin_read_access:
            return User(id='demo-admin-readonly', email='demo-admin-readonly@local', role=Role.agent)
        return current_user(x_finguard_role, x_finguard_actor)
    return dep


def require_chat_access(x_finguard_role: str | None = Header(default=None), x_finguard_actor: str | None = Header(default=None)) -> User | None:
    settings = get_settings()
    user = _user_from_headers(x_finguard_role, x_finguard_actor)
    if user is None:
        if settings.public_customer_chat:
            return None
        if not settings.auth_required and settings.app_env != 'production':
            return User(id='local-admin', email='local-admin@local', role=Role.admin)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication required')
    if not can_access(user.role, 'chat:create'):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Insufficient permissions')
    return user
