Buffer
======
The Buffer block will collect all incoming signals and emit them every **interval**. If **interval_duration** is non-zero, then the signal emitted each **interval** will be all the signals collected over the last **interval_duration**.

Properties
----------
- **backup_interval**: An interval of time that specifies how often persisted data is saved.
- **group_by**: The signal attribute on the incoming signal whose values will be used to define groups on the outgoing signal.
- **interval**: Time interval at which signals are emitted.
- **interval_duration**: At each **interval**, emit signals collected during this amount of time. If unspecifed or 0, then all input signals collected during the last **interval** will be emitted.
- **load_from_persistence**: If `True`, the block’s state will be saved when the block is stopped and reloaded once the block is restarted.
- **signal_start**: If `True`, start the first interval when a signal is received.

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

