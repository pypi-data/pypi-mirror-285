
from typing import Dict
from typing import List
from typing import NewType
from typing import Tuple
from typing import cast

from logging import Logger
from logging import getLogger

from wx import ID_ABOUT
from wx import ID_EXIT
from wx import ITEM_CHECK
from wx import ITEM_NORMAL
from wx import ITEM_RADIO

from wx import NewIdRef
from wx import GetTranslation
from wx import Platform
from wx import WindowIDRef

# TODO Can we avoid using these
# noinspection PyProtectedMember
from wx._core import ItemKind

from metamenus.Constants import THE_GREAT_MAC_PLATFORM
from metamenus.metamenus import _clean

from metamenus.types import CustomMethods

from metamenus.Constants import _sep
from metamenus.Constants import META_MENUS_LOGGING_NAME


SItems      = NewType('SItems', List["SItem"])
MethodNames = NewType('MethodNames', Dict[str, WindowIDRef])

SPECIAL_EXIT_MENU_TEXT:  str = 'Exit'
SPECIAL_QUIT_MENU_TEXT:  str = 'Quit'
SPECIAL_ABOUT_MENU_TEXT: str = 'About'


class SItem:
    """
    Internal use only. This provides a structure for parsing the 'trees'
    supplied in a sane way.
    """
    def __init__(self, params):

        self.logger: Logger = getLogger(META_MENUS_LOGGING_NAME)

        self._parent:   SItem  = cast(SItem, None)
        self._params:   Tuple  = self._adjust(params)
        self._children: SItems = SItems([])

        self._label:        str = ''
        self._labelText:    str = ''
        self._tLabel:       str = ''
        self._tLabelText:   str = ''
        self._accelerator:  str = ''

        self._methodName: str  = ''
        self._allMethods: MethodNames = MethodNames({})

        self._id: WindowIDRef = self._assignMenuId()
        self.Update()

    def _adjust(self, params):
        """
        This is responsible for formatting the args and kwargs for items
        supplied within the 'tree'.
        TODO:  Lots of chicanery going on here with the same variable changing
        types and formats
        """

        args = ()
        kwargs = {}
        params = params + [None] * (3 - len(params))

        if type(params[1]) is tuple:
            args = params[1]
        elif type(params[1]) in [str, int, ItemKind]:
            args = (params[1],)                         # type: ignore
        elif type(params[1]) is dict:
            kwargs = params[1]

        if type(params[2]) is tuple:
            args = params[2]
        elif type(params[2]) in [str, int, ItemKind]:
            args = (params[2],)                         # type: ignore
        elif type(params[2]) is dict:
            kwargs = params[2]

        args = list(args) + [""] * (2 - len(args))      # type: ignore

        # For those who believe wx.UPPERCASE_STUFF_IS_UGLY... 8^)
        kind_conv = {"radio":  ITEM_RADIO,
                     "check":  ITEM_CHECK,
                     "normal": ITEM_NORMAL}
        # ...well, these strings look more compact.

        if args[0] in list(kind_conv.keys()) + list(kind_conv.values()):    # type: ignore
            args = (args[1], args[0])                                       # type: ignore

        kind_conv.update({"normal": None, "": None})

        if type(args[1]) in [str]:                                          # type: ignore
            kind = kind_conv.get(args[1])                                   # type: ignore
            if kind is not None:
                args = (args[0], kind)                                      # type: ignore
            else:
                args = (args[0],)                                           # type: ignore

        return params[0], tuple(args), kwargs

    def Update(self):
        # noinspection SpellCheckingInspection
        """
        Members created/updated here:

        label:            "&New\tCtrl+N"
        labelText:        "&New"
        tLabel:           "&Novo\tCtrl+N"     (full label translated)
        tLabelText:       "&Novo"             (label text translated)
        accelerator:      "Ctrl+N"

        Not actually using all of them right now, but maybe later
        """
        preLabel: str = self._params[0]

        # if isinstance(preLabel, str):
        self._label     = preLabel.strip()
        self._labelText = self._label.split("\t")[0].strip()

        label, acc = (self._label.split("\t") + [''])[:2]

        self._tLabelText = GetTranslation(label.strip())
        self._accelerator = acc.strip()
        if self._accelerator is None or self._accelerator == '':
            self._tLabel = self._tLabelText
        else:
            # self._tLabel = "\t".join([self._tLabelText, self._accelerator])
            self._tLabel = f'{self._tLabelText}\t{self._accelerator}'

    def AddChild(self, item: 'SItem'):
        """
        Adds `item` to this SItem and updates the input item's parent attribute

        Args:
            item: The SItem to include as this SItem's child

        Returns:  The same item updated
        """
        item._parent = self
        self._children.append(item)
        return item

    def GetRealLabel(self, i18n):
        if i18n:
            label = self.GetLabelTranslation()
        else:
            label = self.GetLabel()
        return label

    def GetLabel(self) -> str:
        return self._label

    def GetLabelText(self):
        return self._labelText

    def GetLabelTranslation(self):
        return self._tLabel

    def GetLabelTextTranslation(self):
        return self._tLabelText

    def GetAccelerator(self) -> str:
        return self._accelerator

    def GetId(self) -> WindowIDRef:
        return self._id

    def GetParams(self):
        return self._params

    def GetParent(self):
        return self._parent

    def GetChildren(self, recursive=False) -> SItems:
        def _walk(Item, r):
            for child in Item.GetChildren():
                r.append(child)
                if child.HasChildren():
                    _walk(child, r)
            return r

        if not recursive:
            return self._children
        else:
            return _walk(self, [])

    def HasChildren(self) -> bool:
        return bool(self._children)

    def GetChildWithChildren(self):
        def _walk(Item, r):
            for child in Item.GetChildren():
                if child.HasChildren():
                    r.insert(0, child)
                    _walk(child, r)
            return r

        return _walk(self, [])

    def GetChildWithId(self, Id):
        r = None
        for child in self.GetChildren(True):
            if child.GetId() == Id:
                r = child
                break
        return r

    def GetPath(self):
        this = self
        path: str = this.GetLabelText()

        while this.GetParent() is not None:
            this = this.GetParent()
            # path = "%s %s %s" % (this.GetLabelText(), _sep, path)
            path = f'{this.GetLabelText()} {_sep} {path}'

        return path

    # noinspection SpellCheckingInspection
    def SetMethod(self, prefix: str, customMethods: CustomMethods):
        """

        Args:
            prefix:         The default prefix to use
            customMethods:  The potential custom methods for this SItem
        """

        menuName = _clean(self.GetPath())

        customMethodName:  str = cast(str, customMethods.get(menuName))  # The return is MenuName
        defaultMethodName: str = prefix + menuName

        # If a custom method was passed here, use it; otherwise we'll use a
        # default method name when this menu item is selected.
        if customMethodName is None:
            self._methodName = defaultMethodName
        else:
            self._methodName = customMethodName

        # We also store a reference to all method names that the public methods can address.
        self._allMethods = MethodNames(
            {
                customMethodName:  self.GetId(),
                defaultMethodName: self.GetId(),
                menuName:       self.GetId()
            }
        )
        self.logger.debug(f'{self._allMethods=}')

    def GetMethod(self) -> str:
        """
        TODO rename to GetMethodName
        Returns: The method name
        """
        return self._methodName

    def GetAllMethods(self) -> MethodNames:
        return self._allMethods

    def _assignMenuId(self) -> WindowIDRef:
        """
        Ideally, I would like to know that this SItem has a parent
        or not in order to use the special OS X identifiers

        Returns:
        """
        # parent: SItem = self._parent
        # if parent is not None:
        if Platform == THE_GREAT_MAC_PLATFORM:
            labelText = self._cleanup(self._labelText)
            self.logger.debug(f'{labelText}')
            if labelText == SPECIAL_ABOUT_MENU_TEXT:
                return ID_ABOUT
            if labelText == SPECIAL_EXIT_MENU_TEXT or labelText == SPECIAL_QUIT_MENU_TEXT:
                return ID_EXIT

        return NewIdRef()

    def _cleanup(self, menuLabel: str) -> str:

        menuLabel = menuLabel.replace('&', '')

        return menuLabel

    def __str__(self) -> str:
        return (
            f'SItem: `{self._labelText}` '
            f'`{self._id}` '
            f'path: `{self.GetPath()}` '
            f'parent={self._parent} '
        )
