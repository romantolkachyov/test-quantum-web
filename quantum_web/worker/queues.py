import enum
import logging
from datetime import datetime

from django.conf import settings
from redis.client import Redis

log = logging.getLogger(__name__)
redis = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True
)


class EventType(enum.Enum):
    """Result queue event type enum."""
    #: worker got the job and start processing
    START = 'start'
    #: solution found
    SOLUTION = 'solution'
    #: worker stopped to run a job, must be the last message in the stream
    STOP = 'stop'


class ResultQueue:
    """Work process result queue.

    Abstraction and interface around redis stream with quantum process results.

    Streams will be removed after `ttl` seconds if no new messages published.
    """
    #: flag indicating queue received the last STOP message
    stopped = False

    def __init__(
        self,
        job_id: str,
        prefix: str = settings.RESULT_QUEUE_PREFIX,
        ttl: int = settings.RESULT_QUEUE_EXPIRE
    ):
        self.job_id = job_id
        self.ttl = ttl
        self.stream_name = f"{prefix}_{job_id}"

    def put_start(self):
        """Put START event to the stream."""
        self.put(EventType.START)

    def put_solution(self, energy: float, date: datetime | None = None):
        """Put SOLUTION event to the stream."""
        if date is None:
            date = datetime.now()
        self.put(EventType.SOLUTION, date=date.isoformat(), energy=energy)

    def put_stop(self, reason=""):
        """Put STOP event to the stream.

        Reason can be provided (will be printed out to the user).
        """
        self.put(EventType.STOP, reason=reason)
        self.stopped = True

    def reset_expire(self):
        """Update stream ttl and start countdown again."""
        log.debug("Reset %s stream ttl up to %i seconds", self.stream_name, self.ttl)
        redis.expire(self.stream_name, self.ttl)

    def put(self, event_type: EventType, **kwargs):
        """Put message to the stream (internal).

        Make sure we didn't send STOP message and reset stream ttl.
        """
        if self.stopped:
            raise RuntimeError("Trying to put message in the stream "
                               "while STOP message already sent.")
        log.debug("Send message with type %s (kwargs: %s) to the stream %s",
                  event_type, kwargs, self.stream_name)
        redis.xadd(self.stream_name, {
            "type": event_type.value,
            **kwargs
        })
        self.reset_expire()


class JobQueue:
    """Queue with jobs to process.

    Abstraction and an interface around redis.
    """
    def __init__(self, queue_name: str = settings.JOB_QUEUE):
        self.queue_name = queue_name

    def get(self):
        """Get next task id to process.

                Block until new tasks will be received.
                """
        _, job_id = redis.blpop(self.queue_name)
        job_id = job_id.decode()
        return job_id
