from collections import defaultdict
from datetime import datetime
from threading import Lock
from time import time
from nio.block.base import Block
from nio.block.mixins.persistence.persistence import Persistence
from nio.block.mixins.group_by.group_by import GroupBy
from nio.properties.timedelta import TimeDeltaProperty
from nio.modules.scheduler import Job
from nio.signal.base import Signal
from nio.command import command
from nio.command.params.string import StringParameter


@command("emit", StringParameter("group", default=None, allow_none=True))
class Buffer(Persistence, GroupBy, Block):

    interval = TimeDeltaProperty(title='Buffer Interval', allow_none=True)
    interval_duration = TimeDeltaProperty(title='Interval Duration',
                                          allow_none=True)

    def __init__(self):
        super().__init__()
        self._last_emission = None
        self._cache = defaultdict(lambda: defaultdict(list))
        self._cache_lock = Lock()
        self._emission_job = None

    def persisted_values(self):
        return ['_last_emission', '_cache']

    def start(self):
        if self.interval():
            now = datetime.utcnow()
            latest = self._last_emission or now
            delta = self.interval() - (now - latest)
            self._emission_job = Job(
                self._emit_job,
                delta,
                False,
                group=None,
                reset=True,
            )

    def emit(self, group=None):
        self._emit_job(group)

    def _emit_job(self, group, reset=False):
        self.logger.debug('Emitting signals')
        if reset:
            self._emission_job.cancel()
            self._emission_job = Job(
                self._emit_job,
                self.interval(),
                True,
                group=group,
            )
        self._last_emission = datetime.utcnow()
        signals = self._get_emit_signals(group)
        if signals:
            self.logger.debug('Notifying {} signals'.format(len(signals)))
            self.notify_signals(signals)
        else:
            self.logger.debug('No signals to notify')

    def _get_emit_signals(self, group=None):
        signals = []
        with self._cache_lock:
            if not group:
                for group in self._cache.keys():
                    signals.extend(self._get_emit_signals_for_group(group))
            else:
                signals.extend(self._get_emit_signals_for_group(group))
        return signals

    def _get_emit_signals_for_group(self, group):
        now = int(time())
        signals = []
        cache_times = sorted(self._cache[group].keys())
        if self.interval_duration():
            # Remove old signals from cache.
            old = now - int(self.interval_duration().total_seconds())
            self.logger.debug(
                'Removing signals from cache older than {}'.format(old))
            for cache_time in cache_times:
                if cache_time < old:
                    del self._cache[group][cache_time]
                else:
                    break
        for cache in sorted(cache_times):
            signals.extend(self._cache[group][cache])
        if not self.interval_duration():
            # Clear cache every time if duration is not set.
            self.logger.debug('Clearing cache of signals')
            self._cache[group] = defaultdict(list)
        return signals

    def process_signals(self, signals):
        self.for_each_group(self.process_group, signals)

    def process_group(self, signals, key):
        with self._cache_lock:
            now = int(time())
            self._cache[key][now].extend(signals)
