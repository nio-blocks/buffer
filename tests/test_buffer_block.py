from ..buffer_block import Buffer
from unittest.mock import MagicMock, patch
from nio.testing.block_test_case import NIOBlockTestCase
from nio.signal.base import Signal
from threading import Event
from nio.block.terminals import DEFAULT_TERMINAL


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

    def test_buffer_groups(self):
        event = Event()
        block = EventBuffer(event)
        block._backup = MagicMock()
        self.configure_block(block, {
            "interval": {
                "milliseconds": 200
            },
            "group_by": "{{ $group }}",
        })
        block.start()
        block.process_signals([
            Signal({"iama": "signal", "group": "a"}),
            Signal({"iama": "signal", "group": "b"}),
            Signal({"iama": "signal", "group": "b"}),
        ])
        event.wait(.3)
        self.assert_num_signals_notified(3, block)
        self.assertTrue(
            {"iama": "signal", "group": "a"} in \
                [n.to_dict() for n in self.last_notified[DEFAULT_TERMINAL]]
        )
        self.assertEqual(
            len([n.to_dict() for n in self.last_notified[DEFAULT_TERMINAL] if \
                n.to_dict() == {"iama": "signal", "group": "b"}]),
            2
        )
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

    @patch(Buffer.__module__ + '.Job')
    def test_emit_command(self, patched_job):
        block = Buffer()
        self.configure_block(block, {})
        block.start()
        block.process_signals([Signal(), Signal()])
        block.emit()
        self.assert_num_signals_notified(2, block)
        block.stop()
        self.assertFalse(patched_job.call_count)

    @patch(Buffer.__module__ + '.Job')
    def test_emit_command_groups(self, patched_job):
        block = Buffer()
        self.configure_block(block, {"group_by": "{{ $group }}"})
        block.start()
        block.process_signals([
            Signal({"iama": "signal", "group": "a"}),
            Signal({"iama": "signal", "group": "b"}),
            Signal({"iama": "signal", "group": "b"}),
        ])
        block.emit(group="b")
        self.assert_num_signals_notified(2, block)
        block.emit(group="a")
        self.assert_num_signals_notified(3, block)
        block.process_signals([
            Signal({"iama": "signal", "group": "a"}),
            Signal({"iama": "signal", "group": "b"}),
            Signal({"iama": "signal", "group": "b"}),
        ])
        block.emit()
        self.assert_num_signals_notified(6, block)
        block.stop()
        self.assertFalse(patched_job.call_count)

    def test_buffer_start_signal(self):
        event = Event()
        block = EventBuffer(event)
        block._backup = MagicMock()
        self.configure_block(block, {
            "interval": {
                "milliseconds": 200
            },
            "signal_start": True
        })
        block.start()
        self.assert_num_signals_notified(0, block)
        event.wait(.1)
        block.process_signals([Signal()])
        event.wait(.1) # 200 miliseconds have now passed but the block should have only been active for 100
        block.process_signals([Signal()])
        event.wait(.1)
        self.assert_num_signals_notified(2, block) # This would be 1 if signal_start is False
        block.stop()
