import asyncio
import logging
from dataclasses import dataclass, field

log = logging.getLogger(__name__)


@dataclass
class Subscriber:
    """Subscriber data class.
    """
    #: id of the last message received from the stream
    last_message_id: str = "0"
    #: subscriber queue
    queue: asyncio.Queue = field(default_factory=asyncio.Queue)

    async def put(self, msg_id, payload):
        """Send message to subscriber."""
        self.last_message_id = msg_id.decode()
        await self.queue.put(payload)


class SubscribersCollection:
    """Collection of stream subscribers.

    Manage subscribers such a way that we can spread all subscribes to multiple groups.
    Each group has only one subscription to a particular topic. If we add another listener
    for the same topic, collection will create another group.

    At the moment of listner removal, collection tries to optimize groups: if we remove listener
    from the first group then collection will check next group for subscribers to the same topic
    and move their listner to the first group. It allows to maintain the shortest group list.
    """
    groups: list[dict[str, Subscriber]]

    def __init__(self):
        self.groups = []

    def add(self, stream_name: str) -> asyncio.Queue:
        """Add new subscriber for the stream and return queue to consume messages.

        Looking for a first group without listeners on specified stream.
        """
        instance = Subscriber()
        for i, group in enumerate(self.groups):
            if stream_name not in group:
                log.debug("Add listener to the group %i", i)
                group[stream_name] = instance
                break
        else:
            log.debug("Create new group for new %s listener (%i groups occupied)",
                      stream_name, len(self.groups))
            self.groups.append({stream_name: instance})
        return instance.queue

    def remove(self, stream_name: str, queue: asyncio.Queue):
        """Remove subscriber from the collection.

        Search listener in all groups, remove and try to compress groups be moving same stream
        listeners to the found listener group. It allows to maintain the shortest group list
        possible.
        """
        log.debug("Removing listener from stream %s", stream_name)
        for i, group in enumerate(self.groups[:]):
            if stream_name in group and group[stream_name].queue == queue:
                log.debug("Removing listener from group %i", i)
                del group[stream_name]

                # build upper groups list
                upper_groups = []
                for other in reversed(self.groups):  # pragma: no branch
                    if other == group:
                        break
                    upper_groups.append(other)

                # try to find same stream listeners in an upper group and move it to the lowest
                # unoccupied group (starting from the lowest group)
                for other in upper_groups:
                    if stream_name in other:
                        log.debug("Found same stream listener in the upper group."
                                  " Moving to the actual group.")
                        group[stream_name] = other[stream_name]
                        del other[stream_name]
                        if not other:
                            self.groups.remove(other)
                        break
                else:
                    if not group:
                        log.debug("Group become empty, remove it.")
                        self.groups.remove(group)
                return
        log.error("Can't remove stream from the collection. Subscriber not found (stream: %s)",
                  stream_name)

    def get_groups(self):
        """Get listeners groups."""
        return self.groups

    def __len__(self):
        return sum([
            len(g) for g in self.groups
        ])
