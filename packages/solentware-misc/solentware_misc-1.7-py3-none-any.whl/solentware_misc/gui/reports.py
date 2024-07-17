# reports.py
# Copyright 2007 Roger Marsh
# Licence: See LICENCE (BSD licence)

# This has become a hack.
# There are three cases:
# 1. Running in main thread - do not use queue
# 2. Running in other thread - use queue
#
# Split module into two with identical interface:

"""Provide classes which define widgets for dialogues and reports.

These widgets can be used as alternatives to the Label widget used in
tkinter's equivalents.

"""

import tkinter
import tkinter.filedialog

from solentware_bind.gui.bindings import Bindings
from solentware_bind.gui.exceptionhandler import FOCUS_ERROR

from . import textreadonly


class AppSysReportBase(Bindings):
    """Base class for reports and dialogues."""

    def __init__(
        self,
        parent=None,
        title=None,
        save=None,
        ok=None,
        close=None,
        cnf=None,
        **kargs,
    ):
        """Create the report or dialogue widget.

        parent - report's parent object (note this is not a tkinter widget).
        title - report title text.
        save - command for Save button, default None.
        ok - command for Ok button, default None.
        close - command for Close button, default None.
        cnf - passed to tkinter.Text widget as cnf argument, default {}.
        **kargs - passed to tkinter.Text widget as **kargs argument.

        The parent argument is expected to have a get_widget() method, which
        returns a tkinter object useable as the master argument in Toplevel()
        calls for example.

        """
        super().__init__()
        self.parent = parent
        self._create_widget(
            parent, title, save, ok, close, {} if cnf is None else cnf, kargs
        )

    def get_button_definitions(self, **k):
        """Return an empty set of button definitions.

        Subclasses should override this method.

        """
        return ()

    def create_buttons(self, buttons, buttons_frame):
        """Create the report buttons.

        buttons - a list or tuple of button definitions.
        buttons_frame - the parent widget of the buttons.
        """
        buttonrow = buttons_frame.pack_info()["side"] in ("top", "bottom")
        for i, butdef in enumerate(buttons):
            button = tkinter.Button(
                master=buttons_frame,
                text=butdef[0],
                underline=butdef[3],
                command=self.try_command(butdef[4], buttons_frame),
            )
            if buttonrow:
                buttons_frame.grid_columnconfigure(i * 2, weight=1)
                button.grid_configure(column=i * 2 + 1, row=0)
            else:
                buttons_frame.grid_rowconfigure(i * 2, weight=1)
                button.grid_configure(row=i * 2 + 1, column=0)
        if buttonrow:
            buttons_frame.grid_columnconfigure(len(buttons * 2), weight=1)
        else:
            buttons_frame.grid_rowconfigure(len(buttons * 2), weight=1)

    def append(self, text):
        """Append text to report widget."""
        self.textreport.insert(tkinter.END, text)

    def _create_widget(self, parent, title, save, ok, close, cnf, kargs):
        """Create the report widget."""
        self._toplevel = tkinter.Toplevel(master=parent.get_widget())
        self._toplevel.wm_title(title)
        buttons_frame = tkinter.Frame(master=self._toplevel)
        buttons_frame.pack(side=tkinter.BOTTOM, fill=tkinter.X)
        butdefs = self.get_button_definitions(save=save, ok=ok, close=close)
        self.create_buttons(butdefs, buttons_frame)
        report_frame = tkinter.Frame(master=self._toplevel)
        self.textreport = textreadonly.make_text_readonly(
            master=report_frame, cnf=cnf, **kargs
        )
        self.textreport.focus_set()
        for button in butdefs:
            if button[3] >= 0:
                self.textreport.bind(
                    "".join(
                        ("<Alt-KeyPress-", button[0][button[3]].lower(), ">")
                    ),
                    self.try_event(button[4]),
                )
        scrollbar = tkinter.Scrollbar(
            master=report_frame,
            orient=tkinter.VERTICAL,
            command=self.textreport.yview,
        )
        self.textreport.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self.textreport.pack(
            side=tkinter.LEFT, fill=tkinter.BOTH, expand=tkinter.TRUE
        )
        report_frame.pack(
            side=tkinter.BOTTOM, fill=tkinter.BOTH, expand=tkinter.TRUE
        )


class AppSysDialogueBase(AppSysReportBase):
    """Base class for dialogues."""

    def __init__(self, report=None, **kargs):
        """Extend superclass and append report to widget.

        parent - passed to superclass as parent argument.
        title - passed to superclass as title argument.
        report - text to be displayed by widget.
        *args - passed to superclass as *args argument.
        **kargs - passed to superclass as **kargs argument.
        """
        super().__init__(**kargs)
        self.append(report)
        self.restore_focus = self._toplevel.focus_get()
        self._toplevel.wait_visibility()
        self._toplevel.grab_set()
        self._toplevel.wait_window()

    def __del__(self):
        """Restore focus to widget with focus before dialogue started."""
        try:
            # restore focus on dismissing dialogue
            self.restore_focus.focus_set()
        except tkinter._tkinter.TclError as error:
            # application destroyed while confirm dialogue exists
            if str(error) != FOCUS_ERROR:
                raise
        super().__del__()


