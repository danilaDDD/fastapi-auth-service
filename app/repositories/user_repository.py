from app.models.models import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    model = User

