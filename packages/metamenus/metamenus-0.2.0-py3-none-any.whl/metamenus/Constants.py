
from wx.lib.newevent import NewCommandEvent

# Events -----------------------------------------------------------------------

(MenuExBeforeEvent, EVT_BEFOREMENU) = NewCommandEvent()
(MenuExAfterEvent,  EVT_AFTERMENU)  = NewCommandEvent()

META_MENUS_LOGGING_NAME: str = 'metamenus'
# More info on 'history' and 'README.md' files.

# _sep is used internally only and is a substring that _cannot_
# appear on any of the regular menu labels.

_sep: str = " @@@ "

# noinspection SpellCheckingInspection
THE_GREAT_MAC_PLATFORM: str = '__WXMAC__'
