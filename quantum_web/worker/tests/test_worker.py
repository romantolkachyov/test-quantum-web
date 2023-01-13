from unittest import TestCase
from unittest.mock import MagicMock, patch

from sdk_mock.qboard.constants import CB_TYPE_NEW_SOLUTION

from ..worker import QuantumWorker


class TestException(Exception):
    pass


class WorkerTest(TestCase):
    job_id = '1234'

    def setUp(self) -> None:
        self.worker = QuantumWorker(self.job_id)

    @patch("qboard.solver.solver.solve_qubo")
    @patch("quantum_web.worker.worker.ResultQueue.put_start")
    @patch("quantum_web.worker.worker.ResultQueue.put_stop")
    def test_run(
        self,
        solve_mock: MagicMock,
        put_stop_mock: MagicMock,
        put_start_mock: MagicMock
    ):
        self.worker.run()
        put_start_mock.assert_called_once()
        solve_mock.assert_called_once()
        put_stop_mock.assert_called_once()

    @patch("qboard.solver.solver.solve_qubo", side_effect=TestException())
    @patch("quantum_web.worker.worker.ResultQueue.put_start")
    @patch("quantum_web.worker.worker.ResultQueue.put_stop")
    def test_run_exception(
        self,
        solve_mock: MagicMock,
        put_stop_mock: MagicMock,
        put_start_mock: MagicMock
    ):
        self.worker.run()
        put_start_mock.assert_called_once()
        solve_mock.assert_called_once()
        put_stop_mock.assert_called_once()

    @patch("quantum_web.worker.worker.ResultQueue.put_solution")
    def test_solver_callback(self, put_solution_mock):
        self.worker.solver_callback({
            "cb_type": CB_TYPE_NEW_SOLUTION,
            "energy": -12.323
        })

    def test_solver_callback_no_cb_type(self):
        with self.assertRaises(RuntimeError):
            self.worker.solver_callback({})

    def test_solver_callback_invalid_type(self):
        self.worker.solver_callback({"cb_type": 999})

    @patch("quantum_web.worker.worker.ResultQueue.put_solution")
    def test_on_new_solution(self, put_solution_mock: MagicMock):
        energy = -2.32
        self.worker.on_new_solution({"energy": energy})
        put_solution_mock.assert_called_once_with(energy)

    @patch("quantum_web.worker.worker.ResultQueue.put_solution")
    def test_on_new_solution_without_energy(self, put_solution_mock: MagicMock):
        self.worker.on_new_solution({})
        put_solution_mock.assert_not_called()

    @patch("quantum_web.worker.worker.ResultQueue.put_stop")
    def test_on_interrupt_timeout(self, put_stop_mock: MagicMock):
        self.worker.on_interrupt_timeout({})
        put_stop_mock.assert_called_once_with("Solver interrupted by timeout")

    @patch("quantum_web.worker.worker.ResultQueue.put_stop")
    def test_on_interrupt_target(self, put_stop_mock: MagicMock):
        self.worker.on_interrupt_target({})
        put_stop_mock.assert_called_once_with("Solver interrupted by target")
