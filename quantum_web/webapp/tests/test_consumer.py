import asyncio
from datetime import datetime
from unittest.mock import Mock, patch

from channels.testing import WebsocketCommunicator
from django.test import TestCase

from quantum_web.asgi import application

FAKE_MESSAGES = [
    {"type": "start"},
    {"type": "solution", "energy": -1.23, "date": datetime.now().isoformat()},
    {"type": "stop"},
]


async def fake_get_messages(job_id):
    for msg in FAKE_MESSAGES:
        yield msg


async def sleep_get_messages(job_id):
    yield await asyncio.sleep(1)


class ConsumerTest(TestCase):
    @patch("quantum_web.webapp.consumers.listener.get_messages", new=fake_get_messages)
    @patch("quantum_web.webapp.consumers.listener.wait_job_stream")
    async def test_streaming_job(self, wait_mock: Mock):
        comm = WebsocketCommunicator(application, "/ws/process/1234/")
        await comm.connect()
        resp = await comm.receive_json_from()
        self.assertEqual(resp, FAKE_MESSAGES[0])

    @patch("quantum_web.webapp.consumers.listener.get_messages", new=fake_get_messages)
    @patch("quantum_web.webapp.consumers.listener.wait_job_stream")
    async def test_client_disconnect(self, wait_mock: Mock):
        comm = WebsocketCommunicator(application, "/ws/process/1234/")
        await comm.connect()
        await comm.disconnect()

    @patch("quantum_web.webapp.consumers.listener.get_messages", new=sleep_get_messages)
    @patch("quantum_web.webapp.consumers.listener.wait_job_stream")
    async def test_client_disconnect_on_sleep(self, wait_mock: Mock):
        comm = WebsocketCommunicator(application, "/ws/process/1234/")
        await comm.connect()
        await comm.disconnect()
