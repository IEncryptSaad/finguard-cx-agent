from fastapi import Depends, Header, HTTPException, status
from app.models.schemas import Role, User
from app.core.config import get_settings
from app.auth.rbac import can_access

def current_user(x_finguard_role: str | None = Header(default=None), x_finguard_actor: str | None = Header(default=None)) -> User:
    if x_finguard_role is None:
        if not get_settings().auth_required and get_settings().app_env != 'production':
            return User(id='local-admin', email='local-admin@local', role=Role.admin)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication required')
    try: role = Role(x_finguard_role)
    except ValueError: raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid role')
    return User(id=x_finguard_actor or role.value, email=f'{x_finguard_actor or role.value}@local', role=role)

def require(permission: str):
    def dep(user: User = Depends(current_user)):
        if not can_access(user.role, permission):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Insufficient permissions')
        return user
    return dep
