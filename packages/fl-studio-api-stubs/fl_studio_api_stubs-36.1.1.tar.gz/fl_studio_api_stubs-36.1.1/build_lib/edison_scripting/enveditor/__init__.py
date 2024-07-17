"""
# Enveditor

This module provides editing tools for interacting with audio clips in the
Edison editor, using its integrated scripts functionality.

Main script files should use the `.pyscript` file extension, with additional
modules using standard `.py` files.

Note that this module is not accessible in MIDI Controller Scripts, it can only
be used in scripts that run in Edison's editor.

## Table of contents

* [enveditor.ScriptDialog](https://il-group.github.io/FL-Studio-API-Stubs/edison_scripting/enveditor/script_dialog#enveditor.__script_dialog.ScriptDialog): create, show and get responses
  from dialog windows.
* [enveditor.Sample](https://il-group.github.io/FL-Studio-API-Stubs/edison_scripting/enveditor/sample#enveditor.__sample.Sample): interact with audio samples.
* [enveditor.EditorSample](https://il-group.github.io/FL-Studio-API-Stubs/edison_scripting/enveditor/sample#enveditor.__sample.EditorSample): the sample loaded into Edison
* [enveditor.Region](https://il-group.github.io/FL-Studio-API-Stubs/edison_scripting/enveditor/sample#enveditor.__sample.Region): a region of a sample.
* [enveditor.Editor](https://il-group.github.io/FL-Studio-API-Stubs/edison_scripting/enveditor/sample#enveditor.__sample.Editor): an object representing the state of
  the Edison editor.
* [enveditor.Utils](https://il-group.github.io/FL-Studio-API-Stubs/edison_scripting/enveditor/utils#enveditor.__utils.Utils): a collection of useful functions for
  interacting with audio.
"""
__all__ = [
    'ScriptDialog',
    'Region',
    'Sample',
    'EditorSample',
    'MEEditor',
    'Editor',
    'TUtils',
    'Utils',
]

from .__script_dialog import ScriptDialog
from .__sample import Region, Sample, EditorSample, MEEditor, Editor
from .__utils import TUtils, Utils
