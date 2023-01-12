from typing import Callable

import numpy as np

from quantum_web.worker.queues import ResultQueue, log
from sdk_mock import qboard
from sdk_mock.qboard.constants import (  # TODO: interval, new_loss?
    CB_TYPE_INTERRUPT_TARGET, CB_TYPE_INTERRUPT_TIMEOUT, CB_TYPE_NEW_SOLUTION)


class QuantumWorker:
    """Worker process.

    A process running a particular job.

    Generate random sample and run solver.
    """
    def __init__(self, job_id: str):
        self.job_id = job_id
        self.result = ResultQueue(job_id)

    def run(self):
        """Handle computation job.

        The main class method.
        """
        log.info("Job started (job_id=%s)", self.job_id)
        self.result.put_start()

        try:
            solver = qboard.solver(mode="bf")
            solver.solve_qubo(
                self.generate_sample(),
                callback=self.solver_callback,
                timeout=30,
                verbosity=0
            )
        except Exception as e:  # noqa
            log.exception("Solver raised an unhandled exception.")
        finally:
            self.result.put_stop()
            log.info("Job stopped (job_id: %s).", self.job_id)

    def solver_callback(self, payload: dict):
        """Solver callback.

        Solver invoke this callback on some kind of events like new solution found or solver stopped.
        """
        cb_type = payload.get('cb_type')
        callback: Callable[[dict], None] = {
            CB_TYPE_NEW_SOLUTION: self.on_new_solution,
            CB_TYPE_INTERRUPT_TIMEOUT: self.on_interrupt_timeout,
            CB_TYPE_INTERRUPT_TARGET: self.on_interrupt_target,
        }.get(cb_type)
        if callback is not None:
            return callback(payload)
        log.error("Unhandled event type `%s`. Skip event. Payload: %s", cb_type, payload)

    def on_new_solution(self, payload):
        """Handle new solution from the solver."""
        energy = payload["energy"]
        spins = payload["spins"]
        log.debug("New solution found, energy %f, result vector %s", energy, spins)
        self.result.put_solution(energy)

    def on_interrupt_timeout(self, payload):
        """Handle interrupt event caused by specified solver timeout."""
        msg = f"Solver interrupted by timeout"
        log.info("%s (job_id=%s)", msg, self.job_id)
        self.result.put_stop(msg)

    def on_interrupt_target(self, payload):
        """Handle interruption event caused by reaching (?) the target.

        No target specified in the test assigment.
        """
        msg = "Solver interrupted by target"
        log.info("%s (job_id=%s)", msg, self.job_id)
        self.result.put_stop(msg)

    @staticmethod
    def generate_sample():
        """Generate random sample for solver."""
        return np.random.rand(30, 30) - 0.5
