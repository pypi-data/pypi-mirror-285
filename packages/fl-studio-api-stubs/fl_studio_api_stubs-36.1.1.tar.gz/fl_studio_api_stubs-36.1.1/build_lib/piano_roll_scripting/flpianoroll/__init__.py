"""
# Flpianoroll

This module provides editing tools for interacting with notes and markers on
the FL Studio piano roll, using its piano roll scripting functionality.

Note that this module is not accessible in MIDI Controller Scripts, it can only
be used in scripts that run in FL Studio's piano roll.

## Table of contents

* [flpianoroll.ScriptDialog](https://il-group.github.io/FL-Studio-API-Stubs/piano_roll_scripting/enveditor#enveditor.ScriptDialog): create, show and get responses
  from dialog windows.
* [flpianoroll.score](https://il-group.github.io/FL-Studio-API-Stubs/piano_roll_scripting/flpianoroll/score#flpianoroll.__score.score): access and manipulate the piano roll
  contents.
* [flpianoroll.Note](https://il-group.github.io/FL-Studio-API-Stubs/piano_roll_scripting/flpianoroll/note#flpianoroll.__note.Note): a class to represent notes in the piano
  roll.
* [flpianoroll.Marker](https://il-group.github.io/FL-Studio-API-Stubs/piano_roll_scripting/flpianoroll/marker#flpianoroll.__marker.Marker): a class to represent markers in the
  piano roll.
* [flpianoroll.Utils](https://il-group.github.io/FL-Studio-API-Stubs/piano_roll_scripting/enveditor#enveditor.Utils): a collection of useful functions for
  interacting with the piano roll.
"""
from enveditor import ScriptDialog, Utils
from .__note import Note
from .__marker import Marker
from .__score import score


__all__ = [
    'score',
    'Note',
    'Marker',
    'ScriptDialog',
    'Utils',
]
