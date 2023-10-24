from sqlalchemy.orm import Session
from app.interfaces import users as UserInterfaces
from app.exceptions import UserNotFoundError
from app.models import User
from datetime import datetime

class UserRepository:
    """User Repository implementation"""
    def get_user(self, db: Session, _id: int) -> User:
        """get user by id"""
        return db.query(User).filter(User.id == _id).first()

    def create_user(self, db: Session, info: UserInterfaces.CreateUserInfo) -> User:
        """Create a new user"""
        user = User(**info.model_dump())
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def update_user(self, db: Session, info: UserInterfaces.UpdateUserInfo) -> User:
        """更新用戶資料"""
        user = db.query(User).filter(User.id == info.id)
        user.update(**info.model_dump())
        db.commit()
        user = user.first()
        if user is None:
            raise UserNotFoundError("找不到用戶")
        return user

    def delete_user(self, db: Session, _id: int) -> None:
        user: User = db.query(User).filter(User.id == _id).first()
        if user is None:
            raise UserNotFoundError("找不到用戶")
        user.deleted_at = datetime.now()
        user.is_deleted = True