from collections import defaultdict
from datetime import datetime
from time import time
from nio.common.block.base import Block
from nio.common.discovery import Discoverable, DiscoverableType
from nio.metadata.properties.bool import BoolProperty
from nio.metadata.properties.timedelta import TimeDeltaProperty
from nio.metadata.properties.string import StringProperty
from nio.modules.scheduler import Job
from nio.modules.threading import Lock
from nio.common.signal.base import Signal


@Discoverable(DiscoverableType.block)
class Buffer(Block):

    interval = TimeDeltaProperty(title='Buffer Interval')
    interval_duration = TimeDeltaProperty(title='Interval Duration')
    timeout = BoolProperty(title='Buffer Timeout', default=False)
    timeout_attr = StringProperty(title='Timeout Attributes', visible=False, default="timeout")
    use_persistence = BoolProperty(title='Use Persistence?', visible=False, default=False)

    def __init__(self):
        super().__init__()
        self._last_emission = None
        self._cache = defaultdict(list)
        self._cache_lock = Lock()
        self._emission_job = None

    def configure(self, context):
        super().configure(context)
        if self.use_persistence:
            self._last_emission = self.persistence.load('last_emission')
            self._cache = self.persistence.load('cache') or defaultdict(list)
            # For backwards compatability, make sure cache is dict.
            if not isinstance(self._cache, dict):
                self._cache = defaultdict(list)

    def start(self):
        now = datetime.utcnow()
        latest = self._last_emission or now
        delta = self.interval - (now - latest)
        self._emission_job = Job(
            self.emit,
            delta,
            False,
            reset=True
        )

    def stop(self):
        if self.use_persistence:
            self._backup()

    def emit(self, reset=False):
        self._logger.debug('Emitting signals')
        if reset:
            self._emission_job.cancel()
            self._emission_job = Job(
                self.emit,
                self.interval,
                True
            )
        self._last_emission = datetime.utcnow()
        signals = self._get_emit_signals()
        if signals:
            self._logger.debug('Notifying {} signals'.format(len(signals)))
            self.notify_signals(signals)
        elif self.timeout:
            self._logger.debug('Notifying timeout signal')
            self.notify_signals([Signal({self.timeout_attr: True})])
        else:
            self._logger.debug('No signals to notify')
        if self.use_persistence:
            self.persistence.store('last_emission', self._last_emission)
            self._backup()

    def _get_emit_signals(self):
        with self._cache_lock:
            now = int(time())
            signals = []
            if self.interval_duration:
                # Remove old signals from cache.
                old = now - int(self.interval_duration.total_seconds())
                self._logger.debug(
                    'Removing signals from cache older than {}'.format(old))
                cache_times = sorted(self._cache.keys())
                for cache_time in cache_times:
                    if cache_time < old:
                        del self._cache[cache_time]
                    else:
                        break
            for cache in self._cache:
                signals.extend(self._cache[cache])
            if not self.interval_duration:
                # Clear cache every time if duration is not set.
                self._logger.debug('Clearing cache of signals')
                self._cache = defaultdict(list)
            return signals

    def process_signals(self, signals):
        with self._cache_lock:
            now = int(time())
            self._cache[now].extend(signals)

    def _backup(self):
        self.persistence.store('cache', self._cache)
        self.persistence.save()
