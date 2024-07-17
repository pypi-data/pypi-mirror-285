# workarounds.py
# Copyright 2011 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Tkinter function workarounds at Tcl/Tk 8.5 at Python2.6 or Python2.7.

Both grid_configure_query and text_count became redundant at an unknown
point after the problems they fix were spotted.

It is assumed the genuine functions work at Python 2.5 with Tcl/Tk 8.4, if
the feature is supported, and changes in Tcl/Tk 8.5 raise the problem.

"""
import os
import sys


def grid_configure_query(widget, command, index, option=None):
    """Hack of Tkinter.py Misc method _grid_configure for option queries.

    widget.grid_rowconfigure(1, 'pad') and similar do not work at Python 2.6
    because the self.tk.call(...) for the query, in _grid_configure, returns
    an int (maybe a double for width?) rather than a str; at least when
    Tk/Tcl 8.5 is used.

    This function can handle 'weight', 'pad', 'minsize', 'uniform', and
    'all', option queries for columnconfigure and rowconfigure commands.

    Queries on 'uniform' work in the genuine function.

    """
    if option is None:
        res = widget.tk.call("grid", command, widget._w, index)
        words = widget.tk.splitlist(res)
        dict_ = {}
        for i in range(0, len(words), 2):
            key = words[i][1:]
            value = words[i + 1]
            # perhaps just testing value == '' is enough.
            if key == "uniform":
                if not value:
                    value = None
            elif value == "":
                value = None
            dict_[key] = value
        return dict_
    # should precisely one leading '-' and one trailing '_' be adjusted.
    res = widget.tk.call(
        (
            "grid",
            command,
            widget._w,
            index,
            "".join(("-", option.rstrip("_").lstrip("-"))),
        )
    )
    # perhaps just testing res == '' is enough.
    if option == "uniform":
        if not res:
            res = None
    elif res == "":
        res = None
    return res


def text_count(widget, index1, index2, *options):
    """Hack Text count command. Return integer, or tuple if len(options) > 1.

    Tkinter does not provide a wrapper for the Tk Text widget count command
    at Python 2.7.1

    widget is a Tkinter Text widget.
    index1 and index2 are Indicies as specified in TkCmd documentation.
    options must be a tuple of zero or more of option values.  If no options
    are given the Tk default option is used.  If less than two options are
    given an integer is returned.  Otherwise a tuple of integers is returned
    (in the order specified in TkCmd documentation).

    See text manual page in TkCmd documentation for valid option values and
    index specification.

    Example:
    chars, lines = text_count(widget, start, end, '-chars', '-lines')

    """
    return widget.tk.call((widget._w, "count") + options + (index1, index2))


def text_get_displaychars(widget, index1, index2=None):
    """Hack Text get_displaychars to return non-elided characters in range.

    Tkinter does not support the 'displaychars' option at Python 3.9 but the
    underlying tk.Text.get() does support it (as stated in the Tcl/Tk text
    manual page).

    widget is a Tkinter Text widget.
    index1 and index2 are Indicies as specified in TkCmd documentation.
    Multiple text ranges are not supported.

    See text manual page in TkCmd documentation for details.

    Example:
    text_get_displaychars(widget, start, end)

    """
    return widget.tk.call(widget._w, "get", "-displaychars", index1, index2)


def text_delete_ranges(widget, *ranges):
    """Hack Text delete to delete multiple ranges of characters.

    Tkinter does not support deletion of multiple ranges at Python 3.9 but
    the underlying tk.Text.delete() does support it (as stated in the Tcl/Tk
    text manual page).

    widget is a Tkinter Text widget.
    ranges is a tuple of Indicies as specified in TkCmd documentation.

    See text manual page in TkCmd documentation for details.

    Example:
    text_delete_ranges(widget, start, end)

    """
    return widget.tk.call(widget._w, "delete", *ranges)


def winfo_pathname(widget, error):
    """Hack winfo_pathname to cope with exception on Microsoft Windows.

    The problem is a '_tkinter.TclError: window id "<number>" doesn't exist
    in this application' exception in w.winfo_pathname(w.winfo_id()) calls
    on the amd64 architecture (64 bit Python in other words).

    The problem does not occur for 32 bit Python running on the amd64
    architecture and, if I remember correctly, on 32 bit Windows XP on
    the 32 bit (x86) architecture.

    From the description of winfo_id in "tcl.tk/man/tcl8.6/TkCrr" it is
    assumed the problem may also affect macOS systems.

    See winfo manual page in TkCmd documentation for details.

    widget is a Tkinter widget.
    error is the Exception raised in a tkinter.winfo_pathname() call.

    """
    if (
        sys.platform == "win32"
        and os.getenv("PROCESSOR_ARCHITECTURE") == "AMD64"
    ) or sys.platform == "darwin":
        name = widget.winfo_name()
        if name == ".":
            return name
        parent = widget.winfo_parent()
        if parent == ".":
            return parent + name
        return ".".join((parent, name))
    raise RuntimeError(
        " ".join((sys.platform, "winfo_pathname(id) call"))
    ) from error
