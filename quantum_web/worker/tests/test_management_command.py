from unittest import TestCase
from unittest.mock import MagicMock, patch

from ..management.commands.qworker import Command


class QworkerManagementCommandTest(TestCase):
    def setUp(self) -> None:
        self.command = Command()

    @patch("quantum_web.worker.management.commands.qworker.QuantumListener.run")
    def test_handle(self, run_mock: MagicMock):
        self.command.handle()
        run_mock.assert_called_once()
