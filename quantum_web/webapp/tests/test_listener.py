import asyncio
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock, patch

from ..listener.listener import JobResultListener, StreamUnavailable


class TestStopException(Exception):
    pass


class ListenerTest(IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.listener = JobResultListener(queue_prefix="test")

    def test_subscribe_unsubscribe(self):
        queue = self.listener.subscribe("1234")
        self.assertEqual(len(self.listener.collection), 1)
        self.listener.unsubscribe("1234", queue)
        self.assertEqual(len(self.listener.collection), 0)

    @patch("quantum_web.webapp.listener.listener.JobResultListener.listen_all")
    async def test_start(self, listen_all_mock: MagicMock):
        await self.listener.start()
        await self.listener.task
        listen_all_mock.assert_called_once()

    @patch("quantum_web.webapp.listener.listener.JobResultListener.listen_all")
    async def test_start_twice(self, listen_all_mock: MagicMock):
        await self.listener.start()
        with self.assertRaises(RuntimeError):
            await self.listener.start()
        await self.listener.ensure_started()
        await self.listener.task
        listen_all_mock.assert_called_once()

    @patch("quantum_web.webapp.listener.listener.JobResultListener.start")
    @patch("quantum_web.webapp.listener.listener.JobResultListener.subscribe")
    async def test_get_messages(self, subscribe_mock: MagicMock, start_mock: MagicMock):
        queue: asyncio.Queue = asyncio.Queue()
        await queue.put({"type": "solution"})
        await queue.put({"type": "stop"})
        subscribe_mock.return_value = queue
        result = []
        async for message in self.listener.get_messages("1234"):
            result.append(message)
        self.assertEqual(len(result), 2)
        start_mock.assert_called_once()
        subscribe_mock.assert_called_once_with("1234")

    async def test_wait_job_stream_unavailable(self):
        redis_mock = AsyncMock()
        redis_mock.exists = AsyncMock(return_value=False)
        with patch(
            "quantum_web.webapp.listener.listener.JobResultListener.get_redis",
            new=AsyncMock(return_value=redis_mock)
        ), self.assertRaises(StreamUnavailable):
            await self.listener.wait_job_stream("1234", max_tries=2, sleep_time=0)

    async def test_wait_job_stream(self):
        redis_mock = AsyncMock()
        redis_mock.exists = AsyncMock(return_value=True)
        with patch(
            "quantum_web.webapp.listener.listener.JobResultListener.get_redis",
            new=AsyncMock(return_value=redis_mock)
        ):
            await self.listener.wait_job_stream("1234", max_tries=2, sleep_time=0)

    @patch("quantum_web.webapp.listener.listener.asyncio.sleep", side_effect=TestStopException)
    async def test_listen_all(self, sleep_mock: MagicMock):
        redis_mock = AsyncMock()
        redis_mock.xread = AsyncMock(return_value=[
            (b'test_1234', [
                [
                    b'msg_id_0',
                    {b'type': b'stop'}
                ]
            ])
        ])
        queue = self.listener.subscribe("1234")
        with patch(
            "quantum_web.webapp.listener.listener.JobResultListener.get_redis",
            new=AsyncMock(return_value=redis_mock)
        ), self.assertRaises(TestStopException):
            await self.listener.listen_all()
        msg = queue.get_nowait()
        self.assertEqual(msg['type'], 'stop')
