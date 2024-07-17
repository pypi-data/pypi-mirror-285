# texttab.py
# Copyright 2009 Roger Marsh
# Licence: See LICENCE (BSD licence)

######
#
# Hacked <Escape><Tab> as I do not see how to make Alt-Shift-Tab work.
# (Later: what if monitor is on same PC that runs Python?)
#
######
"""Provide a subclass of tkinter.Text with <Escape><Tab> replacing Tab.

The intention is to avoid accidents where a Text widget is in the tab order
cycle along with Buttons and other widgets where the significance of Tab may
change from widget to widget.

I do not see how to make Alt-Shift-Tab work, which is why <Escape><Tab> got
the job.

"""

import tkinter

from solentware_bind.gui import bindings


# Is ExceptionHandler appropriate to this class - Tkinter.Text not wrapped.
# However the Bindings instance created in __init__() has ExceptionHandler
# available.
class TextTab(tkinter.Text):
    """Extend tkinter.Text with methods to replace and restore Tab bindings."""

    def __init__(self, cnf=None, **kargs):
        """Delegate to tkinter.Text and provide a Bindings instance.

        tkinter.Text does not do super().__init__() so Bindings instance
        is not provided by TextReadonly(Bindings, ...)

        """
        super().__init__(cnf={} if cnf is None else cnf, **kargs)
        self._bindings = bindings.Bindings()

    def set_tab_bindings(self):
        """Set bindings replacing Tab with <Escape><Tab>."""
        set_tab_bindings(self)

    def unset_tab_bindings(self):
        """Unset bindings replacing Tab with <Escape><Tab>."""
        unset_tab_bindings(self)


def make_text_tab(cnf=None, **kargs):
    """Return Text widget with <Escape><Tab> binding replacing Tab binding.

    See tkinter.Text for arguments.
    """
    text = tkinter.Text(cnf={} if cnf is None else cnf, **kargs)
    set_tab_bindings(text)
    return text


def set_tab_bindings(widget):
    """Set bindings to replace Tab with <Escape><Tab> on tw.

    widget - a tkinter.Text instance.

    """

    def insert_tab(event=None):
        # Hacked to use <Escape><Tab> instead of <Alt-Shift-Tab>
        if event.keysym == "Escape":
            widget.__time_escape = event.time
            return None
        if event.time - widget.__time_escape > 500:
            del widget.__time_escape
            return "break"
        # Let the Text (class) binding insert the Tab
        return "continue"

    for sequence in _suppress_bindings:
        widget.bind(sequence=sequence, func=lambda event=None: "break")
    for sequence in _use_class_bindings:
        widget.bind(sequence=sequence, func=lambda event=None: "continue")
    for sequence in _tab_bindings:
        widget.bind(sequence=sequence, func=insert_tab)


def unset_tab_bindings(widget):
    """Unset bindings that replace Tab with <Escape><Tab> on tw.

    widget - a tkinter.Text instance.

    """
    for sequences in (_suppress_bindings, _use_class_bindings, _tab_bindings):
        for sequence in sequences:
            widget.bind(sequence=sequence)


# The text (class) bindings to be suppressed
_suppress_bindings = (
    "<Tab>",
    "<Shift-Tab>",
)

# The text (class) bindings to be kept active
_use_class_bindings = ("<Control-Tab>",)

# The tab bindings specific to this widget
# Not seen how to make <Alt-Shift-Tab> work so hack <Escape><Tab>
_tab_bindings = (
    "<Escape>",
    "<Escape><Tab>",
)
