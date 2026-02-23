import re
import bcrypt
from sqlalchemy.exc import IntegrityError
from database.db import SessionLocal
from models.user_model import User

class AuthService:

    @staticmethod
    def validate_email(email: str):
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(pattern, email)

    @staticmethod
    def validate_password(password: str):
        # Minimum 6 chars, at least one number
        pattern = r'^(?=.*\d).{6,}$'
        return re.match(pattern, password)

    @staticmethod
    def hash_password(password: str):
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    @staticmethod
    def verify_password(password: str, hashed: str):
        return bcrypt.checkpw(password.encode(), hashed.encode())

    @staticmethod
    def register_user(email: str, password: str):
        if not AuthService.validate_email(email):
            return False, "Invalid email format"

        if not AuthService.validate_password(password):
            return False, "Password must be at least 6 characters and contain a number"

        db = SessionLocal()
        hashed_pw = AuthService.hash_password(password)

        new_user = User(email=email, password=hashed_pw)

        try:
            db.add(new_user)
            db.commit()
            return True, "User registered successfully"
        except IntegrityError:
            db.rollback()
            return False, "Email already exists"
        finally:
            db.close()

    @staticmethod
    def login_user(email: str, password: str):
        db = SessionLocal()
        user = db.query(User).filter(User.email == email).first()
        db.close()

        if not user:
            return False, "User not found"

        if not AuthService.verify_password(password, user.password):
            return False, "Incorrect password"

        return True, user