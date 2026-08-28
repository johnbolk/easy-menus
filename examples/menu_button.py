"""menu_button.py - A Simple MenuButton Example."""

from tkinter import Tk
from menus import MenuButton

root = Tk()

selections = MenuButton(root, 'Selections', 20)
selections.grid(padx=40, pady=40)
selections.menu.begin_update()
for i in range(1, 5):

    def on_select(index=i):
        """Handle the Selection events."""
        print(f'Selection Number {index}')

    selections.menu.add_item(f'Selection #{i}', on_select)
selections.menu.end_update()

root.mainloop()
