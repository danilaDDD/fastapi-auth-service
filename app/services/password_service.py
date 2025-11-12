import hashlib


class PasswordService:

    def hashed(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        return self.hashed(plain_password) == hashed_password


def get_password_service() -> PasswordService:
    return PasswordService()
