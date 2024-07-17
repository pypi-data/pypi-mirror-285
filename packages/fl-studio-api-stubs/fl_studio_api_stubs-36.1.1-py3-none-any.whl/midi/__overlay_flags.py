"""
Overlay flags are used by functions such as [ui.crDisplayRect()](https://il-group.github.io/FL-Studio-API-Stubs/midi_controller_scripting/ui/overlays#ui.__overlays.crDisplayRect)
to control options for displaying the overlay.

For example, to make FL Studio highlight channel names and mute buttons, and
scroll to the selected channels:

```py
import ui
import midi

ui.crDisplayRect(
    0, 1, 1, 3,
    2000,
    flags=midi.CR_HighlightChannelName
    | midi.CR_ScrollToView
    | midi.CR_HighlightChannelMute
)
```
"""

CR_HighlightChannels = 1
"""
When specified, [ui.crDisplayRect()](https://il-group.github.io/FL-Studio-API-Stubs/midi_controller_scripting/ui/overlays#ui.__overlays.crDisplayRect) highlights
channel buttons.
"""

CR_ScrollToView = 1 << 1
"""
When specified, [ui.crDisplayRect()](https://il-group.github.io/FL-Studio-API-Stubs/midi_controller_scripting/ui/overlays#ui.__overlays.crDisplayRect) scrolls so
that the given area is visible.
"""

CR_HighlightChannelMute = 1 << 2
"""
When specified, [ui.crDisplayRect()](https://il-group.github.io/FL-Studio-API-Stubs/midi_controller_scripting/ui/overlays#ui.__overlays.crDisplayRect) highlights
channel mute buttons.
"""

CR_HighlightChannelPanVol = 1 << 3
"""
When specified, [ui.crDisplayRect()](https://il-group.github.io/FL-Studio-API-Stubs/midi_controller_scripting/ui/overlays#ui.__overlays.crDisplayRect) highlights
channel pan and volume.
"""

CR_HighlightChannelTrack = 1 << 4
"""
When specified, [ui.crDisplayRect()](https://il-group.github.io/FL-Studio-API-Stubs/midi_controller_scripting/ui/overlays#ui.__overlays.crDisplayRect) highlights
target mixer track controls.
"""

CR_HighlightChannelName = 1 << 5
"""
When specified, [ui.crDisplayRect()](https://il-group.github.io/FL-Studio-API-Stubs/midi_controller_scripting/ui/overlays#ui.__overlays.crDisplayRect) highlights
channel names.
"""

CR_HighlightChannelSelect = 1 << 6
"""
When specified, [ui.crDisplayRect()](https://il-group.github.io/FL-Studio-API-Stubs/midi_controller_scripting/ui/overlays#ui.__overlays.crDisplayRect) highlights
channel selection buttons.
"""

MI_ScrollToView = 1 << 1
"""
When specified, [ui.miDisplayRect()](https://il-group.github.io/FL-Studio-API-Stubs/midi_controller_scripting/ui/overlays#ui.__overlays.miDisplayRect) scrolls so
that the given mixer tracks are visible.
"""
