from app.models import User
from sqlmodel import Session, select


class SetupService:
    def __init__(self, session: Session):
        self.session = session

    def _create_user(self, name: str) -> User:
        user = User(name=name)
        self.session.add(user)
        self.session.flush()
        self.session.refresh(user)
        return user

    def get_user(self, user_id: int | None, name: str | None = None) -> User:
        if user_id is not None:
            user = self.session.exec(select(User).where(User.id == user_id)).first()
            if user:
                return user
        if not name:
            raise ValueError("Cannot create user without a name")
        return self._create_user(name)