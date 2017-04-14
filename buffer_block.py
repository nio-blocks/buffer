from collections import defaultdict
from datetime import datetime
from threading import Lock
from time import time
from nio.block.base import Block
from nio.block.mixins.persistence.persistence import Persistence
from nio.properties.timedelta import TimeDeltaProperty
from nio.modules.scheduler import Job
from nio.signal.base import Signal
from nio.command import command


@command("emit")
class Buffer(Persistence, Block):

    interval = TimeDeltaProperty(title='Buffer Interval', allow_none=True)
    interval_duration = TimeDeltaProperty(title='Interval Duration',
                                          allow_none=True)

    def __init__(self):
        super().__init__()
        self._last_emission = None
        self._cache = defaultdict(list)
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
                reset=True
            )

    def emit(self):
        self._emit_job()

    def _emit_job(self, reset=False):
        self.logger.debug('Emitting signals')
        if reset:
            self._emission_job.cancel()
            self._emission_job = Job(
                self._emit_job,
                self.interval(),
                True
            )
        self._last_emission = datetime.utcnow()
        signals = self._get_emit_signals()
        if signals:
            self.logger.debug('Notifying {} signals'.format(len(signals)))
            self.notify_signals(signals)
        else:
            self.logger.debug('No signals to notify')

    def _get_emit_signals(self):
        with self._cache_lock:
            now = int(time())
            signals = []
            if self.interval_duration():
                # Remove old signals from cache.
                old = now - int(self.interval_duration().total_seconds())
                self.logger.debug(
                    'Removing signals from cache older than {}'.format(old))
                cache_times = sorted(self._cache.keys())
                for cache_time in cache_times:
                    if cache_time < old:
                        del self._cache[cache_time]
                    else:
                        break
            for cache in self._cache:
                signals.extend(self._cache[cache])
            if not self.interval_duration():
                # Clear cache every time if duration is not set.
                self.logger.debug('Clearing cache of signals')
                self._cache = defaultdict(list)
            return signals

    def process_signals(self, signals):
        with self._cache_lock:
            now = int(time())
            self._cache[now].extend(signals)
