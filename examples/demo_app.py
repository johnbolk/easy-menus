"""demo_app.py - A demonstration application example."""

from tkinter import Tk, Frame, IntVar, filedialog, messagebox
import platform
from imagelist import ImageList
from menus import MainMenu, Menu, MenuItem, EntryType, ConfigInfo


class DemoForm(Frame):
    """The demonstration window."""

    def __init__(self, master: Tk, width: int, height: int):
        """Construct and initialize the demonstration window."""
        super().__init__(master, width=width, height=height)
        self.grid()
        self._master = master
        master.title('Demo Window')
        image_list = ImageList('image_folder', auto_load=True)

        # Create and Populate the Top Menu Bar
        menu_bar = MainMenu(self)
        menu_bar.begin_update()
        menu_bar.add(self._file_menu(image_list))
        menu_bar.add(self._edit_menu(image_list))
        menu_bar.add(self._view_menu())
        help_menu = menu_bar.add_menu('Help')
        about = help_menu.add_item('About', self._on_about)
        about.set_custom_shortcut('<F9>', 'F9')
        menu_bar.end_update()

    def _on_about(self):
        """Handle the 'About' selection."""
        self._console_print('Help_Menu - About')

    def _file_menu(self, images) -> Menu:
        """Construct the 'File' drop-down menu."""
        self._master.protocol('WM_DELETE_WINDOW', self._on_exit)
        if platform.system() == 'Darwin':  # macOS system
            self._master.createcommand('tk::mac::Quit', self._on_exit)
        exit_item = MenuItem('E&xit', self._on_exit, images['exit'])
        exit_item.set_custom_shortcut('<Control-q>', 'Ctrl+Q')

        menu = Menu('File')
        menu.begin_update()
        menu.add_item('Open', self._on_open, images['open']).shortcut = 'o'
        self._save_item = menu.add_item('Save', self._on_save, images['save'])
        self._save_item.shortcut = 's'
        self._save_item.enabled = False
        menu.add_separator()
        menu.add(exit_item)
        menu.end_update()
        return menu

    def _on_open(self):
        """Handle the 'Open' selection."""
        filename = filedialog.askopenfilename(title='Open a File')
        if filename:
            self._save_item.enabled = True
            self._console_print(filename)

    def _on_save(self):
        """Handle the 'Save' selection."""
        filename = filedialog.asksaveasfilename(title='Save a File')
        if filename:
            self._console_print(filename)

    def _on_exit(self):
        """Handle the 'Exit' selection."""
        if messagebox.askyesno('Exit', 'Do you wish to Exit the program?'):
            self._master.destroy()

    def _edit_menu(self, images) -> Menu:
        """Construct the 'Edit' drop-down menu."""
        self._paste_item = MenuItem('Paste', self._on_paste, images['paste'])
        self._paste_item.shortcut = 'v'
        self._paste_item.enabled = False

        menu = Menu('Edit')
        menu.begin_update()
        menu.add_item('Cu&t', self._on_cut, images['cut']).shortcut = 'x'
        menu.add_item('Copy', self._on_copy, images['copy']).shortcut = 'c'
        menu.add(self._paste_item)
        menu.add_separator()
        search_menu = menu.add_menu('Search', images['search'])
        search_menu.begin_update()
        search_menu.add_item('Find', self._on_find).shortcut = 'f'
        search_menu.add_item('Replace', self._on_replace).shortcut = 'r'
        search_menu.end_update()
        menu.end_update()
        return menu

    def _on_cut(self):
        """Handle the 'Cut' selection."""
        self._paste_item.enabled = True
        self._console_print('Edit_Menu - Cut')

    def _on_copy(self):
        """Handle the 'Copy' selection."""
        self._paste_item.enabled = True
        self._console_print('Edit_Menu - Copy')

    def _on_paste(self):
        """Handle the 'Paste' selection."""
        self._console_print('Edit_Menu - Paste')

    def _on_find(self):
        """Handle the 'Find' selection."""
        self._console_print('Edit_Menu - Search_Menu - Find')

    def _on_replace(self):
        """Handle the 'Replace' selection."""
        self._console_print('Edit_Menu - Search_Menu - Replace')

    def _view_menu(self) -> Menu:
        """Construct the 'View' drop-down menu."""
        menu = Menu('View')
        menu.begin_update()
        self._full_screen = menu.add_item(
            'Full Screen',
            self._on_full_screen,
            config=ConfigInfo(EntryType.CHECKBUTTON),
        )
        self._full_screen.shortcut = 't'  # Toggle the screen mode
        menu.add_separator()

        self._zoom_variable = IntVar(value=1)
        config = ConfigInfo(EntryType.RADIOBUTTON, self._zoom_variable)
        zoom_menu = menu.add_menu('Zoom')
        zoom_menu.begin_update()
        for value in (1, 2, 4, 8):
            config.value = value
            zoom_menu.add_item(f'&{value}00%', self._on_zoom, config=config)
        zoom_menu.end_update()
        menu.end_update()
        return menu

    def _on_full_screen(self):
        """Handle the 'Full Screen' toggle selection."""
        self._master.attributes('-fullscreen', self._full_screen.checked)

    def _on_zoom(self):
        """Handle the 'Zoom' selections."""
        self._console_print(f'View_Menu - Zoom {self._zoom_variable.get()}00%')

    @staticmethod
    def _console_print(message):
        """Print the message to the console."""
        print(f'*** {message} was Selected ***')


if __name__ == '__main__':
    main_form = DemoForm(Tk(), 400, 300)
    main_form.mainloop()
