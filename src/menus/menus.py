"""Wrapper classes for easy implementation of Tkinter menus.

This module provides the following class definitions:

* MainMenu    - A class that displays a menu bar across the top of a window
* Menu        - A class used to represent a selection menu
* MenuItem    - A class used to represent a selectable item in a Menu
* EntryType   - An enumerated dataclass of the available MenuItem entry types
* ConfigInfo  - A dataclass that provides MenuItem configuration information
* MenuButton  - A class used to represent a drop-down menu selection button
* ContextMenu - A class used to represent a pop-up context menu.
"""

__version__ = '1.3.6'

import enum
import platform
from warnings import warn
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple, Sequence, Union, Optional, Callable
import tkinter as tk
from PIL.ImageTk import PhotoImage
from PIL import Image, ImageTk

MAC_OS = platform.system() == 'Darwin'


class EntryType(enum.Enum):
    """The available MenuItem entry type identifiers.

    Attributes
    ----------
    STANDARD
        The MenuItem entry is a standard menu selection
    CHECKBUTTON
        The MenuItem entry behaves like a Tkinter Checkbutton widget
    RADIOBUTTON
        The MenuItem entry behaves like a Tkinter Radiobutton widget
    """

    STANDARD = 0
    CHECKBUTTON = 1
    RADIOBUTTON = 2
    SEPARATOR = 3


@dataclass
class ConfigInfo:
    """The MenuItem configuration information.

    Attributes
    ----------
    entry_type : EntryType
        The type identifier for the MenuItem (default is STANDARD)
    variable : tk.IntVar, optional
        The control variable associated with the MenuItem (default is None)
    value : int
        The control value assigned to a RADIOBUTTON MenuItem entry
    """

    entry_type: EntryType = EntryType.STANDARD
    variable: Optional[tk.IntVar] = None
    value: int = 0


