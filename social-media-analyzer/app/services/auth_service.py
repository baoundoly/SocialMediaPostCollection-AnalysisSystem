from sqlalchemy.orm import Session
from typing import Optional
from app.models.user import User
from app.models.role import Role
from app.models.audit_log import AuditLog
from app.core.security import verify_password, get_password_hash, create_access_token
from datetime import timedelta
from app.core.config import settings

class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def login(self, email: str, password: str, ip_address: str = "unknown") -> Optional[str]:
        user = self.db.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.password_hash):
            return None
        if user.status != "active":
            return None
        token = create_access_token(
            {"sub": str(user.id), "role_id": user.role_id},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        log = AuditLog(user_id=user.id, action="login", module_name="auth", ip_address=ip_address)
        self.db.add(log)
        self.db.commit()
        return token

    def register(self, full_name: str, email: str, password: str, role_id: int = 3) -> Optional[User]:
        if self.db.query(User).filter(User.email == email).first():
            return None
        role = self.db.query(Role).filter(Role.id == role_id).first()
        if not role:
            role_id = 3
        user = User(
            full_name=full_name,
            email=email,
            password_hash=get_password_hash(password),
            role_id=role_id,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
