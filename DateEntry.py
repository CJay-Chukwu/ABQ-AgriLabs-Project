import tkinter as tk
from tkinter import ttk
from datetime import datetime


class DateEntry(ttk.Entry):
    """An Entry for ISO-style dates (Year-month-day)"""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.configure(validate='all',
                       validatecommand=(self.register(self._validate), '%S', '%i', '%V', '%d'),
                       invalidcommand=(self.register(self._on_invalid), '%V')
                       )
        
        self.error = tk.StringVar()

    def _toggle_error(self, error=''):
        self.error.set(error)
        self.configure(foreground='red' if error else 'black')

    def _validate(self, char, index, event, action):

        # reset error state
        self._toggle_error()
        valid = True

        # ISO dates only need numbers and hyphens
        if event == 'key':      # if key is pressed
            if action == '0':   # if deleting(code is 0)
                valid = True
            elif index in ('0', '1', '2', '3', '5', '6', '8', '9'):
                # check int value if entries are string numbers
                valid = char.isdigit()
            elif index in ('4', '7'):
                valid = (char == '-')
            else:
                valid = False
        # checking correctness on focus-out
        elif event == 'focusout':
            try:
                datetime.strptime(self.get(), '%Y-%m-%d')
            except ValueError:
                valid = False
        
        return valid

    def _on_invalid(self, event):
        if event != 'key':
            self._toggle_error('Not a valid date')



# testing the DateEntry class
if __name__=='__main__':
    root = tk.Tk()
    entry = DateEntry(root)
    entry.pack()
    ttk.Label(textvariable=entry.error, foreground='red').pack()

    # another widget to select and unfocus the DateEntry widget
    ttk.Entry(root).pack()
    root.mainloop()
