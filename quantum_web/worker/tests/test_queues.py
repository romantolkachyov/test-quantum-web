from datetime import datetime
from unittest import TestCase
from unittest.mock import MagicMock, patch

from ..queues import EventType, JobQueue, ResultQueue


class ResultQueueTest(TestCase):
    def setUp(self) -> None:
        self.queue = ResultQueue('1234', prefix="example", ttl=60)
        self.stream_name = "example_1234"

    @patch("quantum_web.worker.queues.ResultQueue.put")
    def test_put_start(self, put_mock: MagicMock):
        self.queue.put_start()
        put_mock.assert_called_once_with(EventType.START)

    @patch("quantum_web.worker.queues.ResultQueue.put")
    def test_put_stop(self, put_mock: MagicMock):
        reason = "Example reason"
        self.queue.put_stop(reason)
        put_mock.assert_called_once_with(EventType.STOP, reason=reason)
        self.assertEqual(self.queue.stopped, True)

    @patch("quantum_web.worker.queues.ResultQueue.put")
    def test_put_solution(self, put_mock: MagicMock):
        energy = -1.23
        date = datetime.now()
        self.queue.put_solution(energy, date)
        put_mock.assert_called_once_with(EventType.SOLUTION, energy=energy, date=date.isoformat())

    @patch("quantum_web.worker.queues.ResultQueue.put")
    def test_put_solution_no_date(self, put_mock: MagicMock):
        energy = -1.2355
        self.queue.put_solution(energy)
        kw = put_mock.call_args.kwargs
        self.assertIn('date', kw)
        datetime.fromisoformat(kw['date'])

    @patch("quantum_web.worker.queues.redis.expire")
    def test_reset_expire(self, expire_mock: MagicMock):
        self.queue.reset_expire()
        expire_mock.assert_called_once()

    @patch("quantum_web.worker.queues.redis.xadd")
    @patch("quantum_web.worker.queues.ResultQueue.reset_expire")
    def test_raw_put(self, expire_mock: MagicMock, xadd_mock: MagicMock):
        energy = -2.3123
        self.queue.put(EventType.SOLUTION, energy=energy)
        xadd_mock.assert_called_once_with(self.stream_name, {
            "type": "solution",
            "energy": energy
        })

    @patch("quantum_web.worker.queues.redis.xadd")
    def test_raw_put_if_stopped(self, xadd_mock: MagicMock):
        self.queue.stopped = True
        with self.assertRaises(RuntimeError):
            self.queue.put(EventType.START)
        xadd_mock.assert_not_called()


class JobQueueTest(TestCase):
    def setUp(self) -> None:
        self.queue = JobQueue()

    @patch("quantum_web.worker.queues.redis.blpop", return_value=('any', '1234'))
    def test_get(self, blpop_mock: MagicMock):
        self.assertEqual(self.queue.get(), '1234')
        blpop_mock.assert_called_once()
