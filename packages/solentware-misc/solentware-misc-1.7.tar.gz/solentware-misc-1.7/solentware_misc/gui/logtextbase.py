# logtextbase.py
# Copyright 2023 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Provide classes which run tasks in a background thread.

The tasks are run one at a time and progress is reported to a visible
transaction log.

"""

import datetime
import tkinter
import tkinter.font

from .textreadonly import TextReadonly


class LogTextBase(TextReadonly):
    """A progress report log."""

    def __init__(self, master=None, **kargs):
        """Add a vertical scrollbar to a read-only tkinter.Text widget.

        master - parent widget for log widget.
        **kargs - passed to superclass as **kargs argument.

        """
        super().__init__(master=master, **kargs)
        self.set_readonly_bindings()
        scrollbar = tkinter.Scrollbar(
            master, orient=tkinter.VERTICAL, command=self.yview
        )
        self.configure(yscrollcommand=scrollbar.set)
        self.tag_configure(
            "margin",
            lmargin2=tkinter.font.nametofont(self.cget("font")).measure(
                "2010-05-23 10:20:57  "
            ),
        )
        scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=tkinter.TRUE)
        self.tagstart = "1.0"

    def append_bytestring(self, text, timestamp=True):
        """Append text to the log widget with timestamp by default.

        text - a bytestring.
        timestamp - if True the entry is timestamped.
        """
        if timestamp:
            day, time = (
                datetime.datetime.isoformat(datetime.datetime.today())
                .encode("utf8")
                .split(b"T")
            )
            time = time.split(b".")[0]
            self.insert(
                tkinter.END, b"".join((day, b" ", time, b"  ", text, b"\n"))
            )
        else:
            self.insert(
                tkinter.END, b"".join((b"                     ", text, b"\n"))
            )
        try:
            self.tag_add("margin", self.tagstart, tkinter.END)
        except:
            self.tag_add("margin", "1.0", tkinter.END)
        self.tagstart = self.index(tkinter.END)
        self.see(tkinter.END)

    def append_text(self, text, timestamp=True):
        """Append text to the log widget with timestamp by default.

        text - a str.
        timestamp - if True the entry is timestamped.
        """
        if timestamp:
            day, time = datetime.datetime.isoformat(
                datetime.datetime.today()
            ).split("T")
            time = time.split(".")[0]
            self.insert(
                tkinter.END, "".join((day, " ", time, "  ", text, "\n"))
            )
        else:
            self.insert(
                tkinter.END, "".join(("                     ", text, "\n"))
            )
        try:
            self.tag_add("margin", self.tagstart, tkinter.END)
        except:
            self.tag_add("margin", "1.0", tkinter.END)
        self.tagstart = self.index(tkinter.END)
        self.see(tkinter.END)

    def append_bytestring_only(self, text):
        """Append text to the log widget without timestamp.

        text - a bytestring.
        """
        self.append_bytestring(text, timestamp=False)

    def append_text_only(self, text):
        """Append text to the log widget without timestamp.

        text - a str.
        """
        self.append_text(text, timestamp=False)

    def append_raw_bytestring(self, text):
        """Append text as provided to the log widget.

        text - a bytestring.
        """
        # Just call self.append_raw_text because no 'b"".join()'s needed.
        self.append_raw_text(text)

    def append_raw_text(self, text):
        """Append text as provided to the log widget.

        Intended for cases where timestamp and trailing newline have been
        generated when placing the text on a queue for later processing
        (usually milliseconds later but maybe not).

        """
        self.insert(tkinter.END, text)
        try:
            self.tag_add("margin", self.tagstart, tkinter.END)
        except:
            self.tag_add("margin", "1.0", tkinter.END)
        self.tagstart = self.index(tkinter.END)
        self.see(tkinter.END)