class Menu:
    """A class used to represent a selection menu."""

    def __init__(
        self,
        text: str,
        image: Union[PhotoImage, tk.PhotoImage, None] = None,
    ):
        """Construct and initialize the Menu.

        Parameters
        ----------
        text : str
            The text label string for the Menu
        image : PhotoImage | tk.PhotoImage | None
            The optional image associated with the Menu
        """
        self._my: Dict[str, Any] = {'text': text, 'image': image}
        self._my.update({'entry_list': [], 'display_count': 0})
        self._my.update({'grayed': _grayed_image(image), 'owner': None})
        self._my.update({'active': True, 'enabled': True, 'visible': True})
        self._my.update({'update_text': True, 'update': True, 'index': -1})
        self._my.update({'context_menu': text == ''})
        self.parent: Union[MainMenu, ContextMenu, Menu, None] = None
        self.owner = None

    @property
    def count(self) -> int:
        """The total number of items in the Menu."""
        return len(self._my['entry_list'])

    @property
    def enabled(self) -> bool:
        """Get/Set a value indicating whether the Menu is enabled."""
        return self._my['enabled']

    @enabled.setter
    def enabled(self, enabled: bool) -> None:
        """Get/Set a value indicating whether the Menu is enabled."""
        self._my['enabled'] = enabled
        enabled &= bool(self._my['active'])
        mac_main_menu = MAC_OS and isinstance(self.parent, MainMenu)
        if isinstance(self.owner, tk.Menu) and self._my['index'] >= 0:
            state = tk.NORMAL if (enabled or mac_main_menu) else tk.DISABLED
            self._my['owner'].entryconfigure(self._my['index'], state=state)
        for entry in self._my['entry_list']:
            entry.update_active(enabled)
        if mac_main_menu:
            self.update_display()
        self.image = self._my['image']
        if not mac_main_menu or self._my['update_text']:
            self.text = self._my['text']

    @property
    def image(self) -> Union[PhotoImage, tk.PhotoImage, None]:
        """Get/Set the image associated with the Menu."""
        return self._my['image']

    @image.setter
    def image(self, image: Union[PhotoImage, tk.PhotoImage, None]) -> None:
        """Get/Set the image associated with the Menu."""
        if not self._my['context_menu']:
            config = _update_image(image, self._my)
            if isinstance(self.parent, Menu):
                if isinstance(self.owner, tk.Menu) and self._my['index'] >= 0:
                    self._my['owner'].entryconfigure(self._my['index'], config)

    @property
    def owner(self) -> Union[tk.Menu, tk.Menubutton, None]:
        """Get/Set the current owner of the Menu."""
        return self._my['owner']

    @owner.setter
    def owner(self, owner: Union[tk.Menu, tk.Menubutton, None]) -> None:
        """Get/Set the current owner of the Menu."""
        self._my['owner'] = owner
        self.menu = tk.Menu(owner, tearoff=0)
        self.update_display()

    @property
    def text(self) -> str:
        """Get/Set the text label string for the Menu."""
        return self._my['text']

    @text.setter
    def text(self, text: str) -> None:
        """Get/Set the text label string for the Menu."""
        self._my['text'] = '' if self._my['context_menu'] else text
        if isinstance(self.owner, tk.Menu) and self._my['index'] >= 0:
            self._my['update_text'] = False
            label, index = _get_shortcut(self, text)
            config: Dict[str, Any] = {'label': label, 'underline': index}
            self._my['owner'].entryconfigure(self._my['index'], config)

    @property
    def visible(self) -> bool:
        """Get/Set a value indicating whether the MenuItem is visible."""
        return self._my['visible'] and self._my['active']

    @visible.setter
    def visible(self, visible: bool) -> None:
        """Get/Set a value indicating whether the MenuItem is visible."""
        if visible is not self._my['visible']:
            self._my['visible'] = visible or self._my['context_menu']
            if MAC_OS and isinstance(self.parent, MainMenu):
                self._my['active'] = visible
                self.enabled = self._my['enabled']
            elif self.parent is not None:
                self.parent.update_display()

    def __iter__(self) -> Any:
        """Make the Menu class an iterable collection."""
        return (entry for entry in self._my['entry_list'])

    def __getitem__(self, index: int) -> Union['MenuItem', 'Menu']:
        """Get the entry specified by the index value."""
        return self._my['entry_list'][index]

    def copy(self) -> 'Menu':
        """Create and return a deep copy of the Menu."""
        copy = Menu(self.text, self.image)
        copy.begin_update()
        for entry in self._my['entry_list']:
            copy.add(entry.copy())
        copy.end_update()
        return copy

    def begin_update(self) -> None:
        """Prevent screen redraws when updating the items in the Menu."""
        self._my['update'] = False

    def end_update(self) -> None:
        """Enable the screen to display the items in the Menu."""
        self._my['update'] = True
        self.update_display()

    def add(self, entry: Union['MenuItem', 'Menu']) -> None:
        """Add a previously created entry to the end of the Menu.

        Parameters
        ----------
        entry : MenuItem | Menu
            The previously created MenuItem or Menu entry
        """
        self._insert(self.count, entry)

    def add_item(
        self,
        text: str,
        command: Optional[Callable[..., None]] = None,
        image: Union[PhotoImage, tk.PhotoImage, None] = None,
        config: Optional[ConfigInfo] = None,
    ) -> 'MenuItem':
        """Create and add a MenuItem to the end of the Menu.

        Parameters
        ----------
        text : str
            The text label string for the MenuItem
        command : Callable, optional
            The event handler associated with the MenuItem selection
        image : PhotoImage | tk.PhotoImage | None
            The optional image associated with the MenuItem
        config : ConfigInfo | None
            The optional MenuItem configuration information

        Returns
        -------
        MenuItem
            The newly created MenuItem
        """
        return self._insert(self.count, MenuItem(text, command, image, config))

    def add_menu(
        self,
        text: str,
        image: Union[PhotoImage, tk.PhotoImage, None] = None,
    ) -> 'Menu':
        """Create and add a Menu to the end of the Menu.

        Parameters
        ----------
        text : str
            The text label string for the Menu
        image : PhotoImage | tk.PhotoImage | None
            The optional image associated with the Menu

        Returns
        -------
        Menu
            The newly created Menu
        """
        return self._insert(self.count, Menu(text, image))

    def add_range(self, entries: Sequence[Union['MenuItem', 'Menu']]):
        """Add a list of previously created entries to the Menu.

        Parameters
        ----------
        entries : list[MenuItem | Menu]
            The list of previously created MenuItem and Menu entries
        """
        update = self._my['update']
        self.begin_update()
        for entry in entries:
            self.add(entry)
        if update:
            self.end_update()

    def add_separator(self) -> None:
        """Add a separator bar to the end of the Menu."""
        self._insert(self.count, MenuItem('-'))

    def clear(self) -> None:
        """Remove all existing entries from the Menu."""
        if self._my['display_count'] > 0:
            self.menu.delete(0, self._my['display_count'] - 1)
        self._my['display_count'] = 0
        self._my['entry_list'].clear()

    def insert(self, index: int, entry: Union['MenuItem', 'Menu']) -> None:
        """Insert a previously created entry at the index location.

        Parameters
        ----------
        index : int
            The entry's location within the Menu
        entry : MenuItem | Menu
            The previously created MenuItem or Menu entry
        """
        self._insert(index, entry)

    def insert_item(
        self,
        index: int,
        text: str,
        command: Optional[Callable[..., None]] = None,
        image: Union[PhotoImage, tk.PhotoImage, None] = None,
        config: Optional[ConfigInfo] = None,
    ) -> 'MenuItem':
        """Create and insert a MenuItem at the index location.

        Parameters
        ----------
        index : int
            The newly created MenuItem's location within the Menu
        text : str
            The text label string for the MenuItem
        command : Callable, optional
            The event handler associated with the MenuItem selection
        image : PhotoImage |  tk.PhotoImage | None
            The optional image associated with the MenuItem
        config : ConfigInfo | None
            The optional MenuItem configuration information

        Returns
        -------
        MenuItem
            The newly created MenuItem
        """
        return self._insert(index, MenuItem(text, command, image, config))

    def insert_menu(
        self,
        index: int,
        text: str,
        image: Union[PhotoImage, tk.PhotoImage, None] = None,
    ) -> 'Menu':
        """Create and insert a Menu at the index location.

        Parameters
        ----------
        index : int
            The newly created Menu's location within the Menu
        text : str
            The text label string for the Menu
        image : PhotoImage |  tk.PhotoImage | None
            The optional image associated with the Menu

        Returns
        -------
        Menu
            The newly created Menu
        """
        return self._insert(index, Menu(text, image))

    def insert_separator(self, index: int) -> None:
        """Create and insert a separator bar at the index location.

        Parameters
        ----------
        index : int
            The separator bar's location within the Menu
        """
        self._insert(index, MenuItem('-'))

    def index_of(self, entry: Union['MenuItem', 'Menu']) -> int:
        """Report the index value of the specified entry in the Menu.

        Parameters
        ----------
        entry : MenuItem | Menu
            The specified MenuItem or Menu entry in the Menu

        Returns
        -------
        int
            The zero-based index value if found, -1 otherwise.
        """
        index = -1
        if entry in self._my['entry_list']:
            index = self._my['entry_list'].index(entry)
        return index

    def remove(self, entry: Union['MenuItem', 'Menu']) -> None:
        """Remove the specified entry from the Menu.

        Parameters
        ----------
        entry : MenuItem | Menu
            The specified MenuItem or Menu entry.
        """
        self.remove_at(self.index_of(entry))

    def remove_at(self, index: int) -> None:
        """Remove an entry from the Menu at the specified index.

        Parameters
        ----------
        index : int
            The entry's location within the Menu
        """
        if 0 <= index < self.count:
            self._my['entry_list'][index].owner = None
            self._my['entry_list'][index].parent = None
            self._my['entry_list'].pop(index)
            self.update_display()

    def update_active(self, active: bool) -> None:
        """Update the active flag."""
        self._my['active'] = active
        self.enabled = self._my['enabled']

    def update_position(self, position: int) -> None:
        """Update the position value of the Menu in the displayed Menu."""
        self._my['index'] = position
        self.enabled = self._my['enabled']

    def update_display(self) -> None:
        """Update the display of visible items in the Menu."""
        if self._my['update']:
            if self._my['display_count'] > 0:
                self.menu.delete(0, self._my['display_count'] - 1)
            self._my['display_count'] = 0
            for entry in self._my['entry_list']:
                if entry.visible:
                    entry.owner = self.menu
                    if isinstance(entry, Menu):
                        self.menu.add_cascade(menu=entry.menu)
                    else:
                        self._add_entry(entry)
                    entry.update_position(self._my['display_count'])
                    self._my['display_count'] += 1
                else:
                    entry.update_position(-1)

    def _add_entry(self, entry: 'MenuItem') -> None:
        """Add an entry to the actual Tkinter Menu."""
        config: Dict[str, Any] = {'command': entry.command}
        if entry.entry_type == EntryType.SEPARATOR:
            self.menu.add_separator()
        elif entry.entry_type == EntryType.STANDARD:
            self.menu.add_command(config)
        else:
            config.update({'variable': entry.variable})
            if entry.entry_type == EntryType.CHECKBUTTON:
                self.menu.add_checkbutton(config)
            else:  # EntryType.RADIOBUTTON
                config.update({'value': entry.value})
                self.menu.add_radiobutton(config)

    def _insert(self, index: int, entry: Any) -> Any:
        """Insert the entry at the specified index."""
        if not isinstance(entry, ContextMenu):
            entry.parent = self
            if index >= self.count:
                self._my['entry_list'].append(entry)
            else:
                self._my['entry_list'].insert(max(0, index), entry)
            self.update_display()
        else:
            warn('Cannot add a ContextMenu to another Menu!', stacklevel=3)
        return entry


class MenuItem:
    """A class used to represent a selectable item in a Menu."""

    def __init__(
        self,
        text: str,
        command: Optional[Callable[..., Any]] = None,
        image: Union[PhotoImage, tk.PhotoImage, None] = None,
        config: Optional[ConfigInfo] = None,
    ):
        """Construct and initialize the MenuItem.

        Parameters
        ----------
        text : str
            The text label string for the MenuItem
        command : Callable, optional
            The event handler associated with the MenuItem selection
        image : PhotoImage | tk.PhotoImage | None
            The optional image associated with the MenuItem
        config : ConfigInfo | None
            The optional MenuItem configuration information
        """
        info = ConfigInfo() if config is None else config
        variable = tk.IntVar() if info.variable is None else info.variable
        self.owner: Optional[tk.Menu] = None
        self.parent: Union[ContextMenu, Menu, None] = None
        self._my: Dict[str, Any] = {'text': text, 'command': command}
        self._my.update({'image': image, 'type': info.entry_type})
        self._my.update({'grayed': _grayed_image(image), 'index': -1})
        self._my.update({'variable': variable, 'value': info.value})
        self._my.update({'active': True, 'enabled': True, 'visible': True})
        self._my.update({'shortcut': '', 'key': '', 'event': '', 'accel': ''})
        if text.strip() == '-':
            self._my['type'] = EntryType.SEPARATOR

    @property
    def checked(self) -> bool:
        """Get/Set a value indicating whether the MenuItem is checked."""
        status = False
        if self._my['type'] == EntryType.CHECKBUTTON:
            status = self._my['variable'].get() != 0
        return status

    @checked.setter
    def checked(self, status: bool) -> None:
        """Get/Set a value indicating whether the MenuItem is checked."""
        if self._my['type'] == EntryType.CHECKBUTTON:
            self._my['variable'].set(1 if status else 0)

    @property
    def command(self) -> Optional[Callable[..., Any]]:
        """The event handler associated with the MenuItem selection."""
        return self._my['command']

    @property
    def enabled(self) -> bool:
        """Get/Set a value indicating whether the MenuItem is enabled."""
        return self._my['enabled']

    @enabled.setter
    def enabled(self, enabled: bool) -> None:
        """Get/Set a value indicating whether the MenuItem is enabled."""
        if self._my['type'] != EntryType.SEPARATOR:
            self._my['enabled'] = enabled
            if self.owner is not None and self._my['index'] >= 0:
                enabled &= bool(self._my['active'])
                state = tk.NORMAL if enabled else tk.DISABLED
                self.owner.entryconfigure(self._my['index'], state=state)
        self.image = self._my['image']
        self.text = self._my['text']

    @property
    def entry_type(self) -> EntryType:
        """The entry type identifier for the MenuItem."""
        return self._my['type']

    @property
    def image(self) -> Union[PhotoImage, tk.PhotoImage, None]:
        """Get/Set the image associated with the MenuItem."""
        return self._my['image']

    @image.setter
    def image(self, image: Union[PhotoImage, tk.PhotoImage, None]) -> None:
        """Get/Set the image associated with the MenuItem."""
        config = _update_image(image, self._my)
        if self._my['type'] == EntryType.STANDARD:
            if self.owner is not None and self._my['index'] >= 0:
                self.owner.entryconfigure(self._my['index'], config)

    @property
    def shortcut(self) -> str:
        """Get/Set the MenuItem's shortcut key character value."""
        return '' if not self._my['key'] else self._my['key'][-1]

    @shortcut.setter
    def shortcut(self, key: str) -> None:
        """Get/Set the MenuItem's shortcut key character value."""
        modifier, name = ('Command', 'Cmd') if MAC_OS else ('Control', 'Ctrl')
        key = str(key).strip('< >').replace(' ', '')
        if key and key[-1].isalnum() and not self._my['accel']:
            self._my['shortcut'] = f'<{modifier}-Key-{key[-1].lower()}>'
            self._my['key'] = f'{name}+{key[-1].upper()}'
            self.text = self._my['text']

    @property
    def text(self) -> str:
        """Get/Set the text label string for the MenuItem."""
        return self._my['text']

    @text.setter
    def text(self, text: str) -> None:
        """Get/Set the text label string for the MenuItem."""
        self._my['text'] = text
        if (
            (self.owner is not None and self.parent is not None)
            and self._my['type'] != EntryType.SEPARATOR
            and self._my['index'] >= 0
        ):
            label, index = _get_shortcut(self, text)
            config: Dict[str, Any] = {'label': label, 'underline': index}
            if self._my['event'] or self._my['shortcut']:
                event, accel = self._my['shortcut'], self._my['key']
                if self._my['event']:
                    event, accel = self._my['event'], self._my['accel']
                    if self._my['shortcut']:
                        self.owner.unbind_all(self._my['shortcut'])
                        self._my['shortcut'] = self._my['key'] = ''
                self.owner.unbind_all(event)
                if self.enabled and self.visible:
                    self.owner.bind_all(event, self._event_handler)
                if platform.system() == 'Linux':
                    accel = f' {accel}  '
                config.update({'accelerator': accel})
            self.owner.entryconfigure(self._my['index'], config)

    @property
    def variable(self) -> tk.IntVar:
        """The control variable associated with the MenuItem."""
        return self._my['variable']

    @property
    def value(self) -> int:
        """The control value assigned to the MenuItem."""
        return self._my['value']

    @property
    def visible(self) -> bool:
        """Get/Set a value indicating whether the MenuItem is visible."""
        return self._my['visible'] and self._my['active']

    @visible.setter
    def visible(self, visible: bool) -> None:
        """Get/Set a value indicating whether the MenuItem is visible."""
        if visible is not self._my['visible']:
            self._my['visible'] = visible
            self.text = self._my['text']
            if self.parent is not None:
                self.parent.update_display()

    def copy(self) -> 'MenuItem':
        """Create and return a deep copy of the MenuItem."""
        config_info = ConfigInfo(self.entry_type, self.variable, self.value)
        menu_item = MenuItem(self.text, self.command, self.image, config_info)
        menu_item.shortcut = self.shortcut
        if self._my['event']:
            menu_item.set_custom_shortcut(self._my['event'], self._my['accel'])
        return menu_item

    def set_custom_shortcut(self, sequence: str, accelerator: str) -> None:
        r"""Set a custom, user-defined shortcut for the MenuItem.

        Parameters
        ----------
        sequence : str
            The custom event sequence string ( e.g. '\<Control-Shift-A\>' )
        accelerator : str
            The custom accelerator description ( e.g. 'Ctrl+Shift+A' )
        """
        sequence = sequence.strip('< >').replace(' ', '').replace('+', '-')
        accelerator = accelerator.strip().replace(' ', '').replace('-', '+')
        self._my['event'], self._my['accel'] = f'<{sequence}>', accelerator
        self.text = self._my['text']

    def update_active(self, active: bool) -> None:
        """Update the active flag."""
        self._my['active'] = active
        self.enabled = self._my['enabled']

    def update_position(self, position: int) -> None:
        """Update the position value of the MenuItem in the displayed Menu."""
        self._my['index'] = position
        self.enabled = self._my['enabled']

    def _event_handler(self, event: tk.Event) -> None:
        """Map the MenuItem event handler to the shortcut key."""
        if self._my['type'] == EntryType.CHECKBUTTON:
            value = 0 if self._my['variable'].get() != 0 else 1
            self._my['variable'].set(value)
        elif self._my['type'] == EntryType.RADIOBUTTON:
            self._my['variable'].set(self._my['value'])
        if self._my['command'] is not None and event.time >= 0:
            self._my['command']()


