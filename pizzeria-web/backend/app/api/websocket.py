"""
WebSocket endpoints for real-time updates.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List, Dict
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()

# Store active WebSocket connections
class ConnectionManager:
    """Manages WebSocket connections."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.admin_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket, is_admin: bool = False):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        if is_admin:
            self.admin_connections.append(websocket)
        logger.info(f"WebSocket connected. Total: {len(self.active_connections)}, Admin: {len(self.admin_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.admin_connections:
            self.admin_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}, Admin: {len(self.admin_connections)}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific connection."""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: dict, admin_only: bool = False):
        """Broadcast a message to all connections (or admin only)."""
        connections = self.admin_connections if admin_only else self.active_connections
        disconnected = []
        
        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for conn in disconnected:
            self.disconnect(conn)

# Global connection manager instance
manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Main WebSocket endpoint for real-time updates.
    """
    await manager.connect(websocket)
    try:
        while True:
            # Wait for messages from client
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                message_type = message.get("type")
                
                if message_type == "ping":
                    # Respond to ping with pong
                    await manager.send_personal_message({"type": "pong"}, websocket)
                elif message_type == "subscribe_admin":
                    # Client wants admin updates
                    if websocket not in manager.admin_connections:
                        manager.admin_connections.append(websocket)
                    await manager.send_personal_message({
                        "type": "subscribed",
                        "role": "admin"
                    }, websocket)
                elif message_type == "subscribe_order":
                    # Client wants updates for specific order
                    order_id = message.get("order_id")
                    await manager.send_personal_message({
                        "type": "subscribed",
                        "order_id": order_id
                    }, websocket)
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON received: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


async def broadcast_order_update_async(order_data: dict, event_type: str = "order_updated"):
    """
    Broadcast an order update to all connected clients (async version).
    
    Args:
        order_data: Order data to broadcast
        event_type: Type of event (order_created, order_updated, order_deleted)
    """
    message = {
        "type": event_type,
        "timestamp": datetime.now().isoformat(),
        "data": order_data
    }
    await manager.broadcast(message, admin_only=(event_type != "order_status_changed"))


def broadcast_order_update(order_data: dict, event_type: str = "order_updated"):
    """
    Broadcast an order update to all connected clients (sync wrapper).
    
    Args:
        order_data: Order data to broadcast
        event_type: Type of event (order_created, order_updated, order_deleted)
    """
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(broadcast_order_update_async(order_data, event_type))
        else:
            loop.run_until_complete(broadcast_order_update_async(order_data, event_type))
    except RuntimeError:
        # No event loop running, create a new one
        asyncio.run(broadcast_order_update_async(order_data, event_type))


def broadcast_new_order(order_data: dict):
    """Broadcast a new order to admin clients."""
    broadcast_order_update(order_data, "order_created")


def broadcast_status_change(order_data: dict):
    """Broadcast a status change to relevant clients."""
    broadcast_order_update(order_data, "order_status_changed")

