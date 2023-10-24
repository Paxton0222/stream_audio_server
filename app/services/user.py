from sqlalchemy.orm import Session
from app.repositories import UserRepository
from app.interfaces import CreateUserInfo, UpdateUserInfo
from app.models import User

class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.userRepo = UserRepository()
    
    def create_user(self, info: CreateUserInfo):
        user: User = self.userRepo.create_user(info)
        return user
    
    def update_user(self, info: UpdateUserInfo):
        return self.userRepo.update_user(info)
    
    def delete_user(self, user_id: int):
        return self.userRepo.delete_user(self.db, user_id)