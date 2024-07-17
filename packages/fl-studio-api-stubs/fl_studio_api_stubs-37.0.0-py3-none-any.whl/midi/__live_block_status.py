"""
These constants are used with [playlist.getLiveStatus()](https://il-group.github.io/FL-Studio-API-Stubs/midi_controller_scripting/playlist/performance#playlist.__performance.getLiveStatus) and
[playlist.getLiveBlockStatus()](https://il-group.github.io/FL-Studio-API-Stubs/midi_controller_scripting/playlist/performance#playlist.__performance.getLiveBlockStatus) to represent the status of a track
in [performance mode](https://il-group.github.io/FL-Studio-API-Stubs/midi_controller_scripting/tutorials/performance_mode).
"""

LB_Status_Default = 0
"""
The default status.

* Return value: 1, Meaning: Filled
* Return value: 2, Meaning: Scheduled
* Return value: 4, Meaning: Playing
"""

LB_Status_Simple = 1
"""
Simpler status.

## For [playlist.getLiveStatus()](https://il-group.github.io/FL-Studio-API-Stubs/midi_controller_scripting/playlist/performance#playlist.__performance.getLiveStatus):

* Return value: 0, Meaning: Empty
* Return value: 1, Meaning: Filled
* Return value: 2, Meaning: None playing (or scheduled)
* Return value: 4, Meaning: None scheduled (and not playing)

## For [playlist.getLiveBlockStatus()](https://il-group.github.io/FL-Studio-API-Stubs/midi_controller_scripting/playlist/performance#playlist.__performance.getLiveBlockStatus):

* Return value: 0, Meaning: Empty
* Return value: 1, Meaning: Filled
* Return value: 2, Meaning: Playing (or scheduled)
* Return value: 4, Meaning: Scheduled (and not playing)
"""

LB_Status_Simplest = 2
"""
Simplest status.

This flag can only be used with [playlist.getLiveBlockStatus()](https://il-group.github.io/FL-Studio-API-Stubs/midi_controller_scripting/playlist/performance#playlist.__performance.getLiveBlockStatus).

* Return value: 0, Meaning: Empty
* Return value: 1, Meaning: Filled
* Return value: 2, Meaning: Playing or scheduled
"""
