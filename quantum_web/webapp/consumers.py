import asyncio
import logging

from channels.exceptions import StopConsumer
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django_async_redis.client import DefaultClient

from .listener.listener import StreamUnavailable, listener

log = logging.getLogger(__name__)


class SteamingRequestConsumer(AsyncJsonWebsocketConsumer):
    """Streaming request consumer.

    Consume client requests to stream job results.

    Create a single streaming task to stream data from redis.
    """

    #: streaming task
    task: asyncio.Task | None = None
    redis: DefaultClient | None = None
    stopped = False

    async def websocket_connect(self, event):
        """Handle websocket connection.

        Start streaming job on connection.
        """
        await super().websocket_connect(event)
        loop = asyncio.get_event_loop()
        self.task = loop.create_task(self.streaming_job())

    async def websocket_disconnect(self, event):
        """Handle websocket disconnection."""
        log.debug("Client disconnected, stopping consumer")
        if not self.task.done():
            self.task.cancel()
        raise StopConsumer()

    async def streaming_job(self):
        try:
            job_id = self.scope['url_route']['kwargs']['job_id']
            try:
                await listener.wait_job_stream(job_id)
            except StreamUnavailable:
                await self.send_json({
                    "type": "stop",
                    "reason": "Worker didn't start for too long. Please try later."
                })
            async for payload in listener.get_messages(job_id):
                log.debug("Streaming job received payload: %s", payload)
                await self.send_json(payload)
        except asyncio.CancelledError:
            log.debug("Stop consumer, streaming_job task cancelled")
            return
        await self.close()
