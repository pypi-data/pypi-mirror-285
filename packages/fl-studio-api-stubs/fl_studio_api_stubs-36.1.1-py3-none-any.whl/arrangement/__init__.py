"""
# Arrangement

The `arrangement` module provides functions to allow for interaction with
FL Studio arrangements, including markers, selections and timestamps.

## Table of contents

* [Live](https://il-group.github.io/FL-Studio-API-Stubs/midi_controller_scripting/arrangement/live): live
  performance functions.

* [Markers](https://il-group.github.io/FL-Studio-API-Stubs/midi_controller_scripting/arrangement/markers):
  accessing information about markers on the playlist.

* [Selection](https://il-group.github.io/FL-Studio-API-Stubs/midi_controller_scripting/arrangement/selection):
  access information about the current selection on the playlist.

* [Time](https://il-group.github.io/FL-Studio-API-Stubs/midi_controller_scripting/arrangement/time):
  access information about the current time within the song.
"""
__all__ = [
    'liveSelection',
    'liveSelectionStart',
    'jumpToMarker',
    'getMarkerName',
    'addAutoTimeMarker',
    'selectionStart',
    'selectionEnd',
    'currentTime',
    'currentTimeHint',
]


from .__live import (
    liveSelection,
    liveSelectionStart,
)
from .__markers import (
    jumpToMarker,
    getMarkerName,
    addAutoTimeMarker,
)
from .__selection import (
    selectionStart,
    selectionEnd,
)
from .__time import (
    currentTime,
    currentTimeHint,
)
