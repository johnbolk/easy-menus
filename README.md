# Project Description

**Wrapper classes for easy implementation of Tkinter menus.**

This package was created to simplify the process of implementing menus in Tkinter windows. This was accomplished by defining functional "building block" classes which can be assembled together to create the user interface. Each of these classes provides the methods and properties needed to accomplish the assembly task. The design goal was to make this as easy and intuitive as possible.

The following script demonstrates how this package can be used to construct a Tkinter window that displays a **File** drop-down menu in it's top menu bar. The **File** menu, in turn, has a **Quit** selection item that can close the window.

```
from tkinter import Tk
from menus import MainMenu

root = Tk()

def on_quit():
    root.destroy()

# Create and Populate the Top Menu Bar
menu_bar = MainMenu(root)
file_menu = menu_bar.add_menu('File')
file_menu.add_item('Quit', on_quit)

root.mainloop()
```

The package author tried to adhere to these three guiding principles from [**The Zen of Python**](https://peps.python.org/pep-0020/)
* Beautiful is better than ugly.
* Simple is better than complex.
* Readability counts.

# Installation

```
pip install easy-menus
```

<div class="page"/>

# Overview

This package provides the following class definitions **:**

* **MainMenu -** A class that displays a menu bar across the top of a window.
* **Menu -** A class used to represent a selection menu.
* **MenuItem -** A class used to represent a selection item in a Menu.
* **EntryType -** An enumerated dataclass of the available MenuItem entry types.
* **ConfigInfo -** A dataclass that provides MenuItem configuration information.
* **MenuButton -** A class used to represent a drop-down selection menu button.
* **ContextMenu -** A class used to represent a pop-up context menu.

```
import tkinter as tk
from menus import MainMenu

root = tk.Tk()
root.geometry('400x300')

def on_exit():
    """Handle the 'Exit' selection."""
    root.destroy()

# Create and Populate the Top Menu Bar
menu_bar = MainMenu(root)
file_menu = menu_bar.add_menu('File')
file_menu.add_item('E&xit', on_exit).shortcut = 'q'

root.mainloop()
```

```menu_bar = MainMenu(root)``` Creates the top menu bar for the window

```file_menu = menu_bar.add_menu('File')``` Creates the **File** menu and adds it to the top menu bar

<div class="page"/>

 An equivalent approach would be to explicitly create the **File** menu and add it to the top menu bar. Followed by creating the **Exit** selection item, assigning the **Ctrl+Q ( **<font size="2">**&#x2318;**</font> **Q )** shortcut, and finally adding it to the **File** menu.

 This sequence is shown in the following script **:**

```
import tkinter as tk
from menus import MainMenu, Menu, MenuItem

root = tk.Tk()
root.geometry('400x300')

def on_exit():
    """Handle the 'Exit' selection."""
    root.destroy()

# Create and Populate the Top Menu Bar
menu_bar = MainMenu(root)
file_menu = Menu('File')
menu_bar.add(file_menu)
exit_item = MenuItem('E&xit', on_exit)
exit_item.shortcut = 'q'
file_menu.add(exit_item)

root.mainloop()
```


The macOS command character <font size="2">**&#x2318;**</font> **S** versus the Windows/Linux **Ctrl+S**.

```
import tkinter as tk
from menus import MainMenu, EntryType, ConfigInfo

...

# Create and Populate the Top Menu Bar
menu_bar = MainMenu(root)
menu_bar.begin_update()
file_menu = menu_bar.add_menu('File')
edit_menu = menu_bar.add_menu('Edit')
view_menu = menu_bar.add_menu('View')
help_menu = menu_bar.add_menu('Help')
menu_bar.end_update()

file_menu.begin_update()
file_menu.add_item('Open', on_open).shortcut = 'o'
file_menu.add_item('Save', on_save).shortcut = 's'
file_menu.add_separator()
file_menu.add_item('E&xit', on_exit).shortcut = 'q'
file_menu.end_update()
```

```
edit_menu.begin_update()
edit_menu.add_item('Cu&t', on_cut).shortcut = 'x'
edit_menu.add_item('Copy', on_copy).shortcut = 'c'
edit_menu.add_item('Paste', on_paste).shortcut = 'v'
edit_menu.add_separator()

find_menu = edit_menu.add_menu('Find')
find_menu.add_item('Find', on_find).shortcut = 'f'
find_menu.add_item('Replace', on_replace).shortcut = 'r'

edit_menu.end_update()
```

```
zoom_value = tk.IntVar(value=1)

def on_zoom():
    """Handle the 'Zoom' selections."""
    print(f'*** View_Menu - Zoom {zoom_value.get()}00% was Selected ***')

view_menu = menu_bar.add_menu('View')
view_menu.begin_update()
for i in (1, 2, 4):
    label = f'Zoom &{i}00%'
    info = ConfigInfo(EntryType.RADIOBUTTON, zoom_value, i)
    view_menu.add_item(label, on_zoom, config=info)
view_menu.end_update()

help_menu.add_item('About', on_about)
```

<div class="page"/>

# API Documentation

## MainMenu

**Displays a menu bar across the top of a window.**

### MainMenu( ***parent*** )

Construct and initialize the MainMenu.
* ***parent* : Any -** The application window displaying the MainMenu.

### Properties

* **count : int -** The total number of items in the MainMenu. ( readonly )
* **enabled : bool -** A value indicating whether the MainMenu is enabled. ( read / write )

### Methods

* **begin_update( ) :** Prevent screen redraws when updating the items in the MainMenu. This method should be called prior to making any updates or changes to the MainMenu.

* **end_update( ) :** Enable the screen to display the items in the MainMenu. This method should be called after the updates or changes to the MainMenu have been completed.

* **add( *menu* ) :** Add a previously created Menu to the end of the MainMenu.
    * ***menu* : Menu -** The previously created Menu.

* **add_menu( *text* ) -> Menu :** Create and add a Menu to the end of the MainMenu. This method returns the newly created Menu.
    * ***text* : str -** The text label string for the Menu.

* **add_range( *menus* ) :** Add a list of previously created menus to the MainMenu.
    * ***menus* : list[ Menu ] -** The list of previously created Menus.

<div class="page"/>

* **insert( *index*, *menu* ) :** Insert a previously created Menu at the index location in the MainMenu.
    * ***index* : int -** The Menu's location within the MainMenu.
    * ***menu* : Menu -** The previously created Menu.

* **insert_menu( *index*, *text* ) -> Menu :** Create and insert a Menu at the index location in the MainMenu. This method returns the newly created Menu.
    * ***index* : int -** The newly created Menu's location within the MainMenu.
    * ***text* : str -** The text label string for the Menu.

* **index_of( *menu* ) -> int :** Report the index value of the specified Menu in the MainMenu. This method returns the zero-based index value if found, **-1** otherwise.
    * ***menu* : Menu -** The specified Menu in the MainMenu.

* **remove( *menu*) :** Remove the specified Menu from the MainMenu.
    * ***menu* : MenuItem | Menu -** The specified Menu.

* **remove_at( *index* ) :** Remove a Menu from the MainMenu at the specified index location.
    * ***index* : int -** The specified Menu's location within the MainMenu.

<div class="page"/>

## Menu

**A selection menu.**

### Menu( *text*, *image*=None )

Construct and initialize the Menu.
* ***text* : str -** The text label string for the Menu.
* ***image* : PhotoImage | None -** The optional image associated with the Menu, **default = None.**

### Properties

* **count : int -** The total number of items in the Menu. ( readonly )
* **enabled : bool -** A value indicating whether the Menu is enabled. ( read / write )
* **image : PhotoImage | None -** The image associated with the Menu. ( read / write )
* **text : str -** The text label string for the Menu. ( read / write )
* **visible : bool -** A value indicating whether the Menu is visible. ( read / write )

### Methods

* **copy( ) -> Menu :** Create and return a deep copy of the Menu.

* **begin_update( ) :** Prevent screen redraws when updating the items in the Menu. This method should be called prior to making any updates or changes to the Menu.

* **end_update( ) :** Enable the screen to display the items in the Menu. This method should be called after the updates or changes to the Menu have been completed.

* **add( *entry* ) :** Add a previously created entry to the end of the Menu.
    * ***entry* : MenuItem | Menu -** The previously created MenuItem or Menu entry.

* **add_item( *text*, *command*=None, *image*=None, *config*=None ) -> MenuItem :** Create and add a MenuItem to the end of the Menu. This method returns the newly created MenuItem.
    * ***text* : str -** The text label string for the MenuItem.
    * ***command* : Callable | None -** The event handler associated with the MenuItem, **default = None.**
    * ***image* : PhotoImage | None -** The optional image associated with the MenuItem, **default = None.**
    * ***config* : ConfigInfo | None -** The optional MenuItem configuration information, **default = None.**

* **add_menu( *text*, *image*=None ) -> Menu :** Create and add a Menu to the end of the Menu. This method returns the newly created Menu.
    * ***text* : str -** The text label string for the Menu.
    * ***image* : PhotoImage | None -** The optional image associated with the Menu, **default = None.**

<div class="page"/>

* **add_range( *entries* ) :** Add a list of previously created entries to the Menu.
    * ***entries* : list[ MenuItem, Menu ] -** The list of previously created MenuItem and Menu entries.

* **add_separator( ) :** Add a separator bar to the end of the Menu.

* **clear( ) :** Remove all existing entries from the Menu.

* **insert( *index*, *entry* ) :** Insert a previously created entry at the index location in the Menu.
    * ***index* : int -** The entry's location within the Menu.
    * ***entry* : MenuItem | Menu -** The previously created MenuItem or Menu entry.

* **insert_item( *index*, *text*, *command*=None, *image*=None, *config*=None ) -> MenuItem :** Create and insert a MenuItem at the index location in the Menu. This method returns the newly created MenuItem.
    * ***index* : int -** The newly created MenuItem's location within the Menu.
    * ***text* : str -** The text label string for the MenuItem.
    * ***command* : Callable | None -** The event handler associated with the MenuItem, **default = None.**
    * ***image* : PhotoImage | None -** The optional image associated with the MenuItem, **default = None.**
    * ***config* : ConfigInfo | None -** The optional MenuItem configuration information, **default = None.**

* **insert_menu( *index*, *text*, *image*=None ) -> Menu :** Create and insert a Menu at the index location in the Menu. This method returns the newly created Menu.
    * ***index* : int -** The newly created Menu's location within the Menu.
    * ***text* : str -** The text label string for the Menu.
    * ***image* : PhotoImage | None -** The optional image associated with the Menu, **default = None.**

* **insert_separator( *index* ) :** Insert a separator bar at the index location in the Menu.
    * ***index* : int -** The separator bar's location within the Menu.

* **index_of( *entry* ) -> int :** Report the index value of the specified entry in the Menu. This method returns the zero-based index value if found, **-1** otherwise.
    * ***entry* : MenuItem | Menu -** The specified MenuItem or Menu entry in the Menu.

* **remove( *entry*) :** Remove the specified entry from the Menu.
    * ***entry* : MenuItem | Menu -** The specified MenuItem or Menu entry.

* **remove_at( *index* ) :** Remove an entry from the Menu at the specified index location.
    * ***index* : int -** The entry's location within the Menu.

<div class="page"/>

## MenuItem

**A selection item in a Menu.**

### MenuItem( *text*, *command*=None, *image*=None, *config*=None )

Construct and initialize the MenuItem.
* ***text* : str -** The text label string for the MenuItem.
* ***command* : Callable | None -** The event handler associated with the MenuItem, **default = None.**
* ***image* : PhotoImage | None -** The optional image associated with the MenuItem, **default = None.**
* ***config* : ConfigInfo | None -** The optional MenuItem configuration information, **default = None.**

### Properties

* **checked : bool -** A value indicating whether a MenuItem is checked. ( readonly )
* **enabled : bool -** A value indicating whether the MenuItem is enabled. ( read / write )
* **image : PhotoImage | None -** The optional image associated with the MenuItem. ( read / write )
* **shortcut : str -** The MenuItem's shortcut key character value. ( read / write )
* **text : str -** The text label string for the MenuItem. ( read / write )
* **visible : bool -** A value indicating whether the MenuItem is visible. ( read / write )

### Methods

* **copy( ) -> MenuItem :** Create and return a deep copy of the MenuItem.

* **set_custom_shortcut( *sequence*, *accelerator* ) :** Set a custom, user-defined shortcut for the MenuItem.
    * ***sequence* : str -** The custom event sequence string ( e.g. '\<Control-Shift-A\>' ).
    * ***accelerator* : str -** The custom accelerator description ( e.g. 'Ctrl+Shift+A' ).

<div class="page"/>

## EntryType

**The available MenuItem entry types.**

* **STANDARD -** The MenuItem entry is a standard menu selection.

* **CHECKBUTTON -** The MenuItem entry behaves like a Tkinter Checkbutton widget.

* **RADIOBUTTON -** The MenuItem entry behaves like a Tkinter Radiobutton widget.

## ConfigInfo

**The MenuItem configuration information data class.**

### ConfigInfo( *entry_type*=EntryType.STANDARD, *variable*=None, *value*=0 )

* ***entry_type* : EntryType -** The MenuItem entry type identifier, **default = EntryType.STANDARD.**

* ***variable* : IntVar | None -** The Tkinter control variable associated with either a **CHECKBUTTON** or **RADIOBUTTON** MenuItem entry, **default = None**.

* ***value* : int -** The control value assigned to a **RADIOBUTTON** MenuItem entry, **default = 0.**

<div class="page"/>

## MenuButton

**A drop-down selection menu button.**

### MenuButton( *parent*, *text*, *width*=-1, *image*=None )

Construct and initialize the MenuButton.
* ***parent* : Any -** The parent widget of the MenuButton
* ***text* : str -** The text label string for the MenuButton.
* ***width* : int -** The character width of the MenuButton, **default = -1 ( 'auto-size' ).**
* ***image* : PhotoImage | None -** The optional image associated with the MenuButton, **default = None.**

### Properties

* **enabled : bool -** A value indicating whether the MenuButton is enabled. ( read / write )
* **image : PhotoImage | None -** The image associated with the MenuButton. ( read / write )
* **text : str -** The text label string for the MenuButton. ( read / write )
* **menu : Menu -** The MenuButton's drop down menu. ( readonly)

<div class="page"/>

## ContextMenu

**A pop-up context menu.**

### ContextMenu( )

Construct and initialize a ContextMenu.


### Additional Methods

* **copy( ) -> ContextMenu :** Create and return a deep copy of the ContextMenu.

* **display( *location* ) :** Display the ContextMenu at the specified screen location.
    * ***location* : tuple[ int, int ] -** The specified screen location (x, y) of the upper left corner of the ContextMenu.

<div class="page"/>

# Usage Examples
