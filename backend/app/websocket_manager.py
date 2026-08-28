"""
WebSocket connection manager.
"""
from typing import Dict, Set
from fastapi import WebSocket


class ConnectionManager:
    """Manage WebSocket connections per game."""

    def __init__(self):
        # game_id -> set of websockets
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, game_id: str):
        """Accept and register a new connection."""
        await websocket.accept()
        if game_id not in self.active_connections:
            self.active_connections[game_id] = set()
        self.active_connections[game_id].add(websocket)

    def disconnect(self, websocket: WebSocket, game_id: str):
        """Remove a connection."""
        if game_id in self.active_connections:
            self.active_connections[game_id].discard(websocket)
            if not self.active_connections[game_id]:
                del self.active_connections[game_id]

    async def broadcast(self, game_id: str, message: dict):
        """Broadcast message to all connections in a game."""
        if game_id in self.active_connections:
            dead_connections = set()
            for connection in self.active_connections[game_id]:
                try:
                    await connection.send_json(message)
                except:
                    dead_connections.add(connection)

            # Clean up dead connections
            for connection in dead_connections:
                self.active_connections[game_id].discard(connection)


# Global connection manager
manager = ConnectionManager()
