from db.session_manager import SessionManager


class BaseDBService:
    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager
