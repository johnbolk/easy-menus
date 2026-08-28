"""Wrapper classes for easy implementation of Tkinter menus.

This package provides the following class definitions:

* MainMenu    - A class that displays a menu bar across the top of a window
* Menu        - A class used to represent a selection menu
* MenuItem    - A class used to represent a selectable item in a Menu
* EntryType   - An enumerated dataclass of the available MenuItem entry types
* ConfigInfo  - A dataclass that provides MenuItem configuration information
* MenuButton  - A class used to represent a drop-down menu selection button
* ContextMenu - A class used to represent a pop-up context menu.
"""

__version__ = '1.3.6'

from .menus import Menu, MainMenu, MenuItem, MenuButton, ContextMenu, ConfigInfo, EntryType
