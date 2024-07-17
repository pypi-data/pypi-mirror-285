# __init__.py
# Copyright 2007 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Define widgets to provide a notebook style User Interface.

The frame, logpanel, panel, and threadqueue, modules in this package
assume that an user interface is presented in notebook style following the
example of wxWidgets.

The frame, logpanel, and panel, modules provide a number of classes which
applications should subclass as needed when building a notebook style user
interface.  All the classes are subclasses of tkinter.Frame, tkinter.Panel,
or tkinter.Button.

The threadqueue module provides the AppSysThreadQueue class which adds the
ability to run a single background task at a time to the frame.AppSysFrame
class.

The tasklog module provides a widget for reporting progress of an activity.
It is used by the logpanel module but does not rely on the notebook style.

The reports, textreadonly, and texttab, modules provide widgets for reports
containing more data than can be displayed conveniently in the tkinter
messagebox widgets.

The textentry module provides a widget which wraps a tkinter.Entry widget
in a tkinter.Toplevel widget.

The colourslider and fontchooser modules provide widgets for selecting the
font and colours used in a user interface.

The help module provides functions for displaying help text files for an
application.

The exceptionhandler module provides a widget for displaying an exception
report for an exception which is causing the application to stop.
"""
