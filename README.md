Buffer
======
The Buffer block will collect all incoming signals and emit them every **interval**. If **interval_duration** is non-zero, then the signal emitted each **interval** will be all the signals collected over the last **interval_duration**, not just since the last emit.

Properties
----------
- **backup_interval**: How often to save persisted data.
- **group_by**: Signal attribute to define groupings of incoming signals.
- **interval**: Time interval at which signals are emitted.
- **interval_duration**: Each *interval* signals will emit going back this amount of time. If unspecifed or 0, then all input signals over the last **interval** will be emitted.
- **load_from_persistence**: If *True*, the block's state will be saved at a block stoppage and reloaded upon restart.
- **signal_start**: Start the interval when a signal is received.

Inputs
------
- **default**: Any list of signals.

Outputs
-------
- **default**: Signals stored since the time specified by the **interval_duration**.

Commands
--------
- **emit**: Emit stored signals immediately.
- **groups**: View information on current groups.

Dependencies
------------
None