class AppSysReport(AppSysReportBase):
    """Base class for reports.

    On FreeBSD any thread can just call the tkinter.Text insert method, but
    this can be done only in the main thread on Microsoft Windows.  Passing
    the text to the main thread via a queue and getting the main thread to
    do the insert call is fine on both platforms so do it that way.

    """

    def __init__(self, interval=5000, **kargs):
        """Extend superclass to ignore redundant argument.

        parent - passed to superclass as parent argument.
        title - passed to superclass as title argument.
        interval - ignored.
        *args - passed to superclass as *args argument.
        **kargs - passed to superclass as **kargs argument.

        """
        super().__init__(**kargs)

    def append(self, text):
        """Override to append task to queue of tasks to be done in main thread.

        See superclass definition for argument descriptions.
        """
        self.parent.get_appsys().do_ui_task(super().append, args=(text,))

    def _create_widget(self, parent, title, save, ok, close, cnf, kargs):
        """Override to append task to queue of tasks to be done in main thread.

        See superclass definition for argument descriptions.
        """
        parent.get_appsys().do_ui_task(
            super()._create_widget,
            args=(parent, title, save, ok, close, cnf, kargs),
        )

    def get_button_definitions(self, save=None, close=None, **k):
        """Return report button definitions.

        save - description of Save button.
        close - description of Close button.
        **k - sink for other arguments (Ok button command for example).
        """
        buttons = []
        if save is not None:
            buttons.append(
                (
                    save[0],
                    save[2],
                    True,
                    0,
                    self.on_save,
                )
            )
            self._save_title = save[1]
        """if ok is not None:
            buttons.append(
                (ok[0],
                 ok[2],
                 True,
                 0,
                 self._ok_display,
                 ))
            self._ok_callback = ok[3]"""
        if close is not None:
            buttons.append(
                (
                    close[0],
                    close[2],
                    True,
                    0,
                    self.on_close,
                )
            )
            self._close_title = close[1]
        return buttons

    def on_close(self, event=None):
        """Destroy report widget."""
        self._toplevel.destroy()

    def on_save(self, event=None):
        """Present dialogue to save report in selected file."""
        dlg = tkinter.filedialog.asksaveasfilename(
            parent=self._toplevel,
            title=self._save_title,
            # initialdir=os.path.dirname(self.filename),
            defaultextension=".txt",
        )
        if not dlg:
            return
        outfile = open(dlg, mode="wb")
        try:
            outfile.write(
                self.textreport.get("1.0", tkinter.END).encode("utf8")
            )
        finally:
            outfile.close()


def show_report(parent, title, **kargs):
    """Create and return an AppSysReport instance.

    parent - passed to AppSysReport as parent argument.
    title - passed to AppSysReport as title argument.
    **kargs - passed to AppSysReport as **kargs argument.
    """
    return AppSysReport(parent=parent, title=title, **kargs)


class AppSysConfirm(AppSysDialogueBase):
    """A confirmation dialogue with Text widgets for action details."""

    def __init__(self, **kargs):
        """Extend superclass to remember dialogue response.

        *args - passed to superclass as *args argument.
        **kargs - passed to superclass as **kargs argument.
        """
        self.ok = False
        super().__init__(**kargs)

    def get_button_definitions(self, ok=None, close=None, **k):
        """Return confirmation dialogue button definitions.

        save - description of Save button.
        close - description of Close button.
        **k - sink for other arguments (Ok button command for example).
        """
        buttons = []
        if ok is not None:
            buttons.append(
                (
                    ok[0],
                    ok[2],
                    True,
                    0,
                    self.on_ok,
                )
            )
        if close is not None:
            buttons.append(
                (
                    close[0],
                    close[2],
                    True,
                    0,
                    self.on_cancel,
                )
            )
            self._close_title = close[1]
        return buttons

    def is_ok(self):
        """Return True if dialogue dismissed with OK button."""
        return self.ok

    def on_cancel(self, event=None):
        """Dismiss dialogue and indicate OK button not used."""
        self.ok = False
        self._toplevel.destroy()

    def on_ok(self, event=None):
        """Dismiss dialogue and indicate OK button used."""
        self.ok = True
        self._toplevel.destroy()

    def __del__(self):
        """Extend to indicate dialogue not dismissed with OK button."""
        self.ok = False
        super().__del__()


def show_confirm(parent, title, report, **kargs):
    """Create and return an AppSysConfirm instance.

    parent - passed to AppSysConfirm as parent argument.
    title - passed to AppSysConfirm as title argument.
    report - passed to AppSysConfirm as report argument.
    **kargs - passed to AppSysConfirm as **kargs argument.
    """
    return AppSysConfirm(parent=parent, title=title, report=report, **kargs)


class AppSysInformation(AppSysDialogueBase):
    """An information dialogue with Text widgets for action details."""

    def on_ok(self, event=None):
        """Dismiss dialogue and restore focus to widget that lost focus."""
        self.confirm.destroy()

    def get_button_definitions(self, close=None, **k):
        """Return confirmation dialogue button definitions.

        close - description of Close button.
        **k - sink for other arguments (Ok button command for example).
        """
        buttons = []
        if close is not None:
            buttons.append(
                (
                    close[0],
                    close[2],
                    True,
                    0,
                    self.on_close,
                )
            )
            self._close_title = close[1]
        return buttons

    def on_close(self, event=None):
        """Dismiss dialogue and restore focus to widget that lost focus."""
        self._toplevel.destroy()


def show_information(parent, title, report, **kargs):
    """Create and return an AppSysConfirm instance.

    parent - passed to AppSysInformation as parent argument.
    title - passed to AppSysInformation as title argument.
    report - passed to AppSysInformation as report argument.
    **kargs - passed to AppSysInformation as **kargs argument.
    """
    return AppSysInformation(
        parent=parent, title=title, report=report, **kargs
    )
