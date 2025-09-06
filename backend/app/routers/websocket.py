from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict, List
import json
import logging
from datetime import datetime

from ..core.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        self.active_connections[session_id].append(websocket)
        logger.info(f"WebSocket connection established for session: {session_id}")

    def disconnect(self, websocket: WebSocket, session_id: str):
        if session_id in self.active_connections:
            self.active_connections[session_id].remove(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
        logger.info(f"WebSocket connection closed for session: {session_id}")

    async def send_progress_update(self, session_id: str, stage: str, progress: int, message: str):
        """Send progress update to all connections for a session"""
        if session_id in self.active_connections:
            update = {
                "type": "upload_progress",
                "data": {
                    "sessionId": session_id,
                    "stage": stage,
                    "progress": progress,
                    "message": message,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
            # Send to all connected clients for this session
            for connection in self.active_connections[session_id].copy():
                try:
                    await connection.send_text(json.dumps(update))
                except Exception as e:
                    logger.error(f"Error sending WebSocket message: {e}")
                    # Remove broken connection
                    self.active_connections[session_id].remove(connection)

    async def send_error(self, session_id: str, error_code: str, error_message: str):
        """Send error message to all connections for a session"""
        if session_id in self.active_connections:
            error_update = {
                "type": "upload_error",
                "data": {
                    "sessionId": session_id,
                    "error": {
                        "code": error_code,
                        "message": error_message
                    },
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
            for connection in self.active_connections[session_id].copy():
                try:
                    await connection.send_text(json.dumps(error_update))
                except Exception as e:
                    logger.error(f"Error sending WebSocket error: {e}")
                    self.active_connections[session_id].remove(connection)

# Global connection manager
manager = ConnectionManager()

@router.websocket("/ws/upload/{session_id}")
async def websocket_upload_progress(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for upload progress updates"""
    await manager.connect(websocket, session_id)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            logger.info(f"Received WebSocket message for session {session_id}: {data}")
            
            # Echo back a heartbeat
            await websocket.send_text(json.dumps({
                "type": "heartbeat",
                "timestamp": datetime.utcnow().isoformat()
            }))
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {e}")
        manager.disconnect(websocket, session_id)

# Export manager for use in upload router
def get_websocket_manager() -> ConnectionManager:
    return manager
