"""
Undo flags are used to specify information about undo points added using
[general.saveUndo()](https://il-group.github.io/FL-Studio-API-Stubs/midi_controller_scripting/general/undo#general.__undo.saveUndo).

These flags can be combined using bitwise operations to make the undo point
apply to multiple parts of FL Studio.
"""

UF_None = 0
"""
???
"""

UF_EE = 1
"""
Event editor.
"""

UF_PR = 2
"""
Piano roll (includes modifications to patterns).
"""

UF_PL = 4
"""
Playlist (arrangement).
"""

UF_EEPR = UF_EE | UF_PR
"""
Event editor and piano roll.
"""

UF_Knob = 1 << 5
"""
Automated control.
"""

UF_SS = UF_PR
"""
Step sequencer?
"""

UF_AudioRec = 1 << 8
"""
Audio recording.
"""

UF_AutoClip = 1 << 9
"""
Automation clip.
"""

UF_PRMarker = 1 << 10
"""
Pattern (piano roll) marker.
"""

UF_PLMarker = 1 << 11
"""
Arrangement (playlist) marker.
"""

UF_Plugin = 1 << 12
"""
Plugin.
"""

UF_SSLooping = 1 << 13
"""
Step sequencer looping?
"""
