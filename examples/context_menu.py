"""context_menu.py - A Simple ContextMenu Example."""

from tkinter import Tk, Label
from menus import ContextMenu

root = Tk()


def on_context_event():
    """Handle the ContextMenu events."""
    print('Context Menu Event')


context_menu = ContextMenu()
context_menu.add_item('Copy', on_context_event)
context_menu.add_item('Save As ...', on_context_event)
context_menu.add_item('Delete Text', on_context_event)

label = Label(root, text=' ContextMenu Example  ', relief='groove')
label.grid(padx=40, pady=40)


def on_right_button(e):
    """Display the ContextMenu at the mouse position."""
    position = (label.winfo_rootx() + e.x, label.winfo_rooty() + e.y)
    context_menu.display(position)


label.bind('<Button-3>', on_right_button)  # use '<Button-2>' on macOS

root.mainloop()
