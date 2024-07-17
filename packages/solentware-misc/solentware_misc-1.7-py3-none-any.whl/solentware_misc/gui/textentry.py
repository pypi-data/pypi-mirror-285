# textentry.py
# Copyright 2009 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Provide text entry dialogue class and a modal dialogue function."""

import tkinter

from solentware_bind.gui.bindings import Bindings

_TITLE = "title"
_TEXT = "text"


class TextEntry(Bindings):
    """Text entry dialogue widget."""

    def __init__(self, master=None, **options):
        """Initialise dialogue attributes.

        master - tkinter.Toplevel master argument when dialogue created.
        **options - tkinter.Entry **kw argument when dialogue created except
                    title which goes to tkinter.Toplevel and text which goes
                    to the tkinter.Label for the dialogue.

        **options is not put in super().__init__() call.

        """
        super().__init__()
        self.entered_text = None
        self.master = master
        self.options = options
        self.toplevel = None
        self.entry = None

    def _cancel(self):
        """Cancel dialogue."""
        self.toplevel.destroy()
        self.toplevel = None
        self.entry = None

    def get_text(self):
        """Return entered text or None if the dialogue was cancelled."""
        return self.entered_text

    def _ok(self):
        """Get text from dialogue then destroy dialogue."""
        self.entered_text = self.entry.get()
        self.toplevel.destroy()
        self.toplevel = None
        self.entry = None

    def show_modal(self):
        """Create and show the modal text entry dialogue.

        Remove text and title from options before passing rest to Entry.
        Title is passed to Toplevel.
        Text is passed to Label.

        """
        options = self.options

        if _TITLE in options:
            title = options[_TITLE]
            del options[_TITLE]
        else:
            title = "Text Entry"
        if _TEXT in options:
            text = options[_TEXT]
            del options[_TEXT]
        else:
            text = "Enter text"

        self.toplevel = toplevel = tkinter.Toplevel(master=self.master)
        toplevel.wm_title(title)
        label = tkinter.Label(master=toplevel, text=text)
        label.pack()
        self.entry = entry = tkinter.Entry(master=toplevel, **options)
        entry.pack(fill=tkinter.X, expand=tkinter.TRUE)
        buttonbar = tkinter.Frame(master=toplevel)
        buttonbar.pack(fill=tkinter.X, expand=tkinter.TRUE)
        cancel = tkinter.Button(
            master=buttonbar,
            text="Cancel",
            underline=0,
            command=self.try_command(self._cancel, buttonbar),
        )
        cancel.pack(expand=tkinter.TRUE, side=tkinter.LEFT)
        button = tkinter.Button(
            master=buttonbar,
            text="Ok",
            underline=0,
            command=self.try_command(self._ok, buttonbar),
        )
        button.pack(expand=tkinter.TRUE, side=tkinter.LEFT)
        entry.focus()
        toplevel.grab_set()
        toplevel.wait_window()

        return self.entered_text

    def __del__(self):
        """Destroy the dialogue if it exists."""
        if self.toplevel:
            self.toplevel.destroy()
        super().__del__()


def get_text_modal(master=None, **options):
    """Return text from modal TextEntry dialogue.

    master - passed to TextEntry as master argument.
    **options - passed to TextEntry as **options argument.
    """
    widget = TextEntry(master=master, **options)
    return widget.show_modal()
