import asyncio
import json

from channels.consumer import AsyncConsumer
from channels.exceptions import StopConsumer
from django.conf import settings
from django.core.cache import cache


class QuantumProcessConsumer(AsyncConsumer):
    def __init__(self):
        self.running_tasks = []
        super().__init__()

    async def handle_process(self):
        try:
            raw_redis = await cache.client.get_client()
            job_id = self.scope['url_route']['kwargs']['process_id']
            print("Handling job %s" % job_id)
            stream_name = f"{settings.RESULT_QUEUE_PREFIX}_{job_id}"

            try_n = 0
            while try_n < 30:
                exists = await raw_redis.exists(stream_name)
                if exists:
                    break
                print("Worker didn't created stream %s yet" % stream_name)
                await asyncio.sleep(1)
                try_n += 1
            else:
                print("Worker didn't up, will not try check stream %s existance anymore." % stream_name)
                return
            last_msg_id = 0
            finished = False
            while not finished:
                res = await raw_redis.xread({
                    stream_name: last_msg_id
                })
                for stream, items in res:
                    for msg_id, payload in items:
                        print(payload)
                        last_msg_id = msg_id
                        if payload[b'type'] == b"solution":
                            await self.send({
                                "type": "websocket.send",
                                "text": json.dumps({
                                    "type": "solution",
                                    "date": payload[b'date'].decode(),
                                    "energy": payload[b'energy'].decode(),
                                })
                            })
                        elif payload[b'type'] == b"start":
                            await self.send({
                                "type": "websocket.send",
                                "text": json.dumps({
                                    "type": "start",
                                })
                            })
                        elif payload[b'type'] == b'stop':
                            print("Stop event received")
                            await self.send({
                                "type": "websocket.send",
                                "text": json.dumps({
                                    "type": "stop",
                                })
                            })
                            finished = True
            await self.send({
                "type": "websocket.close"
            })
        except asyncio.CancelledError:
            print("Stop consumer, handler task cancelled")

    async def websocket_connect(self, event):
        await self.send({
            "type": "websocket.accept",
        })
        loop = asyncio.get_event_loop()
        self.running_tasks.append(loop.create_task(self.handle_process()))

    async def websocket_disconnect(self, event):
        print("Waiting %i tasks to complete %i", len(self.running_tasks))
        for task in self.running_tasks:
            task.cancel()
        await asyncio.gather(*self.running_tasks)
        print("Tasks completed")
        raise StopConsumer()

    async def websocket_receive(self, event):
        await self.send({
            "type": "websocket.send",
            "text": event["text"],
        })
