from ..buffer_block import Buffer
from unittest.mock import MagicMock
from nio.testing.block_test_case import NIOBlockTestCase
from nio.signal.base import Signal
from threading import Event


class EventBuffer(Buffer):

    def __init__(self, event):
        super().__init__()
        self._event = event

    def emit(self, reset=False):
        super().emit(reset)
        self._event.set()
        self._event.clear()


class TestBuffer(NIOBlockTestCase):

    def test_buffer(self):
        event = Event()
        block = EventBuffer(event)
        block._backup = MagicMock()
        self.configure_block(block, {
            "interval": {
                "milliseconds": 200
            }
        })
        block.start()
        block.process_signals([Signal(), Signal(), Signal(), Signal()])
        self.assert_num_signals_notified(0, block)
        event.wait(.3)
        self.assert_num_signals_notified(4, block)
        block.stop()

    def test_interval_duration(self):
        event = Event()
        block = EventBuffer(event)
        block._backup = MagicMock()
        self.configure_block(block, {
            "interval": {
                "milliseconds": 1000
            },
            "interval_duration": {
                "milliseconds": 2000
            }
        })
        block.start()
        # process 4 signals (first group)
        block.process_signals([Signal(), Signal(), Signal(), Signal()])
        self.assert_num_signals_notified(0, block)
        event.wait(1.3)
        # first emit notifies first group
        self.assert_num_signals_notified(4, block)
        # process 2 more signals (second group)
        block.process_signals([Signal(), Signal()])
        event.wait(1.3)
        # second emit notifies first group and second group
        self.assert_num_signals_notified(10, block)
        # process 2 more signals (thrid group)
        block.process_signals([Signal(), Signal()])
        event.wait(1.3)
        # third emit notifies second group and third group
        self.assert_num_signals_notified(14, block)
        block.stop()

    def test_emit_command(self):
        block = Buffer()
        block.Job = MagicMock()
        self.configure_block(block, {
            "interval": {
                "milliseconds": 0
            },
            "interval_duration": {
                "milliseconds": 0
            }
        })
        block.start()
        self.assertFalse(block.Job.call_count)
        block.process_signals([Signal(), Signal()])
        block.emit()
        self.assert_num_signals_notified(2, block)
        block.stop()
