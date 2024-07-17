# logpanel.py
# Copyright 2013 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Provide classes which contain task log widgets.

These are used in the notebook style frame.AppSysFrame or a tkinter.Toplevel.

"""

import tkinter
import threading

from .textreadonly import make_scrolling_text_readonly
from . import (
    tasklog,
    panel,
)


class TextAndLogPanel(panel.PlainPanel):
    """Provide task log widget for the notebook style frame.AppSysFrame."""

    def __init__(
        self,
        parent=None,
        taskheader=None,
        taskdata=None,
        taskbuttons=None,
        starttaskbuttons=(),
        runmethod=None,
        runmethodargs=None,
        cnf=None,
        **kargs
    ):
        """Create the task log Text widget.

        parent - passed to superclass
        taskheader - optional text for the optional task header widget
        taskdata - optional intial text for the task log widget
        taskbuttons - button definitions for controlling the running task
        starttaskbuttons - button definitions for starting the task
        runmethod - method which does the task
        runmethodargs - arguments for the method which runs the task
        cnf - passed to superclass, default {}
        **kargs - passed to superclass

        """
        self.taskbuttons = {} if taskbuttons is None else taskbuttons

        super().__init__(
            parent=parent, cnf={} if cnf is None else cnf, **kargs
        )

        self.hide_panel_buttons()
        self.show_panel_buttons(starttaskbuttons)
        self.create_buttons()

        if taskheader is not None:
            self.headerwidget = tkinter.Label(
                master=self.get_widget(), text=taskheader
            )
            self.headerwidget.pack(side=tkinter.TOP, fill=tkinter.X)

        paned_w = tkinter.PanedWindow(
            self.get_widget(),
            opaqueresize=tkinter.FALSE,
            orient=tkinter.VERTICAL,
        )
        paned_w.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=tkinter.TRUE)

        if taskdata is not None:
            datawidget_frame, self.datawidget = make_scrolling_text_readonly(
                master=paned_w, wrap=tkinter.WORD, undo=tkinter.FALSE
            )
            paned_w.add(datawidget_frame)
            self.datawidget.insert(tkinter.END, taskdata)

        report_frame = tkinter.Frame(master=paned_w)
        self.tasklog = tasklog.TaskLog(
            get_app=self.get_appsys,
            logwidget=tasklog.LogText(
                master=report_frame,
                get_app=self.get_appsys,
                cnf=dict(wrap=tkinter.WORD, undo=tkinter.FALSE),
            ),
        )
        paned_w.add(report_frame)
        if runmethod is not False:
            self.tasklog.run_method(
                runmethod,
                kwargs={} if runmethodargs is None else runmethodargs,
            )

    def close(self):
        """Close resources prior to destroying this instance.

        Used, at least, as callback from AppSysFrame container
        """
        # pass

    def describe_buttons(self):
        """Define all action buttons that may appear on Control page."""
        for tbi, button in self.taskbuttons.items():
            if button["command"] is False:
                button["command"] = self.on_dismiss
            self.define_button(tbi, **button)

    def on_dismiss(self, event=None):
        """Do nothing 'dismiss' button for escape from task panel."""
        # pass

    def create_buttons(self):
        """Create the action buttons in the main thread.

        This method is called in enough places to get it's own copy of the
        mechanism to ensure it is executed in the main thread.

        """
        if threading.current_thread().name == "MainThread":
            super().create_buttons()
        else:
            self.get_appsys().do_ui_task(super().create_buttons)


class WidgetAndLogPanel(panel.PlainPanel):
    """This class provides a task log widget in a tkinter.Toplevel."""

    def __init__(
        self,
        parent=None,
        taskheader=None,
        maketaskwidget=None,
        taskbuttons=None,
        starttaskbuttons=(),
        runmethod=None,
        runmethodargs=None,
        cnf=None,
        **kargs
    ):
        """Create the task log Toplevel widget.

        parent - passed to superclass
        taskheader - optional text for the optional task header widget
        maketaskwidget - method to create the task log widget
        taskbuttons - button definitions for controlling the running task
        starttaskbuttons - button definitions for starting the task
        runmethod - method which does the task
        runmethodargs - arguments for the method which runs the task
        cnf - passed to superclass
        **kargs - passed to superclass

        """
        self.taskbuttons = {} if taskbuttons is None else taskbuttons

        super().__init__(
            parent=parent, cnf={} if cnf is None else cnf, **kargs
        )

        self.hide_panel_buttons()
        self.show_panel_buttons(starttaskbuttons)
        self.create_buttons()

        if taskheader is not None:
            self.headerwidget = tkinter.Label(
                master=self.get_widget(), text=taskheader
            )
            self.headerwidget.pack(side=tkinter.TOP, fill=tkinter.X)

        paned_w = tkinter.PanedWindow(
            self.get_widget(),
            opaqueresize=tkinter.FALSE,
            orient=tkinter.VERTICAL,
        )
        paned_w.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=tkinter.TRUE)

        if callable(maketaskwidget):
            paned_w.add(maketaskwidget(paned_w))

        report_frame = tkinter.Frame(master=paned_w)
        self.tasklog = tasklog.TaskLog(
            get_app=self.get_appsys,
            logwidget=tasklog.LogText(
                master=report_frame,
                get_app=self.get_appsys,
                cnf=dict(wrap=tkinter.WORD, undo=tkinter.FALSE),
            ),
        )
        paned_w.add(report_frame)
        if runmethod is not False:
            self.tasklog.run_method(
                runmethod,
                kwargs={} if runmethodargs is None else runmethodargs,
            )

    def close(self):
        """Do nothing."""
        # pass

    def describe_buttons(self):
        """Define all action buttons that may appear on Control page."""
        for tbi, button in self.taskbuttons.items():
            if button["command"] is False:
                button["command"] = self.on_dismiss
            self.define_button(tbi, **button)

    def on_dismiss(self, event=None):
        """Do nothing 'dismiss' button for escape from task panel."""
        # pass

    def create_buttons(self):
        """Create application buttons.

        Delegate to superclass create_buttons method if in main thread
        or queue the superclass method for execution in main thread.
        """
        if threading.current_thread().name == "MainThread":
            super().create_buttons()
        else:
            self.get_appsys().do_ui_task(super().create_buttons)