class MainMenu:
    """A class that displays a menu bar across the top of a window."""

    def __init__(self, parent: Any) -> None:
        """Construct and initialize the MainMenu.

        Parameters
        ----------
        parent : Any
            The application window displaying the MainMenu
        """
        top_level = parent.winfo_toplevel()
        self._top_menu = tk.Menu(top_level)
        top_level['menu'] = self._top_menu
        self._entry_list: List[Menu] = []
        self._display_count = 0
        self._enabled = True
        self._update = True

    @property
    def count(self) -> int:
        """The total number of items in the MainMenu."""
        return len(self._entry_list)

    @property
    def enabled(self) -> bool:
        """Get/Set a value indicating whether the MainMenu is enabled."""
        return self._enabled

    @enabled.setter
    def enabled(self, enabled: bool) -> None:
        """Get/Set a value indicating whether the MainMenu is enabled."""
        if enabled != self._enabled:
            self._enabled = enabled
            for entry in self._entry_list:
                entry.update_active(enabled)

    def begin_update(self) -> None:
        """Prevent screen redraws when updating the items in the MainMenu."""
        self._update = False

    def end_update(self) -> None:
        """Enable the screen to display the items in the MainMenu."""
        self._update = True
        self.update_display()

    def add(self, menu: Menu) -> None:
        """Add a previously created Menu to the end of the MainMenu.

        Parameters
        ----------
        menu : Menu
            The previously created Menu
        """
        self._insert(self.count, menu)

    def add_menu(self, text: str) -> Menu:
        """Create and add a Menu to the end of the MainMenu.

        Parameters
        ----------
        text : str
            The text label string for the Menu

        Returns
        -------
        Menu
            The newly created Menu
        """
        return self._insert(self.count, Menu(text))

    def add_range(self, menus: List[Menu]) -> None:
        """Add a list of previously created Menus to the MainMenu.

        Parameters
        ----------
        menus : list[Menu]
            The list of previously created Menus
        """
        update = self._update
        self.begin_update()
        for entry in menus:
            self.add(entry)
        if update:
            self.end_update()

    def insert(self, index: int, menu: Menu) -> None:
        """Insert a previously created Menu at the index location.

        Parameters
        ----------
        index : int
            The Menu's location within the MainMenu
        menu : Menu
            The previously created Menu
        """
        self._insert(index, menu)

    def insert_menu(self, index: int, text: str) -> Menu:
        """Create and insert a Menu at the index location.

        Parameters
        ----------
        index : int
            The newly created Menu's location within the MainMenu
        text : str
            The text label string for the Menu

        Returns
        -------
        Menu
            The newly created Menu
        """
        return self._insert(index, Menu(text))

    def index_of(self, menu: Menu) -> int:
        """Report the index value of the specified Menu in the MainMenu.

        Parameters
        ----------
        menu : Menu
            The specified Menu in the MainMenu

        Returns
        -------
        int
            The zero-based index value if found, -1 otherwise.
        """
        index = -1
        if menu in self._entry_list:
            index = self._entry_list.index(menu)
        return index

    def remove(self, menu: Menu) -> None:
        """Remove the specified Menu from the MainMenu.

        Parameters
        ----------
        menu : Menu
            The specified Menu
        """
        self.remove_at(self.index_of(menu))

    def remove_at(self, index: int) -> None:
        """Remove a Menu from the MainMenu at the specified index.

        Parameters
        ----------
        index : int
            The specified Menu's location within the MainMenu
        """
        if 0 <= index < self.count:
            self._entry_list[index].owner = None
            self._entry_list[index].parent = None
            self._top_menu.delete(index + 1)
            self._entry_list.pop(index)
            for i in range(index, self.count):
                self._entry_list[i].update_position(i + 1)

    def update_display(self):
        """Update the display of visible items in the MainMenu."""
        if self._update:
            if self._display_count > 0:
                self._top_menu.delete(1, self._display_count)
            self._display_count = 0
            for entry in self._entry_list:
                if entry.visible:
                    entry.owner = self._top_menu
                    self._top_menu.add_cascade(menu=entry.menu)
                    entry.update_position(self._display_count + 1)
                    self._display_count += 1
                else:
                    entry.update_position(-1)

    def _insert(self, index: int, entry: Menu) -> Menu:
        """Insert the entry at the specified index."""
        if not isinstance(entry, ContextMenu):
            entry.parent = self
            if index >= self.count:
                self._entry_list.append(entry)
            else:
                self._entry_list.insert(max(0, index), entry)
            self.update_display()
        else:
            warn('Cannot add a ContextMenu to the MainMenu!', stacklevel=3)
        return entry


