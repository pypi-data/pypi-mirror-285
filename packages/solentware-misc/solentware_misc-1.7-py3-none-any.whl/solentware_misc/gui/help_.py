# help_.py
# Copyright 2012 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Provide functions to create widgets which display help text files."""

import tkinter
from os.path import isfile, basename, splitext

from . import textreadonly


def help_text(title, help_text_module, name, encoding="utf-8"):
    """Return text from the help text file for title."""
    for htf in help_text_module._textfile[title]:
        if name is not None:
            if name != splitext(basename(htf))[0]:
                continue
        if isfile(htf):
            try:
                file = open(htf, encoding=encoding)
                try:
                    text = file.read()
                except:
                    text = " ".join(("Read help", str(title), "failed"))
                file.close()
                return text
            except:
                break
    return " ".join((str(title), "help not found"))


def help_widget(master, title, help_text_module, hfname=None):
    """Build a Toplevel widget to display a help text document."""
    toplevel = tkinter.Toplevel(master=master)
    toplevel.wm_title(title)
    help_tro = textreadonly.TextReadonly(
        master=toplevel, cnf=dict(wrap=tkinter.WORD, tabstyle="tabular")
    )
    scrollbar = tkinter.Scrollbar(
        master=toplevel, orient=tkinter.VERTICAL, command=help_tro.yview
    )
    help_tro.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
    help_tro.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=tkinter.TRUE)
    help_tro.set_readonly_bindings()
    help_tro.insert(tkinter.END, help_text(title, help_text_module, hfname))
    help_tro.focus_set()
