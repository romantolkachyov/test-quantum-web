import asyncio
import logging
from collections import defaultdict

from django.conf import settings
from django.core.cache import cache

from .collection import Subscriber, SubscribersCollection

log = logging.getLogger(__name__)


class StreamUnavailable(Exception):
    pass


class JobResultListener:
    """Job result listener.

    Listen for multiple streams and sink messages to subscribers.

    Use single Redis connection to do so instead of spawn connection and block for each listener.
    We should spawn connection and block indefinitely for XREAD instead (so we will have
    a number of active redis connection equal to the number of listeners, and we can reach
    connection number limit on the redis side).

    Groups allow to have multiple listeners with different offset for a single stream.
    """
    listeners: dict[str, Subscriber]
    started: bool = False
    queue_prefix: str
    task: asyncio.Task

    def __init__(self, queue_prefix: str = settings.RESULT_QUEUE_PREFIX):
        self.listeners = defaultdict(Subscriber)
        self.queue_prefix = queue_prefix
        self.collection = SubscribersCollection()

    def subscribe(self, job_id):
        """Subscribe for a job and get queue to consume messages."""
        log.debug("Subscribe to %s", job_id)
        return self.collection.add(self.get_stream_name(job_id))

    def unsubscribe(self, job_id: str, queue: asyncio.Queue):
        """Unsubscribe from the job."""
        log.debug("Unsubscribe job %s", job_id)
        stream_name = self.get_stream_name(job_id)
        self.collection.remove(stream_name, queue)

    async def start(self):
        """Start listener background job."""
        if self.started:
            raise RuntimeError("JobResultListener already started")
        self.started = True
        loop = asyncio.get_event_loop()
        self.task = loop.create_task(self.listen_all())

    async def ensure_started(self):
        """Ensure background job started."""
        if not self.started:
            await self.start()

    async def listen_all(self):
        """Listen all subscribed streams task.

        Iterate over collection groups indefinitely and make a short-blocking XREAD call
        for each group and sink received messages to subscriber.
        """
        redis = await self.get_redis()
        while True:
            for group in self.collection.get_groups()[:]:
                streams = {k: v.last_message_id for k, v in group.items()}
                log.debug("Reading data from streams: %s", streams)
                results = await redis.xread(streams, block=100)
                for stream_name, messages in results:
                    stream_name = stream_name.decode()
                    log.debug("Messages received in stream %s: %s", stream_name, messages)
                    for msg_id, payload in messages:
                        payload = {k.decode(): v.decode() for k, v in payload.items()}
                        log.debug("Publish %s to all subscribers. Payload: %s", msg_id, payload)
                        await group[stream_name].put(msg_id, payload)
            await asyncio.sleep(1)

    async def get_messages(self, job_id: str):
        """Get results from the job stream."""
        await self.ensure_started()
        queue = self.subscribe(job_id)
        log.debug("get_messages subscribed to %s stream", job_id)
        while True:
            msg = await queue.get()
            log.debug("get_messages receive message: %s", msg)
            yield msg
            queue.task_done()
            if msg.get('type') == 'stop':
                log.debug("get_messages receive stop message, unsubscribing")
                break
        self.unsubscribe(job_id, queue)

    async def wait_job_stream(self, job_id: str, max_tries: int = 60, sleep_time=1):
        """Block until job stream will be created by worker.

        Will try `max_tries` times and will sleep `sleep_time` between tries.

        Raise `StreamUnavailable` exception if stream still doesn't exist after no tries remain.
        """
        await self.ensure_started()
        redis = await self.get_redis()
        try_n = 0
        stream_name = self.get_stream_name(job_id)
        while try_n < max_tries:
            exists = await redis.exists(stream_name)
            if exists:
                log.debug("Stream %s exists.", stream_name)
                return True
            log.debug("Worker didn't created stream %s yet, sleep %i seconds",
                      stream_name, sleep_time)
            await asyncio.sleep(sleep_time)
            try_n += 1
        else:
            log.error("Worker didn't create stream %s for too long. Consider task failed.",
                      stream_name)
            raise StreamUnavailable()

    def get_stream_name(self, job_id):
        """Get stream name for job id."""
        return f"{self.queue_prefix}_{job_id}"

    @staticmethod
    def get_redis():
        """Get raw redis client."""
        return cache.client.get_client()


listener = JobResultListener()
