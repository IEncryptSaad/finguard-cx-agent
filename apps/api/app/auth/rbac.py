from app.models.schemas import Role
def can_access(role: Role, permission: str) -> bool:
    permissions = {Role.admin: {"*"}, Role.agent: {"ticket:read", "ticket:update", "chat:handoff"}, Role.customer: {"chat:create"}}
    allowed = permissions[role]
    return "*" in allowed or permission in allowed
