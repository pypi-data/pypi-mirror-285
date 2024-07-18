
from logging import Logger
from logging import getLogger
from typing import Dict
from typing import NewType
from typing import cast

from wx import EVT_MENU

from wx import Menu
from wx import MenuBar

from wx import PostEvent
from wx import WindowIDRef

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

from metamenus.metamenus import _clean

No_Window_ID_Ref = cast(WindowIDRef, None)

MBStringToWindowIdRef = NewType('MBStringToWindowIdRef', Dict[str, WindowIDRef])
WindowIdRefToSItem    = NewType('WindowIdRefToSItem',    Dict[WindowIDRef, SItem])


class MenuBarEx(BaseMenuEx, MenuBar):
    """
    MenuBarEx Main stuff
    """
    def __init__(self, *args, **kwargs):
        # noinspection SpellCheckingInspection
        """
        MenuBarEx(parent, menus, margin=wx.DEFAULT, font=wx.NullFont, customMethods=CustomMethods({}), i18n=True, style=0)
        """
        BaseMenuEx.__init__(self, *args, **kwargs)

        self.logger: Logger = getLogger(META_MENUS_LOGGING_NAME)

        strippedKWArgs = self._extractKeyWordValues(**kwargs)
        MenuBar.__init__(self, **strippedKWArgs)

        # A reference to all the sItems involved.
        tops = []

        # 'fix' for https://github.com/wxWidgets/Phoenix/issues/1648
        self.x = []

        self.logger.debug(f'{self._menus}')
        # For each menu...
        for menuTreeDescription in self._menus:
            # Parse the supplied menu 'tree'.
            self.logger.info(f'Evolving: {menuTreeDescription}')
            top = BaseMenuEx.evolve(menuTreeDescription)

            # Create these menus first...
            wxMenus = {top: Menu()}
            for k in top.GetChildWithChildren():
                wxMenus[k] = Menu()

                # ...and append their respective children.
                for h in k.GetChildren():
                    wxMenus = self._makeMenus(wxMenus, h, k, self._margin, self._font, self._i18n)

            # Now append these items to the top level menu.
            for h in top.GetChildren():
                wxMenus = self._makeMenus(wxMenus, h, top, self._margin, self._font, self._i18n)

            # Now append the top menu to the menu bar.
            self.Append(wxMenus[top], top.GetRealLabel(self._i18n))

            # Store a reference of this sItem.
            tops.append(top)

            # 'fix' for https://github.com/wxWidgets/Phoenix/issues/1648
            self.x.append(wxMenus)

        # Now find out what are the methods that should be called upon
        # menu items selection.
        MBIds: WindowIdRefToSItem = WindowIdRefToSItem({})
        self.MBStrings = MBStringToWindowIdRef({})
        for top in tops:
            for child in top.GetChildren(True):
                # noinspection SpellCheckingInspection
                """ child.SetMethod(self._configuration.menuBarPrefix, custfunc) """
                child.SetMethod(self._configuration.menuBarPrefix, self._customMethods)
                MBIds[child.GetId()] = child
                self.MBStrings.update(child.GetAllMethods())

        # It won't hurt if we get rid of a None key, if any.
        self.MBStrings.pop(No_Window_ID_Ref)

        # We store the position of top-level menus rather than ids because
        # wx.Menu.EnableTop uses positions...
        for i, top in enumerate(tops):
            self.MBStrings[_clean(top.GetLabelText())] = i
            MBIds[i] = top

        # Nice class. 8^) Will take care of this automatically.
        self._parent.SetMenuBar(self)
        self._parent.Bind(EVT_MENU, self.OnMB_)

        # Now do something about the IDs and accelerators...
        self.MBIds: WindowIdRefToSItem = MBIds

    def OnMB_(self, evt):
        """
        Called on all menu events for this menu. It will in turn call
        the related method on parent, if any.
        """

        try:
            attr = self.MBIds[evt.GetId()]

            self.OnMB_before()

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
            self.OnMB_after(attr_name)

        except KeyError:
            # Maybe another menu was triggered elsewhere in parent.
            pass

    def OnMB_before(self):
        # noinspection SpellCheckingInspection
        """
        If you need to execute something right before a menu event is
        triggered, you can bind the EVT_BEFOREMENU.
        """

        evt = MenuExBeforeEvent(-1, obj=self)
        PostEvent(self, evt)

    def OnMB_after(self, attr_name=None):
        # noinspection SpellCheckingInspection
        """
        If you need to execute something right after a menu event is
        triggered, you can bind the EVT_AFTERMENU.
        """

        evt: MenuExAfterEvent = MenuExAfterEvent(-1, obj=self, item=attr_name)
        PostEvent(self, evt)

    def UpdateMenus(self):
        """
        Call this to update menu labels whenever the current locale
        changes.
        """

        if not self._i18n:
            return

        for k, v in self.MBIds.items():
            # Update top-level menus
            if not v.GetParent():
                v.Update()
                self.SetMenuLabel(k, v.GetRealLabel(self._i18n))
            # Update other menu items
            else:
                item = self.FindItemById(k)
                if item is not None:   # Skip separators
                    v.Update()
                    self.SetLabel(k, v.GetRealLabel(self._i18n))

    def GetItemState(self, menu_string):
        """Returns True if a checkable menu item is checked."""

        this = self.MBStrings[menu_string]
        try:
            r = self.IsChecked(this)
        except wxAssertionError:
            r = False
        return r

    def SetItemState(self, menu_string, check=True):
        """Toggles a checkable menu item checked or unchecked."""

        this = self.MBStrings[menu_string]
        self.Check(this, check)

    def EnableItem(self, menu_string, enable=True):
        """Enables or disables a menu item via its label."""

        this = self.MBStrings[menu_string]
        self.Enable(this, enable)

    def EnableItems(self, menu_string_list, enable=True):
        """Enables or disables menu items via a list of labels."""

        for menu_string in menu_string_list:
            self.EnableItem(menu_string, enable)

    def EnableTopMenu(self, menu_string, enable=True):
        """Enables or disables a top level menu via its label."""

        this = self.MBStrings[menu_string]
        self.EnableTop(this, enable)

    def EnableTopMenus(self, menu_string_list, enable=True):
        """Enables or disables top level menus via a list of labels."""

        for menu_string in menu_string_list:
            self.EnableTopMenu(menu_string, enable)
