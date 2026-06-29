from app.models.schemas import Role

def can_access(role: Role, permission: str) -> bool:
    permissions = {
        Role.admin: {'*'},
        Role.agent: {'conversation:read','ticket:read','ticket:create','ticket:update','knowledge:read','audit:read','analytics:read','assistant:use'},
        Role.customer: {'chat:create','ticket:create'},
    }
    allowed = permissions[role]
    return '*' in allowed or permission in allowed
