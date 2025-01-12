# app/routers/ws_results.py

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
from loguru import logger
import asyncio

router = APIRouter(prefix="/ws", tags=["WebSocket"])

# Store active WebSocket connections here
connected_clients: List[WebSocket] = []

@router.websocket("/results")
async def websocket_results(websocket: WebSocket):
    """
    WebSocket endpoint for sending new results in real-time to the client.
    """
    await websocket.accept()
    connected_clients.append(websocket)
    logger.info(f"Client connected: {websocket.client}")

    try:
        # In this example, we don't expect messages from the client;
        # but you can handle them in a loop if needed.
        while True:
            data = await websocket.receive_text()
            logger.debug(f"Received from client: {data}")
            # Optionally echo back or ignore.
            # await websocket.send_text(f"Echo: {data}")

    except WebSocketDisconnect:
        logger.warning(f"Client disconnected: {websocket.client}")
        connected_clients.remove(websocket)

async def broadcast_new_result(message: dict):
    """
    Broadcast `message` to all connected WebSocket clients as JSON.
    """
    disconnected_clients = []
    for client in connected_clients:
        try:
            await client.send_json(message)
        except Exception as e:
            logger.error(f"Error sending to client: {e}")
            disconnected_clients.append(client)

    # Remove clients that failed (i.e., disconnected)
    for client in disconnected_clients:
        if client in connected_clients:
            connected_clients.remove(client)
