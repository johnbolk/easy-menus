"""simple.py - A Simple Example with a Shortcut and an Image."""

from tkinter import Tk, PhotoImage
from menus import MainMenu

root = Tk()


def on_exit():
    """Handle the 'Exit' selection."""
    root.destroy()


# Create and Populate the Top Menu Bar
menu_bar = MainMenu(root)
file_menu = menu_bar.add_menu('File')

exit_icon = PhotoImage(file='image_folder/exit.png')
file_menu.add_item('E&xit', on_exit, exit_icon).shortcut = 'w'

root.mainloop()
