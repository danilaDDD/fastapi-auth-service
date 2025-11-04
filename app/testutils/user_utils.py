from app.models.models import User


class UserGenerator:
    @classmethod
    def generate_user(cls, i: int) -> User:
        return User(
            login=f"user{i}",
            hashed_password=f"hashedpassword{i}",
            first_name=f"First{i}",
            last_name=f"Last{i}",
            second_name=f"Second{i}"
        )