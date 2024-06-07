"""Class version of the ABQ Data Entry application"""

from datetime import datetime
from pathlib import Path
import csv
import tkinter as tk
from tkinter import ttk
from decimal import Decimal, InvalidOperation


# Text widget compatible with control variable
class BoundText(tk.Text):
    """A Text widget with a bound variable."""
    def __init__(self, *args, textvariable=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._variable = textvariable

        # if user provided a variable
        if self._variable:
            self.insert('1.0', self._variable.get())
            # update text widget when the variable is modified
            self._variable.trace_add('write', self._set_content)
            # bind a method to update variable when Text widget is modified
            # event only fires once
            self.bind('<<Modified>>', self._set_var)

    def _set_content(self, *_):
        """Set the text contents to the variable"""
        self.delete('1.0', tk.END)
        self.insert('1.0', self._variable.get())

    def _set_var(self, *_):
        """Set the variable to the text content."""
        if self.edit_modified():
            content = self.get('1.0', 'end-1chars')
            self._variable.set(content)
            # reset modified flag to enable constant modified event to be fired
            self.edit_modified(False)


# advanced LabelInput widget
"""
    - parent: parent widget
    - label: text passed to label
    - var: control variable e.g tk.StringVar()
    - input_class: ttk.Entry, ttk.Spinbox, ttk.Checkbutton etc
    - input_args: styling input widget (dictionary)
    - label_args: styling label text (dictionary)
"""
class LabelInput(tk.Frame):
    """A widget containing a label and input together."""
    def __init__(self, parent, label, var, input_class=ttk.Entry,
                 input_args=None, label_args=None, **kwargs):
        super().__init__(parent, **kwargs)
        input_args = input_args or {}
        label_args = label_args or {}
        self.variable = var
        # set control variable dictionary to reference self/object
        self.variable.label_widget = self

        # setting up the labels
        if input_class in (ttk.Checkbutton, ttk.Button):
            input_args['text'] = label
        else:
            self.label = ttk.Label(self, text=label, **label_args)
            self.label.grid(row=0, column=0, sticky=tk.W + tk.E)
        
        # setup input arguments so that the input's control variable
        # will be passed in with the correct argument name
        if input_class in (ttk.Checkbutton, ttk.Button, ttk.Radiobutton, ValidatedRadioGroup):
            input_args['variable'] = self.variable
        else:
            input_args['textvariable'] = self.variable

        # setup for Radiobutton
        # assuming that the values key holds the label names of each button
        if input_class == ttk.Radiobutton:
            self.input = tk.Frame(self)
            for val in input_args.pop('values', []):
                button = ttk.Radiobutton(self.input, value=val, text=val, **input_args)
                button.pack(side=tk.LEFT, ipadx=10, ipady=2, expand=True, fill='x')
        else:
            self.input = input_class(self, **input_args)

        self.input.grid(row=1, column=0, sticky=(tk.W + tk.E))
        self.columnconfigure(0, weight=1)

    def grid(self, sticky=(tk.W + tk.E), **kwargs):
        """Overrides the grid method to add default sticky values"""
        super().grid(sticky=sticky, **kwargs)


# Building the data entry form
class DataRecordForm(ttk.Frame):
    """Input form for the widgets."""

    def _add_frame(self, label, cols=3):
        """Add a LabelFrame to the form."""
        frame = ttk.LabelFrame(self, text=label)
        frame.grid(sticky=tk.W + tk.E)
        for i in range(cols):
            frame.columnconfigure(i, weight=1)

        return frame

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # dictionary to hold all the variable objects
        self._vars = {
            'Date': tk.StringVar(),
            'Time': tk.StringVar(),
            'Technician': tk.StringVar(),
            'Lab': tk.StringVar(),
            'Plot': tk.IntVar(),
            'Seed Sample': tk.StringVar(),
            'Humidity': tk.DoubleVar(),
            'Light': tk.DoubleVar(),
            'Temperature': tk.DoubleVar(),
            'Equipment Fault': tk.BooleanVar(),
            'Plants': tk.IntVar(),
            'Blossoms': tk.IntVar(),
            'Fruit': tk.IntVar(),
            'Min Height': tk.DoubleVar(),
            'Max Height': tk.DoubleVar(),
            'Med Height': tk.DoubleVar(),
            'Notes': tk.StringVar()
        }

        # building the Record Information section
        # creating the record information frame
        r_info = self._add_frame('Record Information')

        LabelInput(r_info, 'Date', var=self._vars['Date'], input_class=DateEntry
            ).grid(row=0, column=0)

        LabelInput(r_info,
                   'Time',
                   input_class=ValidatedCombobox,
                   var=self._vars['Time'],
                   input_args={'values': ["8:00", "12:00", "16:00", "20:00"]}
                   ).grid(row=0, column=1)
        
        LabelInput(r_info,
                   'Technician',
                   var=self._vars['Technician'],
                   input_class=RequiredEntry
                   ).grid(row=0, column=2)
        
        LabelInput(r_info,
                   'Lab',
                   input_class=ValidatedRadioGroup,
                   var=self._vars['Lab'],
                   input_args={'values': ["A", "B", "C"]}
                   ).grid(row=1, column=0)
        
        LabelInput(r_info,
                   'Plot',
                   input_class=ValidatedCombobox,
                   var=self._vars['Plot'],
                   input_args={'values': list(range(1, 21))}
                   ).grid(row=1, column=1)
        
        LabelInput(r_info,
                   'Seed Sample',
                   var=self._vars['Seed Sample'],
                   input_class=RequiredEntry).grid(row=1, column=2)
        
        # building the Environmental Data section
        e_info = self._add_frame('Environmental Data')

        LabelInput(e_info, "Humidity (g/m³)",
                   input_class=ValidatedSpinbox, 
                   var=self._vars['Humidity'],
                   input_args={"from_": 0.5, "to": 52.0, "increment": .01}
                   ).grid(row=0, column=0)
        
        LabelInput(e_info, "Light (klx)",
                   input_class=ValidatedSpinbox,
                   var=self._vars['Light'],
                   input_args={"from_": 0, "to": 100, "increment": .01}
                   ).grid(row=0, column=1)
        
        LabelInput(e_info, "Temperature (°C)",
                   input_class=ValidatedSpinbox,
                   var=self._vars['Temperature'],
                   input_args={"from_": 4, "to": 40, "increment": .01}
                   ).grid(row=0, column=2)
        
        LabelInput(e_info, "Equipment Fault",
                   input_class=ttk.Checkbutton, 
                   var=self._vars['Equipment Fault']
                   ).grid(row=1, column=0, columnspan=3)
        
        # building the Plant Data section
        p_info = self._add_frame('Plant Data')

        LabelInput(p_info, "Plants", 
                   input_class=ValidatedSpinbox,
                   var=self._vars['Plants'],
                   input_args={"from_": 0, "to": 20}
                   ).grid(row=0, column=0)
        
        LabelInput(p_info, "Blossoms",
                   input_class=ValidatedSpinbox,
                   var=self._vars['Blossoms'],
                   input_args={"from_": 0, "to": 1000}
                   ).grid(row=0, column=1)
        
        LabelInput(p_info, "Fruit", 
                   input_class=ValidatedSpinbox,
                   var=self._vars['Fruit'],
                   input_args={"from_": 0, "to": 1000}
                   ).grid(row=0, column=2)
        
        LabelInput(p_info, "Min Height (cm)",
                   input_class=ttk.Spinbox,
                   var=self._vars['Min Height'],
                   input_args={"from_": 0, "to": 1000, "increment": .01}
                   ).grid(row=1, column=0)
        
        LabelInput(p_info, "Max Height (cm)",
                   input_class=ttk.Spinbox,
                   var=self._vars['Max Height'],
                   input_args={"from_": 0, "to": 1000, "increment": .01}
                   ).grid(row=1, column=1)
        
        LabelInput(p_info, "Median Height (cm)",
                   input_class=ttk.Spinbox,
                   var=self._vars['Med Height'],
                   input_args={"from_": 0, "to": 1000, "increment": .01}
                   ).grid(row=1, column=2)
        
        # widgets in the main window
        LabelInput(self, "Notes",
                   input_class=BoundText,
                   var=self._vars['Notes'],
                   input_args={'width': 75, 'height': 10}
                   ).grid(sticky=tk.W, row=3, column=0)
        
        # creating a buttons frame
        buttons = tk.Frame(self)
        buttons.grid(sticky=tk.W + tk.E, row=4)

        self.savebutton = ttk.Button(buttons, text="Save", command=self.master._on_save)
        self.savebutton.pack(side=tk.RIGHT)
        
        self.resetbutton = ttk.Button(buttons, text="Reset", command=self.reset)
        self.resetbutton.pack(side=tk.RIGHT)

    def reset(self):
        """Reset the form entries"""
        for var in self._vars.values():
            if isinstance(var, tk.BooleanVar):
                var.set(False)
            else:
                var.set('')

    def get(self):
        """Retrieve data from the form"""
        data = dict()
        fault = self._vars['Equipment Fault'].get()
        for key, variable in self._vars.items():
            if fault and key in ('Light', 'Humidity', 'Temperature'):
                data[key] = ''
            else:
                try:
                    data[key] = variable.get()
                except tk.TclError:
                    message = f"Error in field: {key}. Data is not saved!"
                    raise ValueError(message)
        return data


# mixin class to help create validated widget classes
class ValidatedMixin:
    """Adds a validation functionality to an input widget"""

    def __init__(self, *args, error_var=None, **kwargs):
        self.error = error_var or tk.StringVar()
        super().__init__(*args, **kwargs)

        vcmd = self.register(self._validate)
        invcmd = self.register(self._invalid)

        self.configure(
            validate='all',
            validatecommand=(vcmd, '%P', '%s', '%S', '%V', '%i', '%d'),
            invalidcommand=(invcmd, '%P', '%s', '%S', '%V', '%i', '%d')
        )

    def _toggle_error(self, on=False):
        self.configure(foreground=('red' if on else 'black'))

    def _validate(self, proposed, current, char, event, index, action):
        self.error.set('')
        self._toggle_error()
        valid = True
        # don't validate if widget is disabled
        state = str(self.configure('state')[-1])
        if state == tk.DISABLED:
            return valid
        
        if event == 'focusout':
            valid = self._focusout_validate(event=event)
        elif event == 'key':
            valid = self._key_validate(proposed=proposed,
                                       current=current,
                                       char=char,
                                       event=event,
                                       index=index,
                                       action=action)
        return valid
        
    # placeholders for the event-specific validation methods
    def _focusout_validate(self, **kwargs):
        return True
    
    def _key_validate(self, **kwargs):
        return True

    def _invalid(self, proposed, current, char, event, index, action):
        if event == 'focusout':
            self._focusout_invalid(event=event)
        elif event =='key':
            self._key_invalid(proposed=proposed,
                              current=current,
                              char=char,
                              event=event,
                              index=index,
                              action=action)
            
    def _focusout_invalid(self, **kwargs):
        """Handles invalid data on focus-out event"""
        self._toggle_error(True)

    def _key_invalid(self, **kwargs):
        """Handles invalid data on key event"""
        pass

    # manually execute focus-out validation on the widgets
    def trigger_focusout_validation(self):
        valid = self._validate('', '', '', 'focusout', '', '')
        if not valid:
            self._focusout_invalid(event='focusout')
        return valid
        

class RequiredEntry(ValidatedMixin, ttk.Entry):
    """An Entry that requires a value"""

    def _focusout_validate(self, event):
        valid = True
        if not self.get():
            valid = False
            self.error.set('A value is required')
        return valid


class DateEntry(ValidatedMixin, ttk.Entry):
    """An Entry that only accepts ISO Date strings"""

    def _key_validate(self, action, index, char, **kwargs):
        valid = True
        if action == '0':
            valid = True
        elif index in ('0', '1', '2', '3', '5', '6', '8', '9'):
            valid = char.isdigit()
        elif index in ('4', '7'):
            valid = (char == '-')
        else:
            valid = False
        return valid

    def _focusout_validate(self, event):
        valid = True
        if not self.get():
            self.error.set('A value is required')
            valid = False
        try:
            datetime.strptime(self.get(), '%Y-%m-%d')
        except ValueError:
            self.error.set('Invalid date')
            valid = False
        return valid


class ValidatedCombobox(ValidatedMixin, ttk.Combobox):
    """A combobox that only takes values from its string list"""

    def _key_validate(self, proposed, action, **kwargs):
        valid = True
        if action == '0':
            self.set('')
            return True
        # get values list
        values = self.cget('values')
        matching = [x for x in values if x.lower().startswith(proposed.lower())]
        if len(matching) == 0:
            valid = False
        elif len(matching) == 1:
            self.set(matching[0])
            self.icursor(tk.END)
            valid = False   # stops any further input to the widget, even appending the proposed keystroke
        return valid

    def _focusout_validate(self, event):
        valid = True
        if not self.get():
            valid = False
            self.error.set('A value is required')
        return valid


class ValidatedSpinbox(ValidatedMixin, ttk.Spinbox):
    def __init__(self, *args, from_='-Infinity', to='Infinity', **kwargs):
        super().__init__(*args, from_=from_, to=to, **kwargs)
        increment = Decimal(str(kwargs.get('increment', '1.0')))
        self.precision = increment.normalize().as_tuple().exponent

    def _key_validate(self, char, index, current, proposed, action, **kwargs):
        if action == '0':
            return True
        valid = True
        min_val = self.cget('from')
        max_val = self.cget('to')
        # flag variables
        no_negative = min_val >= 0
        no_decimal = self.precision >= 0

        # test if proposed keystroke is a valid character
        if any([
            (char not in '-1234567890.'),
            (char == '-' and (no_negative or index != '0')),
            (char == '.' and (no_decimal or '.' in current))]):
            return False
        
        # check for combination of '-.'
        if proposed in '-.':
            return True

        # at this stage proposed text meets the specifications of a Decimal
        proposed = Decimal(proposed)
        proposed_precision = proposed.as_tuple().exponent
        if any([(proposed > max_val), (proposed_precision < self.precision)]):
            return False
        return valid

    def _focusout_validate(self, **kwargs):
        valid = True
        value = self.get()
        min_val = self.cget('from')
        max_val = self.cget('to')

        try:
            d_value = Decimal(value)
        except InvalidOperation:
            self.error.set(f'Invalid number string: {value}')
            return False

        if d_value < min_val:
            self.error.set(f'Value is too low (min {min_val})')
            valid = False
        if d_value > max_val:
            self.error.set(f'Value is too high (max {max_val})')
            valid = False
        return valid


class ValidatedRadioGroup(ttk.Frame):
    """A validated radio button group"""

    def __init__(self, *args, variable=None, error_var=None, values=None, button_args=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.variable = variable or tk.StringVar()
        self.error = error_var or tk.StringVar()
        self.values = values or list()
        self.button_args = button_args or dict()

        for v in self.values:
            button = ttk.Radiobutton(self, value=v, text=v, variable=self.variable, **self.button_args)
            button.pack(side=tk.LEFT, ipadx=10, ipady=2, expand=True, fill='x')
        # validation callback when focus-out of frame
        self.bind('<FocusOut>', self.trigger_focusout_validation)

    def trigger_focusout_validation(self, *_):
        self.error.set('')
        if not self.variable.get():
            self.error.set('A value is required')


##############################################################

class Application(tk.Tk):
    """Application root window"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title('ABQ Data Entry Application')
        self.columnconfigure(0, weight=1)

        ttk.Label(self,
                  text='ABQ Data Entry Application',
                  font=("TkDefaultFont", 16)
                  ).grid(row=0)
        
        self.recordform = DataRecordForm(self)
        self.recordform.grid(row=1, padx=10, sticky=(tk.W + tk.E))

        self.status = tk.StringVar()
        ttk.Label(self, textvariable=self.status).grid(sticky=(tk.W + tk.E), row=2, padx=10)

        # hold number of records saved
        self._records_saved = 0

    def _on_save(self):
        """Handles the save button clicks"""

        datestring = datetime.today().strftime("%Y-%m-%d")
        filename = f"abq_data_record_{datestring}.csv"
        # if filename does not exist, newfile gets True
        newfile = not Path(filename).exists()

        try:
            data = self.recordform.get()
        except ValueError as e:
            self.status.set(e)
            return
        
        with open(filename, 'a', newline='') as fh:
            csvwriter = csv.DictWriter(fh, fieldnames=data.keys())
            if newfile:
                csvwriter.writeheader()
            csvwriter.writerow(data)

        self._records_saved += 1
        self.status.set(f"{self._records_saved} records saved this session.")
        self.recordform.reset()


# Make the application run
if __name__ == "__main__":
    app = Application()
    app.mainloop()




