"""
# Ui

The `ui` module provides many functions used for interacting with many parts
of FL Studio's user interface.

* [Navigation](https://il-group.github.io/FL-Studio-API-Stubs/midi_controller_scripting/ui/navigation):
  perform generic navigation commands. These functions can be used for binding
  arrow buttons, jog wheels and touch scripts in MIDI Controllers.

* [Windows](https://il-group.github.io/FL-Studio-API-Stubs/midi_controller_scripting/ui/windows):
  interact with and control FL Studio's window management, including switching
  between windows, and determining which windows are visible/active.

* [Browser](https://il-group.github.io/FL-Studio-API-Stubs/midi_controller_scripting/ui/browser):
  interact with and control FL Studio's content browser window. This allows you
  to navigate and select items from the browser tree, as well as navigate
  between browser tabs.

* [State](https://il-group.github.io/FL-Studio-API-Stubs/midi_controller_scripting/ui/state):
  query the general state of FL Studio and its UI, including the hint panel,
  time panel, and other properties.

* [Keyboard](https://il-group.github.io/FL-Studio-API-Stubs/midi_controller_scripting/ui/keyboard):
  interact with FL Studio using keyboard shortcuts. This can be used to perform
  actions such as copy/paste.

* [Overlays](https://il-group.github.io/FL-Studio-API-Stubs/midi_controller_scripting/ui/overlays):
  create UI overlays to indicate the state of your script. These functions can
  show selected regions on the playlist, channel rack and mixer.

* [Editors](https://il-group.github.io/FL-Studio-API-Stubs/midi_controller_scripting/ui/editors):
  launch editor windows, such as Edison or the event editor.
"""
from .__navigation import (
    jog,
    jog2,
    strip,
    stripJog,
    stripHold,
    previous,
    next,
    moveJog,
    horZoom,
    verZoom,
    isInPopupMenu,
    closeActivePopupMenu,
)
from .__windows import (
    getVisible,
    showWindow,
    hideWindow,
    getFocused,
    setFocused,
    getFocusedFormCaption,
    getFocusedFormID,
    getFocusedPluginName,
    scrollWindow,
    nextWindow,
    selectWindow,
    closeAllMenu,
)
from .__browser import (
    navigateBrowser,
    navigateBrowserMenu,
    previewBrowserMenuItem,
    selectBrowserMenuItem,
    getFocusedNodeCaption,
    getFocusedNodeFileType,
    isBrowserAutoHide,
    setBrowserAutoHide,
    navigateBrowserTabs,
    toggleBrowserNode,
)
from .__state import (
    isClosing,
    isMetronomeEnabled,
    isStartOnInputEnabled,
    isPrecountEnabled,
    isLoopRecEnabled,
    getSnapMode,
    setSnapMode,
    snapMode,
    snapOnOff,
    getTimeDispMin,
    setTimeDispMin,
    getHintMsg,
    setHintMsg,
    showNotification,
    getHintValue,
    getProgTitle,
    getVersion,
    getStepEditMode,
    setStepEditMode,
)
from .__keyboard import (
    cut,
    copy,
    paste,
    insert,
    delete,
    enter,
    escape,
    yes,
    no,
    up,
    down,
    left,
    right,
)
from .__overlays import (
    crDisplayRect,
    miDisplayRect,
    miDisplayDockRect,
)
from .__editors import (
    launchAudioEditor,
    openEventEditor,
)

__all__ = [
    'navigateBrowser',
    'navigateBrowserMenu',
    'navigateBrowserTabs',
    'toggleBrowserNode',
    'previewBrowserMenuItem',
    'selectBrowserMenuItem',
    'getFocusedNodeCaption',
    'getFocusedNodeFileType',
    'isBrowserAutoHide',
    'setBrowserAutoHide',
    'launchAudioEditor',
    'openEventEditor',
    'isClosing',
    'isMetronomeEnabled',
    'isStartOnInputEnabled',
    'isPrecountEnabled',
    'isLoopRecEnabled',
    'getSnapMode',
    'setSnapMode',
    'snapMode',
    'snapOnOff',
    'getTimeDispMin',
    'setTimeDispMin',
    'getHintMsg',
    'setHintMsg',
    'showNotification',
    'getHintValue',
    'getProgTitle',
    'getVersion',
    'getStepEditMode',
    'setStepEditMode',
    'cut',
    'copy',
    'paste',
    'insert',
    'delete',
    'enter',
    'escape',
    'yes',
    'no',
    'up',
    'down',
    'left',
    'right',
    'jog',
    'jog2',
    'strip',
    'stripJog',
    'stripHold',
    'previous',
    'next',
    'moveJog',
    'horZoom',
    'verZoom',
    'isInPopupMenu',
    'closeActivePopupMenu',
    'crDisplayRect',
    'miDisplayRect',
    'miDisplayDockRect',
    'getVisible',
    'showWindow',
    'hideWindow',
    'getFocused',
    'setFocused',
    'getFocusedFormCaption',
    'getFocusedFormID',
    'getFocusedPluginName',
    'scrollWindow',
    'nextWindow',
    'selectWindow',
    'closeAllMenu',
]
