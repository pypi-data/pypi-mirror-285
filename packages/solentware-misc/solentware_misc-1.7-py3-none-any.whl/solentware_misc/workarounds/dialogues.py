# dialogues.py
# Copyright 2009 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Wrap some tkinter functions for Python2.6 problem workaround.

This module is redundant because the problem seen for a while with Python
2.6 no longer matters.  It exposes the functions it wrapped for compatibility.
The module will be removed without notice at a future release.

From when the module did something:

This module wraps tkinter.messagebox and tkinter.filedialog functions to
catch tkinter.TclError exceptions raised for grab errors occurring after
the application has been destroyed.

The wrappers for the tkinter.messagebox functions call the _show method,
bypassing the wrapped function, to avoid a problem seen on Python2.6 where
the wrapped function returns a booleanString causing comparison with
tkinter.YES, a str, to be False in all circumstances.
"""

# At 2009-08-01 calling tkMessageBox.askyesno and so on does not work
# on Python2.6: s == YES compares booleanString with str
# but calling _show works (as it does in tkMessageBox.py test stuff).
# tkFileDialog functions seem ok

from tkinter.messagebox import (
    showinfo,
    showwarning,
    showerror,
    askquestion,
    askokcancel,
    askyesno,
    askyesnocancel,
    askretrycancel,
)
from tkinter.filedialog import (
    askopenfilename,
    asksaveasfilename,
    askopenfilenames,
    askopenfile,
    askopenfiles,
    asksaveasfile,
    askdirectory,
)

BAD_WINDOW = 'bad window path name ".!'
DESTROYED_ERROR = (
    "".join(("can't invoke ", '"')),
    '" command:  application has been destroyed',
)
GRAB_ERROR = "grab".join(DESTROYED_ERROR)
FOCUS_ERROR = "focus".join(DESTROYED_ERROR)
