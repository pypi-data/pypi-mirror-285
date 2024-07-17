# callthreadqueue.py
# Copyright 2013 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Provide the CallThreadQueue class to run methods in a dedicated thread.

Methods are read from a queue and requests to run methods while the thread
is running a method are rejected.

"""
import queue
import threading


class CallThreadQueue:
    """Provide a queue and a thread which runs methods placed on the queue.

    The maximum size of the queue is one.

    """

    def __init__(self):
        """Create the queue and start the thread."""
        super().__init__()
        self.queue = queue.Queue(maxsize=1)
        threading.Thread(target=self.__call_method, daemon=True).start()

    def __call_method(self):
        """Get method from queue, run it, and then wait for next method."""
        while True:
            try:
                method, args, kwargs = self.queue.get()
            except:
                self.queue.task_done()
                self.queue = None
                break
            method(*args, **kwargs)
            self.queue.task_done()

    def put_method(self, method, args=(), kwargs=None):
        """Append the method and it's arguments to the queue.

        method - the method to be run.
        args - passed to method as *args.
        kwargs - passed to method as **kwargs.

        The entry is a tuple:

        (method, args, kwargs).
        """
        self.queue.put((method, args, {} if kwargs is None else kwargs))