class ContextMenu(Menu):
    """A class used to represent a pop-up context menu."""

    def __init__(self):
        """Construct and initialize a ContextMenu."""
        super().__init__('')

    def copy(self) -> 'ContextMenu':
        """Create a deep copy of this ContextMenu."""
        copy = ContextMenu()
        copy.begin_update()
        for entry in self._my['entry_list']:
            copy.add(entry.copy())
        copy.end_update()
        return copy

    def display(self, location: Tuple[int, int]) -> None:
        """Display the ContextMenu at the specified screen location.

        Parameters
        ----------
        location : tuple[int, int]
            The specified screen location (x, y) in pixels
        """
        try:
            self.menu.tk_popup(location[0], location[1], False)
        finally:
            self.menu.grab_release()


class MenuButton(tk.Menubutton):
    """A class used to represent a drop-down menu selection button."""

    def __init__(
        self,
        parent: Any,
        text: str = '',
        width: int = -1,
        image: Union[PhotoImage, tk.PhotoImage, None] = None,
    ):
        """Construct and initialize the MenuButton.

        Parameters
        ----------
        parent : Any
            The parent widget of the MenuButton
        text : Text
            The text label string for the MenuButton
        width : int
            The character width of the MenuButton (default is 'auto-size')
        image : PhotoImage | tk.PhotoImage | None
            The optional MenuButton image (default is None)
        """
        border = 1 if platform.system() == 'Linux' else 2
        super().__init__(parent, bd=border, relief='raised')
        self._menu = Menu('')
        self._menu.owner = self
        self.config(menu=self._menu.menu)
        self._my: Dict[str, Any] = {'text': text, 'width': width}
        self._my.update({'image': image, 'grayed': _grayed_image(image)})
        self.text = text
        self.enabled = True

    @property
    def enabled(self) -> bool:
        """Get/Set a value indicating whether the MenuButton is enabled."""
        return self['state'] != tk.DISABLED

    @enabled.setter
    def enabled(self, enabled: bool) -> None:
        """Get/Set a value indicating whether the MenuButton is enabled."""
        self['state'] = tk.NORMAL if enabled else tk.DISABLED
        if self._my['image'] is None:
            self.config(compound='none', width=self._my['width'])
        else:
            image = self._my['image'] if enabled else self._my['grayed']
            width = 9 if MAC_OS else (8 if platform.system() == 'Linux' else 6)
            width = max(-1, width * self._my['width'])
            self.config(compound='left', image=image, width=width)
        for entry in self._menu:
            entry.update_active(enabled)

    @property
    def image(self) -> Union[PhotoImage, tk.PhotoImage, None]:
        """Get/Set the image associated with the MenuItem."""
        return self._my['image']

    @image.setter
    def image(self, image: Union[PhotoImage, tk.PhotoImage, None]) -> None:
        """Get/Set the image associated with the MenuItem."""
        self._my['image'] = image
        self._my['grayed'] = _grayed_image(image)
        self.enabled = self.enabled

    @property
    def menu(self) -> Menu:
        """Get the MenuButton's drop down menu."""
        return self._menu

    @property
    def text(self) -> str:
        """Get/Set the text label string for the MenuButton."""
        return self['text']

    @text.setter
    def text(self, text: str) -> None:
        """Get/Set the text label string for the MenuButton."""
        self._my['text'] = text
        if MAC_OS and self._my['image'] is not None:
            text = '  ' + text
        self.config(text=f' {text} ', justify='center')


