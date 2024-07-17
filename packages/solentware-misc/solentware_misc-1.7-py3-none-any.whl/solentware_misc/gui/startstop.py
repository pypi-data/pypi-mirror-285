# startstop.py
# Copyright 2020 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Functions to assist application start, stop, and exception display."""

import tkinter
import tkinter.messagebox

from solentware_bind.gui.exceptionhandler import GRAB_ERROR


def start_application_exception(error, appname="Application", action="start"):
    """Report an application exception during startup."""
    try:
        tkinter.messagebox.showerror(
            title=appname.join(("Start ", " Exception")),
            message=".\n\nThe reported exception is:\n\n".join(
                (action.join(("Unable to ", " " + appname)), str(error))
            ),
        )
    except tkinter.TclError as tkerror:
        if str(tkerror) != GRAB_ERROR:
            raise SystemExit(
                "Problem in tkinter reporting failure to start application"
            )
    except:
        raise SystemExit("Problem reporting failure to start application")


def stop_application(app, topwidget):
    """Destroy application widget and stop application."""
    try:
        topwidget.destroy()
    except:
        pass
    try:
        del app
    except:
        pass


def application_exception(
    error, app, topwidget, title="Application", appname="the application"
):
    """Report an application exception during run."""
    try:
        tkinter.messagebox.showerror(
            parent=topwidget,
            title=title,
            message="".join(
                (
                    "An exception which cannot be handled within ",
                    appname,
                    " has occurred.",
                    "\n\nThe reported exception is:\n\n",
                    str(error),
                )
            ),
        )
    except tkinter.TclError as local_error:
        if str(local_error) != GRAB_ERROR:
            raise SystemExit(
                "".join(
                    (
                        "Problem in tkinter reporting exception within ",
                        appname,
                        " : ",
                        str(local_error),
                    )
                )
            )
    except Exception as local_error:
        try:
            ser = tkinter.Tk()
            ser.wm_title(title)
            try:
                tkinter.messagebox.showerror(
                    parent=ser,
                    title=title,
                    message="".join(
                        (
                            "An exception which cannot be handled by ",
                            appname,
                            " has occurred.",
                            "\n\nThe reported exception is:\n\n",
                            str(local_error),
                        )
                    ),
                )
            except tkinter.TclError as _error:
                if str(_error) != GRAB_ERROR:
                    raise SystemExit(
                        "".join(
                            (
                                "Problem in tkinter reporting exception in ",
                                appname,
                                " : ",
                                str(_error),
                            )
                        )
                    )
            except Exception as _error:
                raise SystemExit(
                    "".join(
                        (
                            "Problem reporting exception in ",
                            appname,
                            " : ",
                            str(_error),
                        )
                    )
                )
            ser.destroy()
            del ser
        except Exception as exc:
            raise SystemExit(
                "".join(
                    (
                        "Problem reporting problem in reporting exception in ",
                        appname,
                        " : ",
                        str(exc),
                    )
                )
            )
    stop_application(app, topwidget)
