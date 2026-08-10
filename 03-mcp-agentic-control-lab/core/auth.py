from enum import Enum
from typing import Dict, Any, Optional
import config

class Role(str, Enum):
    ADMIN = "ADMIN"
    USER = "USER"
    UNKNOWN = "UNKNOWN"

class UserIdentity:
    def __init__(self, email: str):
        self.email = (email or "").strip().lower()
        self.role = self._resolve_role()

    def _resolve_role(self) -> Role:
        if self.email == config.ADMIN_EMAIL:
            return Role.ADMIN
        elif self.email == config.USER_EMAIL:
            return Role.USER
        return Role.UNKNOWN

    def is_authenticated(self) -> bool:
        return self.role in (Role.ADMIN, Role.USER)

    def can_update_policy(self) -> bool:
        return self.role == Role.ADMIN

    def to_dict(self) -> Dict[str, Any]:
        return {
            "email": self.email,
            "role": self.role.value,
            "can_update": self.can_update_policy()
        }

def authenticate_user(email: str) -> UserIdentity:
    return UserIdentity(email)
