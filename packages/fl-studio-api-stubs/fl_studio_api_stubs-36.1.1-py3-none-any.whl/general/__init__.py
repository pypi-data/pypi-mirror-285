"""
# General

The `general` module contains miscellaneous functions to handle general
interaction with FL Studio.

## Contents

* [FL State](https://il-group.github.io/FL-Studio-API-Stubs/midi_controller_scripting/general/fl state):
  access information about the general state of FL Studio.

* [Undo](https://il-group.github.io/FL-Studio-API-Stubs/midi_controller_scripting/general/undo):
  perform undo and redo actions.
"""
__all__ = [
    'saveUndo',
    'undo',
    'undoUp',
    'undoDown',
    'undoUpDown',
    'restoreUndo',
    'restoreUndoLevel',
    'getUndoLevelHint',
    'getUndoHistoryPos',
    'getUndoHistoryCount',
    'getUndoHistoryLast',
    'setUndoHistoryPos',
    'setUndoHistoryCount',
    'setUndoHistoryLast',
    'getRecPPB',
    'getRecPPQ',
    'getUseMetronome',
    'getPrecount',
    'getChangedFlag',
    'getVersion',
    'processRECEvent',
    'dumpScoreLog',
    'clearLog',
    'safeToEdit',
]


from .__undo import (
    saveUndo,
    undo,
    undoUp,
    undoDown,
    undoUpDown,
    restoreUndo,
    restoreUndoLevel,
    getUndoLevelHint,
    getUndoHistoryPos,
    getUndoHistoryCount,
    getUndoHistoryLast,
    setUndoHistoryPos,
    setUndoHistoryCount,
    setUndoHistoryLast,
)
from .__fl_state import (
    getRecPPB,
    getRecPPQ,
    getUseMetronome,
    getPrecount,
    getChangedFlag,
    getVersion,
    processRECEvent,
    dumpScoreLog,
    clearLog,
    safeToEdit,
)
