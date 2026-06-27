import logging

from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger("votebridge")


class ResultsConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time election results (Phase 5)."""

    async def connect(self):
        await self.accept()
        logger.info("WebSocket connected: results channel")

    async def disconnect(self, close_code):
        logger.info("WebSocket disconnected: results channel (code=%s)", close_code)

    async def receive(self, text_data=None, bytes_data=None):
        pass
