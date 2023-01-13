from unittest import TestCase
from unittest.mock import MagicMock, patch

from ..listener import QuantumListener


class NormalStopException(Exception):
    pass


class ListenerTest(TestCase):
    def setUp(self) -> None:
        self.listener = QuantumListener()

    @patch("quantum_web.worker.listener.QuantumWorker.run")
    def test_handle_job(self, worker_run_mock: MagicMock):
        job_id = "12345678"
        self.listener.handle_job(job_id)
        worker_run_mock.assert_called_once()

    @patch("multiprocessing.pool.Pool.apply_async",
           side_effect=NormalStopException())
    @patch("quantum_web.worker.listener.JobQueue.get",
           return_value='1234')
    def test_run(self, get_mock: MagicMock, apply_async_mock: MagicMock):
        try:
            self.listener.run()
        except NormalStopException:
            pass
        get_mock.assert_called_once()
        apply_async_mock.assert_called_once_with(self.listener.handle_job, ['1234'])
