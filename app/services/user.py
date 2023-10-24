from passlib.context import CryptContext
from app.repositories import UserRepository
from app.interfaces import CreateUserInfo, UpdateUserInfo, UpdateUserPassword
from app.models import User

class UserService:
    def __init__(self, user_repo: UserRepository, crypto_context: CryptContext):
        self.user_repo = user_repo
        self.crypto_context = crypto_context
    
    def get_user_by_id(self, user_id: int) -> User:
        """獲取用戶資訊"""
        return self.user_repo.get_user(user_id)
    
    def create_user(self, info: CreateUserInfo) -> User:
        """創建用戶"""
        info.password = self.crypto_context.hash(info.password)
        user: User = self.user_repo.create_user(info)
        return user
    
    def update_user_by_id(self, info: UpdateUserInfo):
        """更新用戶資訊"""
        return self.user_repo.update_user(info)
    
    def update_user_password_by_id(self, info: UpdateUserPassword) -> User:
        """更新用戶密碼"""
        info.password = self.crypto_context.hash(info.password)
        return self.user_repo.update_password(info)
    
    def delete_user_by_id(self, user_id: int) -> bool:
        """刪除用戶"""
        return self.user_repo.delete_user(user_id)