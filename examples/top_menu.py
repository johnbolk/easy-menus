"""top_menu.py - A Top Menu Bar Example."""

from tkinter import Tk, PhotoImage, IntVar
from menus import MainMenu, EntryType, ConfigInfo

root = Tk()


def on_exit():
    """Handle the 'Exit' selection."""
    root.destroy()


# Create and Populate the Top Menu Bar
menu_bar = MainMenu(root)
menu_bar.begin_update()
file_menu = menu_bar.add_menu('File')
edit_menu = menu_bar.add_menu('Edit')
view_menu = menu_bar.add_menu('View')
help_menu = menu_bar.add_menu('Help')
menu_bar.end_update()


def on_open():
    """Handle the 'Open' selection."""
    print('File_Menu - Open')


def on_save():
    """Handle the 'Save' selection."""
    print('File_Menu - Save')


open_icon = PhotoImage(file='image_folder/open.png')
save_icon = PhotoImage(file='image_folder/save.png')
exit_icon = PhotoImage(file='image_folder/exit.png')

file_menu.begin_update()
file_menu.add_item('Open', on_open, open_icon).shortcut = 'o'
file_menu.add_item('Save', on_save, save_icon).shortcut = 's'
file_menu.add_separator()
file_menu.add_item('E&xit', on_exit, exit_icon).shortcut = 'w'
file_menu.end_update()


def on_cut():
    """Handle the 'Cut' selection."""
    print('Edit_Menu - Cut')


def on_copy():
    """Handle the 'Copy' selection."""
    print('Edit_Menu - Copy')


def on_paste():
    """Handle the 'Paste' selection."""
    print('Edit_Menu - Paste')


edit_menu.begin_update()
edit_menu.add_item('Cu&t', on_cut).shortcut = 'x'
edit_menu.add_item('Copy', on_copy).shortcut = 'c'
edit_menu.add_item('Paste', on_paste).shortcut = 'v'
edit_menu.end_update()

zoom_variable = IntVar(value=100)


def on_zoom():
    """Handle the 'Zoom' selections."""
    print(f'View_Menu - Zoom {zoom_variable.get()}%')


zoom_menu = view_menu.add_menu('Zoom')
zoom_menu.begin_update()
for value in (100, 200, 400):
    label = f'&{value}%'
    config = ConfigInfo(EntryType.RADIOBUTTON, zoom_variable, value)
    zoom_menu.add_item(label, on_zoom, config=config)
zoom_menu.end_update()


def on_about():
    """Handle the 'About' selection."""
    print('Help_Menu - About')


about = help_menu.add_item('About', on_about)
about.set_custom_shortcut('<Control-Shift-A>', 'Ctrl+Shift+A')

root.mainloop()
