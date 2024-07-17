# textreadonly.py
# Copyright 2009 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Provide TextReadonly class which customizes tkinter.Text class.

tkinter.Text is exended with methods to suppress and restore the bindings
for editing, and functions to return a tkinter.Text widget, or a scrollable
version, with bindings to edit text removed.

"""

import tkinter

from solentware_bind.gui import bindings


# Is ExceptionHandler appropriate to this class - Tkinter.Text not wrapped.
# However the Bindings instance created in __init__() has ExceptionHandler
# available.
class TextReadonly(tkinter.Text):
    """Extend tkinter.Text with methods to suppress and restore editing."""

    def __init__(self, cnf=None, **kargs):
        """Provide a Bindings instance.

        tkinter.Text does not do super().__init__() so Bindings instance
        is not provided by TextReadonly(Bindings, ...)

        """
        if cnf is None:
            cnf = {}
        super().__init__(cnf=cnf, **kargs)
        self._bindings = bindings.Bindings()

    def set_readonly_bindings(self):
        """Set bindings to suppress editing actions."""
        set_readonly_bindings(self)

    def unset_readonly_bindings(self):
        """Unset bindings that suppress editing actions."""
        unset_readonly_bindings(self)


def make_text_readonly(cnf=None, **kargs):
    """Return Text widget with read only bindings.

    See tkinter.Text for arguments.
    """
    text = tkinter.Text(cnf={} if cnf is None else cnf, **kargs)
    set_readonly_bindings(text)
    return text


def make_scrolling_text_readonly(master=None, cnf=None, **kargs):
    """Return Frame and scrollable Text widget with read only bindings.

    master - passed to tkinter.Frame as master argument.
    cnf - passed to tkinter.Text as cnf argument, default {}.
    **kargs - passed to tkinter.Text as **kw argument.

    The Frame instance contains a Text instance and a vertical Scrollbar
    instance.
    """
    frame = tkinter.Frame(master=master)
    text = tkinter.Text(master=frame, cnf={} if cnf is None else cnf, **kargs)
    scrollbar = tkinter.Scrollbar(
        master=frame, orient=tkinter.VERTICAL, command=text.yview
    )
    text.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
    text.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=tkinter.TRUE)
    set_readonly_bindings(text)
    return frame, text


# Derived by looking at /usr/local/lib/tk8.5/text.tcl.
def set_readonly_bindings(widget):
    """Set bindings to suppress editing actions on tw.

    widget - a tkinter.Text instance.
    """
    # Never insert character in tw Text widget
    # Suppress editing events
    for sequence in _suppress_bindings:
        widget.bind(sequence=sequence, func=lambda event=None: "break")

    # All navigation sequences are handled by class bindings
    # No need to ignore Escape and KP_Enter here becuase KeyPress
    # never gets to class bindings
    for sequence in _use_class_bindings:
        widget.bind(sequence=sequence, func=lambda event=None: "continue")


# Derived by looking at /usr/local/lib/tk8.5/text.tcl.
def unset_readonly_bindings(widget):
    """Unset bindings that suppress editing actions on tw.

    widget - a tkinter.Text instance.
    """
    for sequences in (_suppress_bindings, _use_class_bindings):
        for sequence in sequences:
            widget.bind(sequence=sequence)


# The text bindings to be suppressed
_suppress_bindings = (
    "<KeyPress>",
    "<B1-Motion>",
    "<Double-1>",
    "<Triple-1>",
    "<Shift-1>",
    "<Double-Shift-1>",
    "<Triple-Shift-1>",
    "<B1-Leave>",
    "<B1-Enter>",
    "<ButtonRelease-1>",
    "<Control-1>",
    "<Shift-Left>",
    "<Shift-Right>",
    "<Shift-Up>",
    "<Shift-Down>",
    "<Shift-Home>",
    "<Shift-End>",
    "<Shift-Prior>",
    "<Shift-Next>",
    "<Shift-Control-Left>",
    "<Shift-Control-Right>",
    "<Shift-Control-Up>",
    "<Shift-Control-Down>",
    "<Control-Shift-Home>",
    "<Control-Shift-End>",
    "<Control-i>",
    "<Control-space>",
    "<Control-Shift-space>",
    "<Shift-Select>",
    "<Control-slash>",
    "<Control-backslash>",
    "<Control-d>",
    "<Control-k>",
    "<Control-o>",
    "<Control-t>",
    "<<Cut>>",
    "<<Copy>>",
    "<<Paste>>",
    "<<Clear>>",
    "<<PasteSelection>>",
    "<<Undo>>",
    "<<Redo>>",
    "<Meta-d>",
    "<Meta-BackSpace>",
    "<Meta-Delete>",
    "<Shift-Option-Left>",
    "<Shift-Option-Right>",
    "<Shift-Option-Up>",
    "<Shift-Option-Down>",
    "<Button-2>",
    "<B2-Motion>",
)

# The text bindings to be kept active
_use_class_bindings = (
    "<Control-KeyPress>",
    "<Shift-KeyPress>",
    "<Alt-KeyPress>",
    "<Meta-KeyPress>",
    "<Left>",
    "<Right>",
    "<Up>",
    "<Down>",
    "<Home>",
    "<End>",
    "<Prior>",
    "<Next>",
    "<Control-Left>",
    "<Control-Right>",
    "<Control-Up>",
    "<Control-Down>",
    "<Control-Home>",
    "<Control-End>",
    "<Control-Prior>",
    "<Control-Next>",
    "<Control-a>",
    "<Control-b>",
    "<Control-e>",
    "<Control-f>",
    "<Control-n>",
    "<Control-p>",
    "<Meta-b>",
    "<Meta-f>",
    "<Meta-less>",
    "<Meta-greater>",
)
