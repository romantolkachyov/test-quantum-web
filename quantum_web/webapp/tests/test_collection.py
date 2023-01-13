import asyncio
from unittest import TestCase
from unittest.mock import MagicMock, patch

from ..listener.collection import Subscriber, SubscribersCollection


class SubscribersCollectionTest(TestCase):
    def setUp(self) -> None:
        self.collection = SubscribersCollection()

    def test_group_management(self):
        self.assertListEqual(self.collection.get_groups(), [])
        self.assertGroupCount(0)
        first_stream = '1234'
        first_queue = self.collection.add(first_stream)
        self.assertGroupCount(1)
        # stream with unique name should go to the first group
        self.collection.add('12345')
        self.assertGroupCount(1)
        # add duplicated stream, new group should be created
        second_queue = self.collection.add(first_stream)
        self.assertGroupCount(2)
        # remove first subscriber and make sure we have duplicated stream migrate to first group
        self.collection.remove('1234', first_queue)
        self.collection.optimize()
        self.assertGroupCount(1)
        self.assertEqual(self.collection.groups[0]['1234'].queue, second_queue)

    def test_group_management_no_subscribers(self):
        self.assertGroupCount(0)
        queue = self.collection.add('1234')
        self.assertGroupCount(1)
        self.collection.remove('1234', queue)
        self.collection.optimize()
        self.assertGroupCount(0)

    def test_group_management_remove_invalid(self):
        queue = asyncio.Queue()
        self.collection.remove('1234', queue)

    def test_group_management_remove_three_level(self):
        for x in range(4):
            self.collection.add('12345')
        self.collection.add('1234')
        queue = self.collection.add('1234')
        last_queue = self.collection.add('1234')
        self.collection.remove('1234', queue)
        self.collection.remove('1234', last_queue)

    @patch("quantum_web.webapp.listener.collection.asyncio.Queue.put")
    def test_subscribe_put(self, put_mock: MagicMock):
        sub = Subscriber()
        msg_id = b"1234"
        payload = {
            "test": "example"
        }
        asyncio.run(sub.put(msg_id, payload))
        put_mock.assert_called_with(payload)
        self.assertEqual(sub.last_message_id, msg_id.decode())

    def assertGroupCount(self, expected: int):
        self.assertEqual(expected, len(self.collection.groups))
