from sqlalchemy.orm import Session

from app.interfaces import users as UserInterfaces
from app.exceptions import UserNotFoundError
from app.models import User

class UserRepository:
    """User Repository implementation"""
    def __init__(self, db: Session):
        self.db = db

    def get_user(self, _id: int) -> User:
        """get user by id"""
        user = self.db.query(User).filter(User.id == _id).first()
        if user is None:
            raise UserNotFoundError()
        return user

    def create_user(self, info: UserInterfaces.CreateUserInfo) -> User:
        """Create a new user"""
        user: User = User(**info.model_dump())
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_user(self, info: UserInterfaces.UpdateUserInfo) -> User:
        """更新用戶資料"""
        user: User = self.db.query(User).filter(User.id == info.id).first()
        if user is None:
            raise UserNotFoundError()
        user.update(info.model_dump())
        self.db.add(user)
        self.db.commit()
        return user
    
    def update_password(self, info: UserInterfaces.UpdateUserPassword) -> User:
        """更新用戶密碼"""
        user: User = self.db.query(User).filter(User.id == info.id).first()
        if user is None:
            raise UserNotFoundError()
        user.update(info.model_dump())
        self.db.add(user)
        self.db.commit()
        return user

    def delete_user(self, _id: int) -> bool:
        """刪除用戶 (soft delete)"""
        self.db.query(User).filter(User.id == _id).delete()
        self.db.commit()
        return self.db.query(User).filter(User.id == _id).first() is None
