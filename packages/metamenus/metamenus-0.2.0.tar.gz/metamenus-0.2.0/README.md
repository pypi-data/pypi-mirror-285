
[![CircleCI](https://dl.circleci.com/status-badge/img/gh/hasii2011/metamenus/tree/master.svg?style=shield)](https://dl.circleci.com/status-badge/redirect/gh/hasii2011/metamenus/tree/master)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/Naereen/StrapDown.js/graphs/commit-activity)
[![PyPI version](https://badge.fury.io/py/metamenus.svg)](https://badge.fury.io/py/metamenus)


# Introduction

This package was forked by [Humberto A. Sanchez II](https://hsanchezii.wordpress.com) 
into GitHub for the purpose of source control and publishing 
to [PyPi](https://pypi.org).  I also updated the formatting to quiet the PEP 8 warnings 
given by PyCharm.  Additionally, I reorganized the packages for maintainability.
This has the effect of changing the imports for the MenuBarEx and MenuEx but does
not alter the functionality.  In order to more explicitly document what used to be
called `custfunc` I created a type named `CustomMethods` so that the API user knows 
that this is a dictionary

# Developer Documents

On the [wiki](https://github.com/hasii2011/metamenus/wiki/Developers)

# Overview

[metamenus](https://www.tacao.com.br/metamenus.html#): classes that aim to simplify the use of menus in wxPython

Written by E. A. Tacao <mailto@tacao.com.br>, (C) 2005... 2020

- `MenuBarEx` is a wx.MenuBar derived class for wxPython; 
- `MenuEx`    is a wx.Menu derived class for wxPython.

Some features:

- Menus are created based on the indentation of items on a list. (See
  'Usage' below.)

- Each menu item will trigger a method on the parent. The methods names may
  be explicitly defined on the constructor, generated automatically or both.

- Allows the developer to enable or disable a menu item or an entire menu given
  its label.

- Supplies EVT_BEFOREMENU and EVT_AFTERMENU, events that are triggered 
  right before and after, respectively, the triggering of a EVT_MENU-bound 
  method on selection of some menu item.

- If your app is already i18n'd, menu items may be translated on the fly.
  All you need to do is to write somewhere a .mo file containing the menu
  translations.

## CustomMethods Type
This new type is defined as follows:

```python
from typing import Dict
from typing import NewType

MenuName   = NewType('MenuName', str)
MethodName = NewType('MethodName', str)

CustomMethods = NewType('CustomMethods', Dict[MenuName, MethodName])

```
## MenuEx Usage:

The MenuEx usage is similar to MenuBarEx (please see below), except that it
has an optional kwarg named show_title (boolean; controls whether the menu
title will be shown; may be platform-dependent):

`MenuEx(self, menus, 
    margin=wx.DEFAULT, 
    show_title=True, 
    font=wx.NullFont, 
    CustomMethods=CustomMethods({}), 
    i18n=True, 
    style=0)`

## MenuBarEx Usage:

In order to put a MenuBarEx inside a frame it is enough to do this:

     MenuBarEx(self, menus)

or you can also use some few optional keyword arguments:
     
`MenuBarEx(self, 
    menus, 
    margin=wx.DEFAULT, 
    font=wx.NullFont,
    customMethods=CustomMethods({}), 
    i18n=True, 
    style=0)`

  Arguments:
    - self:  The frame in question.

    - menus: A python list of 'menus', which are python lists of
             'menu items'. Each 'menu item' is a python list that needs 
             to be in one of the following formats:
    
              [label]
              or [label, args]
              or [label, kwargs]
              or [label, args, kwargs]
              or [label, kwargs, args]  (but please don't do this one as several
              bits may be harmed during the process).
    
      . label: (string) The text for the menu item.
    
               Leading whitespaces at the beginning of a label are used to
               compute the indentation level of the item, which in turn is
               used to determine the grouping of items. MenuBarEx 
               determines one indentation level for every group of two 
               whitespaces.
    
               If you want this item to be a sub-item, increase its
               indentation. Top-level items must have no indentation.
    
               Separators are items labeled with a "-" and may not have 
               args and kwargs.
    
               Menu breaks (please see the wx.MenuItem.Break docs) are 
               items labeled with a "/" and may not have args and kwargs.
    
               Accelerators are handled as usual; please
               refer to the wxPython docs for wx.Menu.Append for more 
               information about them.
    
      . args: (tuple) (helpString, wxItemKind)
    
               - helpString is an optional help string that will be shown 
                 on the parent's status bar. If you don't pass it, no help 
                 string for this item will appear on the statusbar.
    
               - wxItemKind may be one of wx.ITEM_CHECK, "check",
                 wx.ITEM_RADIO or "radio". It is also optional; if you don't 
                 pass one, a default wx.ITEM_NORMAL will be used.
    
               Note that if you have to pass only one argument, you can do
               either:
    
                   args=("", wxItemKind)
                or args=(helpString,)
                or helpString
                or wxItemKind
                or (helpString)
                or (wxItemKind)
    
                When you pass only one item, Metamenus will check if the
                thing passed can be translated as an item kind (either
                wx.RADIO, "radio", etc.) or not, and so will try to guess
                what to do with the thing. So that if you want a status bar
                showing something that could be translated as an item kind,
                say, "radio", you'll have to pass both arguments:
                ("radio",).


       . kwargs: (dict) wxBitmap bmpChecked, wxBitmap bmpUnchecked,
                        wxBitmap bmp,
                        wxFont font, int width,
                        wxColour fgcolour, wxColour bgcolour
    
               These options access wx.MenuItem methods in order to change
               its appearance, and might not be present on all platforms.
               They are internally handled as follows:
    
                 key:                              item method:
    
                 "bmpChecked" and "bmpUnchecked" : SetBitmaps
                 "bmpChecked" or "bmp"           : SetBitmap
                 "font"                          : SetFont
                 "margin",                       : SetMarginWidth
                 "fgColour",                     : SetTextColour
                 "bgColour",                     : SetBackgroundColour
    
               The "bmp", "bmp" and "bmpUnchecked" options accept a bitmap 
               or a callable that returns a bitmap when called. This is 
               useful if you created your bitmaps with encode_bitmaps.py 
               and want to pass something like 
               {"bmpChecked": my_images.getSmilesBitmap} since maybe the wx.App
               may not be created yet.
    
               Please refer to the wxPython docs for wx.MenuItem for more
               information about the item methods.
    
    - margin:   (int) a value that will be used to do a SetMargin() for 
                each menubar item. Please refer to the wxPython docs for
                wx.MenuItem.SetMargin for more information about this.
    
    - font:     (wx.Font) a value that will be used to do a SetFont() for
                each menu item. Please refer to the wxPython docs for
                wx.MenuItem.SetFont for more information about this.
    
    - customMethods: (dict) allows one to define explicitly what will be the
                parent's method called on a menu event.
    
                By default, all parent's methods have to start with "OnMB_"
                (for menubars) or "OnM_" (for menus) plus the full menu
                'path'. For a 'Save' menu item inside a 'File' top menu, 
                e.g:
    
                    def OnMB_FileSave(self):
                        self.file.save()
    
                However, the custfunc arg allows you to pass a dict of
    
                    {menupath: method, menupath: method, ...}
    
                so that if you want your File > Save menu triggering a
                'onSave' method instead, you may pass
    
                    {"FileSave": "onSave"}
                 or {"FileSave": self.onSave}
    
                as custom method entry. This way, your parent's method should look 
                like this instead:
    
                    def onSave(self):
                        self.file.save()
    
                You do not have to put all menu items inside customMethods 
                dictionary. The menupaths not found there will still trigger automatically
                an OnMB_/OnM_-prefixed method.
    
    - i18n:     (bool) Controls whether you want the items to be translated
                or not. Default is True. For more info on i18n, please see
                'More about i18n' below.
    
    - style:    Please refer to the wxPython docs for wx.MenuBar/wx.Menu 
                for more information about this.

## The public methods:

  The 'menu_string' arg on some of the public methods is a string that
  refers to a menu item. For a File > Save menu, e. g., it may be
  "OnMB_FileSave", "FileSave" or the string you passed via the custfunc
  parameter (i. e., if you passed {"FileSave": "onSave"} as custfunc, the
  string may also be "onSave").

  The 'menu_string_list' arg on some of the public methods is a python list
  of 'menu_string' strings described above. Please refer to the methods
  themselves for more details.


More about i18n:
  If you want to get your menu items automatically translated, you'll need
  to:

  1. Create a directory named 'locale' under your app's directory, and 
     under the 'locale', create subdirectories named after the canonical 
     names of the languages you're going to use (e. g., 'pt_BR', 'es_ES', 
     etc.)

  2. Inside each of the subdirectories, write a gettext compiled catalog 
     file (e. g., "my_messages.mo") containing all of the menu labels 
     translated to the language represented by the subdirectory.

  4. The language can be changed on the fly. Whenever you want to change 
     the menu language, execute these lines somewhere in your app:

       l = wx.Locale(wx.LANGUAGE_PORTUGUESE_BRAZILIAN)
       l.AddCatalogLookupPathPrefix("locale")
       l.AddCatalog("my_messages.mo")
       self.my_menu.UpdateMenus()

  Unless you want your menus showing up in pt_BR, replace the
  wx.LANGUAGE_PORTUGUESE_BRAZILIAN above by the proper language identifier.
  For a list of supported identifiers please see the wxPython docs, under 
  the 'Constants\Language identifiers' section.

  Some items may show up in the selected language even though you didn't
  create a .mo file for the translations. That's because wxPython looks for
  them in the wxstd.mo file placed somewhere under the wxPython folders, and
  maybe wxPython already uses some of the strings you are using.

  Note that if you're to distribute a standalone app the wxPython localization
  files may not be present, so it's a good idea to include a specific .mo file
  in your package. On the other hand, if by any reason you _don't_ want the 
  menu items to be translated, you may pass a i18n=False kwarg to the 
  constructor.

  You can use metamenus itself directly from a command line to help on
  creating a gettext-parseable file based on the menus you wrote. For more
  info about this, please see the docs for the _mmprep class below.

  For more info about i18n, .mo files and gettext, please see
  <http://wiki.wxpython.org/index.cgi/Internationalization>.

## Menu bar example:

    a = [["File"],
         ["  New",          "Creates a new file"],
         ["  Save"],
         ["  -"],
         ["  Preview",      "Preview Document",
                            {"bmpChecked": images.getSmilesBitmap(),
                             "fgColour": wx.RED}],
         ["  -"],
         ["  Exit"]]
    
    b = [["Edit"],
         ["  Cut"],
         ["  Copy"],
         ["    Foo",         "check"],
         ["    Bar",         "check"],
         ["  Paste"]]
    
    myMenuBar = MenuBarEx(self, [a, b])

## Context menu example:

    a = [["Edit"],          # A 'top-level' (0-indent) item is used as title;
         ["  Cut"],
         ["  Copy"],
         ["    Foo",        "radio"],
         ["    Bar",        "radio"],
         ["  Paste"]]
    
    myContextMenu = MenuEx(self, a)


If you don't want to show the title for the context menu:

   myContextMenu = MenuEx(self, a, show_title=False)

(Please note that menu titles may be platform dependent).

A very default 'File' menu example:

       [
        ['&File'],
        ['  &New\tCtrl+N'],
        ['  &Open...\tCtrl+O'],
        ['  &Save\tCtrl+S'],
        ['  Save &As...\tCtrl+Shift+S'],
        ['  -'],
        ['  Publis&h\tCtrl+Shift+P'],
        ['  -'],
        ['  &Close\tCtrl+W'],
        ['  C&lose All'],
        ['  -'],
        ['  E&xit\tAlt+X']
       ]


## Note: 
tacao does not maintain this fork.  

For all kind of problems, requests, enhancements, bug reports, etc,
please drop me an e-mail.

Maintainer  <a href="mailto:email@humberto.a.sanchez.ii@gmail.com?subject=Hello Humberto">Humberto A. Sanchez II</a>  (C) 2024

