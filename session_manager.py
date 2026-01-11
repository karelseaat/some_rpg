from typing import List, Protocol, Any

class MessageSender(Protocol):
    async def send(self, message: str, game: Any = None) -> None:
        ...

class Session:
    def __init__(self, player_name: str, game: Any, sender: MessageSender):
        self.player_name = player_name
        self.game = game
        self.sender = sender

class SessionManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SessionManager, cls).__new__(cls)
            cls._instance.sessions: List[Session] = []
        return cls._instance

    def add_session(self, session: Session):
        self.sessions.append(session)

    def remove_session(self, session: Session):
        if session in self.sessions:
            self.sessions.remove(session)

    async def broadcast(self, message: str, exclude_player: str = None):
        for session in self.sessions:
            if session.player_name != exclude_player:
                await session.sender.send(message, game=session.game)

    async def broadcast_to_location(self, location_id: str, message: str, exclude_player: str = None):
        for session in self.sessions:
            if session.game.player.location_id == location_id and session.player_name != exclude_player:
                await session.sender.send(message, game=session.game)

    def get_session_by_name(self, player_name: str) -> Any:
        for session in self.sessions:
            if session.player_name.lower() == player_name.lower():
                return session
        return None

# Global instance
session_manager = SessionManager()
