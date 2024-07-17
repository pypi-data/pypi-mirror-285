# threadqueue.py
# Copyright 2013 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Provide the AppSysThreadQueue class to run background tasks.

It extends the frame.AppSysFrame class which supports progress reports.

"""

import queue
import threading

from ..core import callthreadqueue

from . import frame


class AppSysThreadQueue(frame.AppSysFrame):
    """Add thread task queue and UI update queue to frame.AppSysFrame class.

    Provide a background thread and associated queue for submitting tasks using
    a CallThreadQueue instance.  One background task can be run at a time.
    Requests to run a background task when one is already running are rejected.

    Use a queue to pass user interface update requests to the main thread for
    execution.  (The background task can report progress to the task log.)

    This means all user interface update calls have to be done as:
    do_ui_task(<method>, tuple, dictionary).

    Just do <method>(*tuple, **dictionary) if the main thread does the call.

    Do <queue>.put((<method>, tuple, dictionary)) for other threads.

    """

    # Start of comments copied from chesstab.gui.chessdu on 2017-09-05.

    # Methods __call__, get_reportqueue, __run_ui_task_from_queue, and
    # get_thread_queue, introduced to allow this module to work if tkinter is
    # compiled without --enable-threads as in OpenBSD 5.7 i386 packages.  The
    # standard build from FreeBSD ports until early 2015 at least, when this
    # change was introduced, is compiled with --enable-threads so the unchanged
    # code worked.  Not sure if the change in compiler on FreeBSD from gcc to
    # clang made a difference.  The Microsoft Windows' Pythons seem to be
    # compiled with --enable-threads because the unchanged code works in that
    # environment.  The situation on OS X, and any GNU-Linux distribution, is
    # not known.

    # Code in the solentware_misc.gui.tasklog module already dealt with this
    # problem, so the minimum necessary was copied to here.  The classes in
    # tasklog are modified versions of code present in this module before this
    # change.

    # End of comments copied from chesstab.gui.chessdu on 2017-09-05.

    def __init__(self, interval=5000, **kargs):
        """Delegate to superclass then create and start task.

        Tasks are taken from a queue of maximum length 1.

        interval - poll report queue after a time delay (default 5 seconds).
        **kargs - passed to superclass as **kargs argument.
        """
        super().__init__(**kargs)
        self.queue = callthreadqueue.CallThreadQueue()
        self.reportqueue = queue.Queue(maxsize=1)
        self.__run_ui_task_from_queue(interval)

    def get_reportqueue(self):
        """Return the report notification queue."""
        return self.reportqueue

    def __run_ui_task_from_queue(self, interval):
        """Do all queued tasks then poll the queue after interval.

        interval - poll report queue after a time delay.
        """
        while True:
            try:
                method, args, kwargs = self.reportqueue.get_nowait()
                method(*args, **kwargs)
            except queue.Empty:
                self.get_widget().after(
                    interval,
                    self.try_command(
                        self.__run_ui_task_from_queue, self.get_widget()
                    ),
                    *(interval,)
                )
                break
            self.reportqueue.task_done()

    def do_ui_task(self, method, args=(), kwargs=None):
        """Run method on main thread or add to queue on other threads.

        method - the method to be run.
        args - passed to method as *args.
        kwargs - passed to method as **kwargs, default {}.

        The method is called directly if do_ui_task is running in the main
        thread.

        The method and it's arguments are added to the report queue if
        do_ui_task is not running in the main thread.  The entry is a tuple:

        (method, args, kwargs).
        """
        if kwargs is None:
            kwargs = {}
        if threading.current_thread().name == "MainThread":
            method(*args, **kwargs)
        else:
            self.reportqueue.put((method, args, kwargs))
