
from logging import Logger
from logging import getLogger

from wx import EVT_MENU
from wx import ITEM_CHECK
from wx import ITEM_RADIO

from wx import Menu

from wx import GetTranslation
from wx import PostEvent
# noinspection PyUnresolvedReferences
from wx.core import DEFAULT

# TODO Can avoid using these
# noinspection PyProtectedMember
from wx._core import wxAssertionError

from metamenus.BaseMenuEx import BaseMenuEx
from metamenus.Constants import META_MENUS_LOGGING_NAME
from metamenus.Constants import MenuExAfterEvent
from metamenus.Constants import MenuExBeforeEvent
from metamenus.SItem import SItem


class MenuEx(Menu, BaseMenuEx):
    """
    """

    # noinspection PyUnusedLocal
    def __init__(self, *args, **kwargs):
        # noinspection SpellCheckingInspection
        """
        MenuEx(parent, menu, margin=wx.DEFAULT, font=wx.NullFont, show_title=True,
        customMethods: customMethods=CustomMethods({}), i18n=True, style=0)
        """
        BaseMenuEx.__init__(self, *args, **kwargs)

        self.logger: Logger = getLogger(META_MENUS_LOGGING_NAME)

        strippedKWArgs = self._extractKeyWordValues(**kwargs)
        Menu.__init__(self, **strippedKWArgs)

        self._title = self._menus[0][0]
        if self._show_title:
            if self._i18n:
                self.SetTitle(GetTranslation(self._title))
            else:
                self.SetTitle(self._title)

        # 'fix' for https://github.com/wxWidgets/Phoenix/issues/1648
        self.x = []

        # Parse the menu 'tree' supplied.
        top = BaseMenuEx.evolve(self._menus)

        # Create these menus first...
        wxMenus = {top: self}
        for k in top.GetChildWithChildren():
            wxMenus[k] = Menu()

            # ...and append their respective children.
            for h in k.GetChildren():
                wxMenus = self._makeMenus(wxMenus, h, k, self._margin, self._font, self._i18n)

        # Now append these items to the top level menu.
        for h in top.GetChildren():
            wxMenus = self._makeMenus(wxMenus, h, top, self._margin, self._font, self._i18n)

        # Now find out what are the methods that should be called upon
        # menu items selection.
        self.MenuIds     = {}
        self.MenuStrings = {}       # type: ignore
        self.MenuList    = []
        for child in top.GetChildren(True):
            Id = child.GetId()
            item = self.FindItemById(Id)
            if item:
                child.SetMethod(self._configuration.menuPrefix, self._customMethods)
                self.MenuIds[Id] = child
                self.MenuStrings.update(child.GetAllMethods())
                self.MenuList.append([Id, child.GetPath()])

            # 'fix' for https://github.com/wxWidgets/Phoenix/issues/1648
            self.x.append(wxMenus)

        # Initialize menu states.
        self.MenuState = {}
        for Id in self.MenuIds.keys():
            if self.FindItemById(Id).IsCheckable():
                is_checked = self.IsChecked(Id)
            else:
                is_checked = False
            self.MenuState[Id] = is_checked

        # Nice class. 8^) Will take care of this automatically.
        #
        # TODO: Used to work before Phoenix on TaskBarIcons,
        # now it seems we have to bind there instead... 8^(
        self._parent.Bind(EVT_MENU, self.OnM_)

    def _update(self, i):
        def _resetRadioGroup(idx):
            g = []
            n = []

            for Id, s in self.MenuList:
                item = self.FindItemById(Id)
                if item.GetKind() == ITEM_RADIO:
                    g.append(Id)
                else:
                    g.append(None)

            for x in range(g.index(idx), 0, -1):
                # if g[x] != None:
                if g[x] is not None:
                    n.append(g[x])
                else:
                    break

            for x in range(g.index(idx) + 1, len(g)):
                # if g[x] != None:
                if g[x] is not None:
                    n.append(g[x])
                else:
                    break

            for idx in n:
                self.MenuState[idx] = False

        kind = self.FindItemById(i).GetKind()

        if kind == ITEM_CHECK:
            self.MenuState[i] = not self.IsChecked(i)

        elif kind == ITEM_RADIO:
            _resetRadioGroup(i)
            self.MenuState[i] = True

    def OnM_(self, evt):
        """
        Called on all menu events for this menu. It will in turn call
        the related method on parent, if any.
        """
        try:
            attr = self.MenuIds[evt.GetId()]

            self.OnM_before()

            if isinstance(attr, SItem):
                attr_name = attr.GetMethod()

                if callable(attr_name):
                    # noinspection PyCallingNonCallable
                    attr_name()
                elif hasattr(self._parent, attr_name) and callable(getattr(self._parent, attr_name)):
                    getattr(self._parent, attr_name)()
                else:
                    if self._configuration.verboseWarnings is True:
                        self.logger.warning(f"{attr_name} not found in parent.")

            # TODO fix this
            # noinspection PyUnboundLocalVariable
            self.OnM_after(attr_name)

        except KeyError:
            # Maybe another menu was triggered elsewhere in parent,
            # maybe I screwed something up somewhere...
            pass

        evt.Skip()

    def OnM_before(self):
        # noinspection SpellCheckingInspection
        """
        If you need to execute something right before a menu event is
        triggered, you can bind the EVT_BEFOREMENU.
        """

        evt = MenuExBeforeEvent(-1, obj=self)
        PostEvent(self, evt)

    def OnM_after(self, attr_name=None):
        # noinspection SpellCheckingInspection
        """
        If you need to execute something right after a menu event is
        triggered, you can bind the EVT_AFTERMENU.
        """

        evt = MenuExAfterEvent(-1, obj=self, item=attr_name)
        PostEvent(self, evt)

    # def UpdateMenus(self):
    #     """
    #     Call this to update menu labels whenever the current locale
    #     changes.
    #
    #     This method never seems to be called from the demo programs.  Which
    #     is probably why `MenuIds` un-resolved does not matter;
    #     """
    #
    #     if not self._i18n:
    #         return
    #
    #     # noinspection PyUnresolvedReferences
    #     for k, v in MenuIds.items():
    #         item = self.FindItemById(k)
    #         if item is not None:   # Skip separators
    #             v.Update()
    #             self.SetLabel(k, v.GetRealLabel(self._i18n))

    def Popup(self, evt):
        """Pops this menu up."""

        [self.Check(i, v) for i, v in self.MenuState.items()
         if self.FindItemById(i).IsCheckable()]

        obj = evt.GetEventObject()
        pos = evt.GetPosition()
        obj.PopupMenu(self, pos)

    def GetItemState(self, menu_string):
        """Returns True if a checkable menu item is checked."""

        this = self.MenuStrings[menu_string]
        try:
            r = self.IsChecked(this)
        except wxAssertionError:
            r = False
        return r

    def SetItemState(self, menu_string, check):
        """Toggles a checkable menu item checked or unchecked."""

        this = self.MenuStrings[menu_string]
        self.MenuState[this] = check

    def EnableItem(self, menu_string, enable=True):
        """Enables or disables a menu item via its label."""

        this = self.MenuStrings[menu_string]
        self.Enable(this, enable)

    def EnableItems(self, menu_string_list, enable=True):
        """Enables or disables menu items via a list of labels."""

        for menu_string in menu_string_list:
            self.EnableItem(menu_string, enable)

    def EnableAllItems(self, enable=True):
        """Enables or disables all menu items."""

        for Id in self.MenuIds.keys():
            self.Enable(Id, enable)
