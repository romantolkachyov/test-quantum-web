import logging
from multiprocessing import Pool

from django.conf import settings

from quantum_web.worker.queues import JobQueue, log
from quantum_web.worker.worker import QuantumWorker


class QuantumListener:
    """Job listener.

    Listen to job queue and spawns subprocesses to handle received jobs.
    """
    def __init__(self):
        self.queue = JobQueue()

    def run(self) -> None:
        """Start worker.

        Listen to job queue and spawn new processes in the pool.
        """
        n_proc = settings.WORKER_MAX_CONCURRENCY
        logging.info("Starting QuantumListener with %i subprocesses", n_proc)
        with Pool(n_proc) as pool:
            while True:
                job = self.queue.get()
                log.info("Job received (job_id=%s)", job)
                pool.apply_async(self.handle_job, [job])

    @staticmethod
    def handle_job(job_id):
        """Handle job in a separate process.

        This method MUST BE static in order to prevent serialization issues.
        """
        p = QuantumWorker(job_id)
        p.run()
