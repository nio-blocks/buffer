Buffer
=======

Collects all incoming signals and then emits them every **interval**.

If **interval_duration** is non-zero, then the signal emitted each **interval** will be all the signals over the last **interval_duration**, not just since the last emit.

If **timeout** is set *True* and no signals were input during an interval, a timeout signal will be output at the end of the interval. This signal will have a single attribute, *timeout*, that is set to *True*.

If **use_persistence** is *True*, then persistence is used to maintain the list of signals between stopping and starting the block.

Properties
--------------

-   **interval**: Time interval at which signals are emitted.
-   **interval_duration**: Each *interval* signals will emit going back this amount of time. If unspecifed or 0, then all input signals over the last **interval** will be emitted.
-   **timeout** (False): If *True* then a timeout signal will be emitted at the end of any interval with no signals.
-   **timeout_attr** ('timeout'): When a timeout signal is emitted, an attribute with the value will be set to True on the signal.
-   **use_persistence** (False): If *True*, use persistence to store the list of signals.

Dependencies
----------------
None

Commands
----------------
None

Input
-------
Any list of signals.

Output
---------
At the end of every **interval** all input signals over the last **interval_duration** will be emitted. If **interval_duration** is unspecified or 0, then all input signals over the last **interval** will be emitted.
