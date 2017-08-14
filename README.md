Buffer
======

Collects all incoming signals and then emits them every **interval**.
If **interval_duration** is non-zero, then the signal emitted each **interval** will be all the signals over the last **interval_duration**, not just since the last emit.
If **use_persistence** is *True*, then persistence is used to maintain the list of signals between stopping and starting the block.

Properties
----------
- **backup_interval**: Interval to backup buffer to persistence
- **group_by**: Specify signal attribute to group incoming signals by
- **interval**: Time interval at which signals are emitted.
- **interval_duration**:  Each *interval* signals will emit going back this amount of time. If unspecifed or 0, then all input signals over the last **interval** will be emitted.
- **load_from_persistence**: If *True*, use persistence to store the list of signals.
- **signal_start**: start the interval when a signal is received

Inputs
------

Any list of signals.

Outputs
-------

At the end of every **interval** all input signals over the last **interval_duration** will be emitted. If **interval_duration** is unspecified or 0, then all input signals over the last **interval** will be emitted.

Commands
--------
- **emit**: Emit stored signals immediately
- **groups**: View information on current groups

Dependencies
------------
None
