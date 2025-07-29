from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.auth import UserCreate

class UserService:
    def __init__(self, db: Session):
        self.db = db

    async def get_user_by_email(self, email: str) -> User | None:
        # Logic to get user by email will go here
        pass

    async def create_user(self, user_in: UserCreate) -> User:
        # Logic to create a new user will go here
        pass