def _get_shortcut(owner: Union[MenuItem, Menu], text: str) -> Tuple[str, int]:
    """Get the shortcut information from the text label."""
    parent = owner.parent
    while isinstance(parent, Menu):
        parent = parent.parent
    label = ' ' + text.lstrip()
    index = max(1, label.find('&')) if isinstance(parent, MainMenu) else -1
    return label.replace('&', ''), index


def _grayed_image(image: Any) -> Any:
    """Create a grayed (disabled) version of the image for macOS systems."""
    grayed_image = image
    if MAC_OS and image is not None:
        pil_image = ImageTk.getimage(image).convert('RGBA')
        red, green, blue, alpha = pil_image.split()
        grayed_alpha = alpha.point(lambda x: x * 0.35)
        grayed = Image.merge('RGBA', (red, green, blue, grayed_alpha))
        grayed_image = PhotoImage(grayed)
    return grayed_image


def _update_image(image: Any, params: Dict[str, Any]) -> Dict[str, Any]:
    """Update the image parameter and return the display configuration."""
    size = (16, 16) if image is None else (image.width(), image.height())
    blank_image = None if MAC_OS else PhotoImage(Image.new('RGBA', size, 0))
    params['image'] = blank_image if image is None else image
    params['grayed'] = _grayed_image(params['image'])
    config: Dict[str, Any] = {'compound': 'none'}
    if params['image'] is not None:
        enabled = params['enabled'] and params['active']
        display = params['image'] if enabled else params['grayed']
        config = {'compound': 'left', 'image': display}
    return config
