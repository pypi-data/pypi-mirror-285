# dialogue.py
# Copyright 2020 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Provide classes which do modal dialogues and non-modal reports.

The Dialog and SimpleDialog classes in the tkinter.simpledialog module
are used to guide implementation.

ModalDialogueGo follows the example of tkinter.simpledialog.SimpleDialog,
and ModalDialogue follows the example of tkinter.simpledialog.Dialog, in
starting and closing a dialogue.

ModalDialogueGo does:

    self.root.wait_visibility()
    self.root.grab_set()
    self.root.mainloop()
    self.root.destroy()

in it's go() method and the button methods do self.root.quit().

ModalDialogue does:

    self.root.wait_visibility()
    self.root.grab_set()
    self.root.wait_window()

in it's __init__() method and the button methods do self.root.destroy().

ModalDialogue assumes a tkinter mainloop() is running in the caller's
environment, while ModalDialogueGo runs it's own tkinter mainloop().

Report does not do a grab_set sequence, and does self.root.destroy() in
it's Close button's method only.

Construction of the dialogue widget is done by this module's Dialogue class,
a superclass of ModalDialogueGo, ModalDialogue, and Report.

This module's Dialogue class does not do:

    self.root.wait_visibility()
    self.root.grab_set()
    and either self.root.mainloop() or self.root.wait_window()

but does do self.root.destroy() in it's button methods.

The ModalConfirmGo and ModalConfirm classes provide a dialogue with the Ok
and Cancel buttons.  It is indended for cases where a choice must be made
between doing, and not doing, something.

The ModalInformationGo and ModalInformation classes provide a dialogue with
the Ok button.  It is intended for cases where acknowledging something must
happen before proceeding.

The show_modal_confirm() and show_modal_information() methods create a
ModalConfirmGo or ModalInformationGo instance respectively, call it's go()
method, and return the instance.

"""

import tkinter
import tkinter.filedialog

from solentware_bind.gui.bindings import Bindings
from solentware_bind.gui.exceptionhandler import FOCUS_ERROR, DESTROY_ERROR

from . import textreadonly


class Dialogue(Bindings):
    """Base class for non-modal dialogues which use the event loop for parent.

    parent - report's parent object (note this is not a tkinter widget).
    title - report title text.
    text - the text to display in the widget.
    action_titles - titles associated with widget displayed by button.  Any
                    items in action_titles whose key is not present as a
                    [0] value of a buttons item are ignored.
    buttons - iterable of Button names.
    side - rule for packing buttons in widget, default tkinter.BOTTOM.
    scroll - provide scrollbar for text, default is True.
    body - a function which returns a widget, default is a customised Text
           widget returned by textreadonly.make_text_readonly().  Widgets
           with more structure may be used by subclasses of Dialogue
           provided the subclass overrides the append method to fit, and
           wrappers for the bind, cget, configure, yview, and pack, methods
           of the target Text widget in body.
    geometry - position the report relative to parent if True, default False.
    cnf - passed as cnf argument to tkinter.Text widget created if body is
          None.
    **kargs - passed as **kargs argument to tkinter.Text widget created if
              body is None, or the body() function.

    The parent argument is expected to have a get_widget() method, which
    returns a tkinter object useable as the master argument in Toplevel()
    calls for example.

    A scrollbar is provided if text is too large to fit in widget, even if
    scroll argument is False.

    The action attribute is initialised to None, and by default set to the
    name which appears on the button used to close the widget.  You should
    allow for the action attribute being bound to None, which will happen if
    the application is destroyed by the window manager, when deciding what to
    do based on it's value.

    Two methods, with names based on the button name, are generated:
    on_<button name>, if it does not exist, which sets the action attribute;
    <button name>_pressed which returns True if the action attribute value
    is the button name.

    Keyboard equivalents for button click events indicated by an underlined
    character in the button label are provided by default.

    Buttons do not take focus via keyboard traversal by default.
    """

    underline_buttons = True
    buttons_takefocus = tkinter.FALSE

    def __init__(
        self,
        parent=None,
        title=None,
        text=None,
        action_titles=None,
        buttons=None,
        side=tkinter.BOTTOM,
        scroll=True,
        body=None,
        geometry=False,
        cnf=None,
        **kargs
    ):
        """Create modal or non-modal dialogue."""
        super().__init__()
        self.action = None
        if buttons is None:
            buttons = ()
        self._create_widget(
            parent,
            title,
            text,
            action_titles,
            buttons,
            side,
            scroll,
            body,
            {} if cnf is None else cnf,
            kargs,
        )
        self.root.protocol("WM_DELETE_WINDOW", self.wm_delete_window)

        # self.restore_focus = self.root.focus_get()
        if geometry:
            self._set_geometry(self.parent.get_widget())

        def button_action():
            return self.action

        def button_function(action):
            def function():
                return bool(action == button_action())

            return function

        # Create methods <button name>_pressed which return True if self.action
        # equals name of button.  For example a button labelled 'Add Name' will
        # get the method self.add_name_pressed().  It is assumed clicking a
        # button causes self.action to be set to the button label (the text
        # argument in the tkinter.Button() call for the button).
        for button in buttons:
            setattr(
                self,
                "_".join(button.split()).lower() + "_pressed",
                button_function(button),
            )

    def append(self, text):
        """Append text to body widget."""
        self.body.insert(tkinter.END, text)

    def _create_widget(
        self,
        parent,
        title,
        text,
        action_titles,
        buttons,
        side,
        scroll,
        body,
        cnf,
        kargs,
    ):
        """Create the report or dialogue widget."""
        if action_titles is None:
            action_titles = {}
        for k, action in action_titles.items():
            if isinstance(action, str):
                action_titles[k] = (action, "")
            elif len(action) < 2:
                action_titles[k] += ("",) * (2 - len(action))
        self.parent = parent
        self.root = tkinter.Toplevel(master=parent.get_widget())
        self.root.title(title)
        self.root.iconname(title)
        reportframe = tkinter.Frame(master=self.root)
        span = len(buttons)
        if scroll:
            reportframe.pack(
                side=tkinter.BOTTOM, expand=tkinter.TRUE, fill=tkinter.BOTH
            )
        else:
            reportframe.pack(side=tkinter.BOTTOM, expand=tkinter.TRUE)
        bodyframe = tkinter.Frame(master=reportframe)
        bodyframe.grid_configure(sticky=tkinter.NSEW)
        if side == tkinter.BOTTOM:
            if scroll:
                reportframe.grid_rowconfigure(0, weight=1)
            bodyframe.grid_configure(row=0, column=0, columnspan=span)
        elif side == tkinter.RIGHT:
            if scroll:
                reportframe.grid_columnconfigure(0, weight=1)
            bodyframe.grid_configure(row=0, column=0, rowspan=span)
        elif side == tkinter.TOP:
            if scroll:
                reportframe.grid_rowconfigure(1, weight=1)
            bodyframe.grid_configure(row=1, column=0, columnspan=span)
        elif side == tkinter.LEFT:
            if scroll:
                reportframe.grid_columnconfigure(1, weight=1)
            bodyframe.grid_configure(row=0, column=1, rowspan=span)
        if body is None:
            self.body = textreadonly.make_text_readonly(
                master=bodyframe, cnf=cnf, **kargs
            )
        else:
            self.body = body(master=bodyframe, cnf=cnf, **kargs)
        if not self.underline_buttons:
            underline = [-1] * len(buttons)
        elif len(set(b[0].lower() for b in buttons)) == len(buttons):
            underline = [0] * len(buttons)
        else:
            bchars = set("".join(buttons).lower())
            underline = [-1] * len(buttons)
            for index, action in enumerate(buttons):
                for i, char in enumerate(action):
                    if char in bchars:
                        underline[index] = i
                        bchars.discard(char)
                        break
        self.action_title = {}
        for index, action in enumerate(buttons):
            on_b_attr_name = "on_" + "_".join(action.split()).lower()
            if not hasattr(self, on_b_attr_name):
                setattr(self, on_b_attr_name, self.button_on_attr(action))
            on_b = getattr(self, on_b_attr_name)
            if action in action_titles:
                self.action_title[on_b] = action_titles[action][0]
            else:
                self.action_title[on_b] = action
            button = tkinter.Button(
                master=reportframe,
                text=action,
                takefocus=self.buttons_takefocus,
                underline=underline[index],
                command=self.try_command(on_b, self.root),
            )
            if side == tkinter.BOTTOM:
                button.grid_configure(column=index, row=1, padx=5)
                if scroll:
                    reportframe.grid_columnconfigure(index, weight=1)
            elif side == tkinter.RIGHT:
                button.grid_configure(row=index, column=1, padx=5)
                if scroll:
                    reportframe.grid_rowconfigure(index, weight=1)
            elif side == tkinter.TOP:
                button.grid_configure(column=index, row=0, padx=5)
                if scroll:
                    reportframe.grid_columnconfigure(index, weight=1)
            elif side == tkinter.LEFT:
                button.grid_configure(row=index, column=0, padx=5)
                if scroll:
                    reportframe.grid_rowconfigure(index, weight=1)
            if underline[index] >= 0:
                self.body.bind(
                    "".join(
                        (
                            "<Alt-KeyPress-",
                            action[underline[index]].lower(),
                            ">",
                        )
                    ),
                    self.try_event(on_b),
                )
        self.focus_set()
        forcescroll = bool(scroll)
        if text is not None:
            if not scroll:
                height = self.body.cget("height")
                width = self.body.cget("width")
                lines = text.splitlines()
                linecount = len(lines)
                maxlinelength = max(len(line) for line in lines)
                if linecount > height or maxlinelength > width:
                    forcescroll = True
                    if maxlinelength > width:
                        if self.body.cget("wrap") == tkinter.NONE:
                            self.body.configure(wrap=tkinter.WORD)
            self.append(text)
        if forcescroll:
            scrollbar = tkinter.Scrollbar(
                master=bodyframe,
                orient=tkinter.VERTICAL,
                command=self.body.yview,
            )
            self.body.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self.body.pack(
            side=tkinter.LEFT, fill=tkinter.BOTH, expand=tkinter.TRUE
        )

    def button_on_attr(self, action):
        """Return event handler which sets action and destroys dialogue.

        Action indicates the action requested by dialogue.

        The requested action is not done by the event handler.
        """

        def on_f(event=None):
            del event
            self.action = action
            self.root.destroy()

        return on_f

    def _set_geometry(self, master, relx=0.5, rely=0.3):
        """Set the widget geometry and make the widget visible.

        Copied from tkinter.simpledialog.SimpleDialog._set_transient but
        renamed _set_geometry because that seems more appropriate to what
        is done.

        The original widget.transient() call is wrapped because Dialogue
        should not do it but ModalDialogue and ModalDialogueGo should.
        """
        widget = self.root
        widget.withdraw()  # Remain invisible while we figure out the geometry.
        self.widget_transient(widget, master)
        widget.update_idletasks()  # Actualize geometry information.
        if master.winfo_ismapped():
            m_width = master.winfo_width()
            m_height = master.winfo_height()
            m_x = master.winfo_rootx()
            m_y = master.winfo_rooty()
        else:
            m_width = master.winfo_screenwidth()
            m_height = master.winfo_screenheight()
            m_x = m_y = 0
        w_width = widget.winfo_reqwidth()
        w_height = widget.winfo_reqheight()
        x = m_x + (m_width - w_width) * relx
        y = m_y + (m_height - w_height) * rely
        if x + w_width > master.winfo_screenwidth():
            x = master.winfo_screenwidth() - w_width
        elif x < 0:
            x = 0
        if y + w_height > master.winfo_screenheight():
            y = master.winfo_screenheight() - w_height
        elif y < 0:
            y = 0
        widget.geometry("+%d+%d" % (x, y))
        widget.deiconify()  # Become visible at the desired location.

    def widget_transient(self, *args):
        """Do nothing.  Dialogue is for persistent widgets."""

    def wm_delete_window(self):
        """Do nothing.  Deletion is not tied to a button action by default.

        Subclasses are likely to choose the Cancel button action as the
        appropriate action by overriding this method.

        """

    def focus_set(self, *args, **kargs):
        """Do nothing.  Dialogies which accept input will likely override."""


class ModalDialogueGo(Dialogue):
    """Base class for modal dialogues which provide their own event loop.

    *args - passed to superclass as *args argument.
    geometry - position the report relative to parent if True, default True.
               (parent is the first argument in *args)
    **kargs - passed to superclass as **kargs argument.
    """

    def __init__(self, geometry=True, **kargs):
        """Extend and note widget with focus on opening dialogue."""
        super().__init__(geometry=geometry, **kargs)
        self.restore_focus = self.root.focus_get()

    # Follow example in tkinter.simpledialog.SimpleDialog class.
    # Do not use with ModalConfirm and ModalInformation classes.
    # If the button commands call destroy() rather than quit(), the mainloop()
    # and destroy() calls in 'go' must be replaced by a wait_window() call.
    def go(self):
        """Run dialogue, destroy window, and return action."""
        self.root.wait_visibility()
        self.root.grab_set()
        self.root.mainloop()
        try:
            self.root.destroy()
        except tkinter.TclError as error:
            # application destroyed while confirm dialogue exists.
            if str(error) != DESTROY_ERROR:
                raise
        return self.action

    def __del__(self):
        """Restore focus to widget with focus before dialogue started."""
        try:
            # restore focus on dismissing dialogue.
            if self.restore_focus is not None:
                self.restore_focus.focus_set()
        except tkinter._tkinter.TclError as error:
            # application destroyed while confirm dialogue exists.
            if str(error) != FOCUS_ERROR:
                raise
        super().__del__()

    def button_on_attr(self, action):
        """Return default event handler for button name 'a'."""

        def on_f(event=None):
            del event
            self.action = action
            if self.restore_focus is not None:
                self.restore_focus.focus_set()
            self.root.quit()

        return on_f

    def widget_transient(self, widget, master):
        """Mark the widget transient.

        The widget is marked transient because it is modal.  Particular window
        managers may ignore the mark.

        Copied from tkinter.simpledialog.SimpleDialog._set_transient but
        wrapped.
        """
        widget.transient(master)


class ModalDialogue(Dialogue):
    """Base class for modal dialogues which use the event loop for parent.

    *args - passed to superclass as *args argument.
    **kargs - passed to superclass as **kargs argument.
    """

    def __init__(self, **kargs):
        """Extend and note widget with focus on opening dialogue."""
        super().__init__(**kargs)
        self.restore_focus = self.root.focus_get()

        # Emulate reports.AppSysDialogueBase
        self.root.wait_visibility()
        self.root.grab_set()
        self.root.wait_window()

    def __del__(self):
        """Restore focus to widget with focus before dialogue started."""
        try:
            # restore focus on dismissing dialogue
            if self.restore_focus is not None:
                self.restore_focus.focus_set()
        except tkinter._tkinter.TclError as error:
            # application destroyed while confirm dialogue exists
            if str(error) != FOCUS_ERROR:
                raise
        super().__del__()

    def widget_transient(self, widget, master):
        """Mark the widget transient.

        The widget is marked transient because it is modal.  Particular window
        managers may ignore the mark.

        """
        widget.transient(master)


# Report is the replacement for the reports.AppSysReport class, which offers
# Save, Ok, and Close, buttons in __init__ arguments, where Ok is always
# ignored.  Here the save and close arguments are absent and both buttons are
# always provided.  If the arguments are provided the call to tkinter.Text
# creating the report's widget will raise an exception.
class Report(Dialogue):
    """Display a non-modal dialogue with Save and Close options.

    interval - ignored.
    buttons - ignored, the Save and Close buttons are supplied.
    *args - passed to superclass as *args argument.
    **kargs - passed to superclass as **kargs argument.

    On FreeBSD any thread can just call the tkinter.Text insert method, but
    this can be done only in the main thread on Microsoft Windows.  Passing
    the text to the main thread via a queue and getting the main thread to
    do the insert call is fine on both platforms so do it that way.
    """

    buttons = "Save", "Close"

    def __init__(self, interval=5000, buttons=None, **kargs):
        """Extend superclass to ignore redundant arguments."""
        del interval, buttons
        super().__init__(buttons=self.buttons, **kargs)

    def append(self, text):
        """Override to append task to queue of tasks to be done in main thread.

        See superclass definition for argument descriptions.
        """
        self.parent.get_appsys().do_ui_task(super().append, args=(text,))

    def _create_widget(
        self,
        parent,
        title,
        text,
        action_titles,
        buttons,
        side,
        scroll,
        body,
        cnf,
        kargs,
    ):
        """Override to append task to queue of tasks to be done in main thread.

        See superclass definition for argument descriptions.
        """
        parent.get_appsys().do_ui_task(
            super()._create_widget,
            args=(
                parent,
                title,
                text,
                action_titles,
                buttons,
                side,
                scroll,
                body,
                cnf,
                kargs,
            ),
        )

    def on_save(self, event=None):
        """Override and present dialogue to save report in selected file.

        The report widget is not destroyed, so self.attribute is not set to
        the button name 'Save' and the self.save_pressed() method generated
        by the superclass will always return False.

        The report is saved in utf-8 encoding.

        """
        del event
        dlg = tkinter.filedialog.asksaveasfilename(
            parent=self.root,
            title=self.action_title[self.on_save],
            defaultextension=".txt",
        )
        if not dlg:
            return
        with open(dlg, mode="wb") as outfile:
            outfile.write(self.body.get("1.0", tkinter.END).encode("utf8"))


def show_report(parent, title, **kargs):
    """Create and return a Report instance.

    parent - passed to Report as parent argument.
    title - passed to Report as title argument.
    **kargs - passed to Report as **kargs argument.
    """
    return Report(parent=parent, title=title, **kargs)


# ModalConfirm is the replacement for the reports.AppSysConfirm class because
# both use the wait_window() rather than mainloop() style.
class ModalConfirm(ModalDialogue):
    """A confirmation modal dialogue with Ok and Cancel options.

    buttons - ignored, the Ok and Cancel buttons are supplied.
    *args - passed to superclass as *args argument.
    **kargs - passed to superclass as **kargs argument.
    """

    buttons = "Ok", "Cancel"

    def __init__(self, buttons=None, **kargs):
        """Extend superclass to provide Ok and Cancel buttons."""
        del buttons
        super().__init__(buttons=self.buttons, **kargs)


class ModalConfirmGo(ModalDialogueGo):
    """A confirmation modal dialogue with Ok and Cancel options.

    buttons - ignored, the Ok and Cancel buttons are supplied.
    *args - passed to superclass as *args argument.
    **kargs - passed to superclass as **kargs argument.
    """

    buttons = "Ok", "Cancel"

    def __init__(self, buttons=None, **kargs):
        """Extend superclass to provide Ok and Cancel buttons."""
        del buttons
        super().__init__(buttons=self.buttons, **kargs)


def show_modal_confirm(parent, title, **kargs):
    """Return a ModalConfirmGo instance after calling it's go() method.

    parent - passed to ModalConfirmGo as parent argument.
    title - passed to ModalConfirmGo as title argument.
    **kargs - passed to ModalConfirmGo as **kargs argument.
    """
    widget = ModalConfirmGo(parent=parent, title=title, **kargs)
    widget.go()
    return widget


# ModalInformation is the replacement for the reports.AppSysInformation class
# because both use the wait_window() rather than mainloop() style.
class ModalInformation(ModalDialogue):
    """An information modal dialogue with Ok option meaning 'seen it'.

    buttons - ignored, the Ok button is supplied.
    *args - passed to superclass as *args argument.
    **kargs - passed to superclass as **kargs argument.
    """

    buttons = ("Ok",)

    def __init__(self, buttons=None, **kargs):
        """Extend superclass to provide Ok button."""
        del buttons
        super().__init__(buttons=self.buttons, **kargs)


class ModalInformationGo(ModalDialogueGo):
    """An information modal dialogue with Ok option meaning 'seen it'.

    buttons - ignored, the Ok button is supplied.
    *args - passed to superclass as *args argument.
    **kargs - passed to superclass as **kargs argument.
    """

    buttons = ("Ok",)

    def __init__(self, buttons=None, **kargs):
        """Extend superclass to provide Ok button."""
        del buttons
        super().__init__(buttons=self.buttons, **kargs)


def show_modal_information(parent, title, **kargs):
    """Return an ModalInformationGo instance after calling it's go() method.

    parent - passed to ModalInformationGo as parent argument.
    title - passed to ModalInformationGo as title argument.
    **kargs - passed to ModalInformationGo as **kargs argument.
    """
    widget = ModalInformationGo(parent=parent, title=title, **kargs)
    widget.go()
    return widget


class _Entry:
    """A data entry modal dialogue with Ok and Cancel options.

    buttons - ignored, the Ok and Cancel buttons are supplied.
    scroll - ignored, set to False in super().__init__() call.
    body - either a function which returns a widget of data entry elements,
           or an iterable of prompts, initial values, and substitute characters
           displayed instead of actual values, for data entries,
           or None when a default Entry widget is created.
    *args - passed to superclass as *args argument.
    **kargs - passed to superclass as **kargs argument.

    Expected use is like C(_OnEntry, _Entry, ModalDialogue) where
    ModuleDialogue provides the __init__ method assumed by the super() call.

    Provide default behaviour for modal data entry dialogues.

    Follows the example of the tkinter.simpledialog.Dialog class, but the
    dialogue's Toplevel is bound to an attribute of the _Entry class rather
    than defining _Entry as a subclass of Toplevel.

    The simplest _Entry classes will have one, or perhaps a few, Entry widgets
    and no Text widget with instructions so False is default scroll argument.

    Methods corresponding to the append, bind, cget, configure, focus_set,
    yview, and pack, methods of the default Text widget assumed by Dialogue
    are defined.  All do nothing except focus_set which searches the actual
    widget for something which accepts the focus on keyboard traversal and
    sets the initial focus to the first one found.
    """

    buttons = "Ok", "Cancel"

    def __init__(self, buttons=None, scroll=False, body=None, **kargs):
        """Extend to provide Ok and Cancel buttons and dialogue body."""
        del buttons, scroll
        if body is None:
            body = (("", "", None, False),)
        if isinstance(body, (tuple, list)):
            body = self.body_factory(body)
        self.entries = {}
        self.result = None
        super().__init__(
            buttons=self.buttons, scroll=False, body=body, **kargs
        )

    def __del__(self):
        """Restore focus to widget with focus before dialogue started."""
        self.entries = None
        self.result = None
        if hasattr(super(), "__del__"):
            super().__del__()

    def append(self, text):
        """Override, do nothing."""

    def bind(self, *a, **k):
        """Do nothing."""

    def cget(self, *a, **k):
        """Do nothing."""

    def configure(self, *a, **k):
        """Do nothing."""

    def yview(self, *a, **k):
        """Do nothing."""

    def pack(self, *a, **k):
        """Do nothing."""

    def focus_set(self, *args, **kargs):
        """Set focus to first widget found in keyboard traversal order.

        Child widgets are searched before siblings.
        """
        del args, kargs
        widget = self._child_focus_set(self.body)
        if widget:
            widget.focus_set()

    def _child_focus_set(self, widget):
        """Return widget or child widget if it takes focus.

        Children are searched first.  False is returned if no children of
        widget nor widget take focus.
        """
        children = widget.winfo_children()
        if not children:
            if widget.cget("takefocus") != str(tkinter.FALSE):
                return widget
            return False
        for child in children:
            focus_widget = self._child_focus_set(child)
            if focus_widget:
                return focus_widget
        return False

    # tkinter.simpledialog.Dialog equivalent is 'body', but this name is taken.
    def body_factory(self, body_definition):
        """Return function which creates the dialogue body."""

        def make_body(master=None, cnf=None, **kwargs):
            # Create dialog body and return dictionary of Entry widgets.
            del kwargs
            if cnf is None:
                cnf = {}
            frame = tkinter.Frame(master)
            for index, body in enumerate(body_definition):
                prompt, initialvalue, substitute, select = body
                label = tkinter.Label(frame, text=prompt, justify=tkinter.LEFT)
                label.grid(row=index * 2, padx=5, sticky=tkinter.W)
                if initialvalue is not None:
                    width = max(30, min(80, len(str(initialvalue))))
                else:
                    width = 30
                if substitute is not None:
                    entry = tkinter.Entry(frame, show=substitute, width=width)
                else:
                    entry = tkinter.Entry(frame, width=width)
                entry.grid(
                    row=index * 2 + 1, padx=5, sticky=tkinter.W + tkinter.E
                )
                if initialvalue is not None:
                    entry.insert(0, initialvalue)
                if select:
                    entry.select_range(0, tkinter.END)
                self.entries[prompt] = entry
            return frame

        return make_body

    def getresult(self):
        """Return dictionary of Entry widget content."""
        return {k: v.get() for k, v in self.entries.items()}


class _OnEntry:
    """Provide on_ok and on_cancel methods.

    When used like C(_OnEntry, _Entry, ModalDialogue), the on_ok and
    on_cancel methods are bound to the Ok and Cancel buttons by the
    Dialogue._create_widget method.

    _OnEntry follows the example of tkinter.simpledialog.SimpleDialog in it's
    reaction to events.  The dialogue response indicates which button was used
    to end the dialogue, and some buttons may expose the dialogue's content
    when closed: here Ok provides the content but Cancel does not.

    No validation is done, or action taken, before the content is exposed.

    """

    def on_ok(self, event=None):
        """Handle Ok button event."""
        del event
        if self.parent is not None:
            self.parent.get_widget().focus_set()
        self.action = self.action_title[self.on_ok]
        self.result = self.getresult()
        self.root.destroy()

    def on_cancel(self, event=None):
        """Handle Cancel button event."""
        del event
        if self.parent is not None:
            self.parent.get_widget().focus_set()
        self.action = self.action_title[self.on_cancel]
        self.root.destroy()


class ModalEntry(_OnEntry, _Entry, ModalDialogue):
    """A data entry modal dialogue with Ok and Cancel options.

    _OnEntry provides the button event handlers.

    _Entry provides the button definitions and a function to createthe
    dialogue content.

    ModalDialogue provides the dialogue.

    The event loop is assumed to be active already.
    """


class ModalEntryGo(_OnEntry, _Entry, ModalDialogueGo):
    """A data entry modal dialogue with Ok and Cancel options.

    _OnEntry provides the button event handlers.

    _Entry provides the button definitions and a function to createthe
    dialogue content.

    ModalDialogueGo provides the dialogue.

    The event loop is activated by the ModalDialogueGo.go() method.
    """


class _EntryApply(_Entry):
    """Provide default validate and apply methods.

    The tkinter.simpledialog.Dialog class example is followed.

    The keyboard equivalents for button click events defined by underlining
    a charcter in the button name are suppressed because Ok is bound to the
    Return key and Cancel to Escape in the ModalEntryApplyGo and
    ModalEntryApply classes.
    """

    underline_buttons = False

    def validate(self):
        """Validate data and return True if valid.

        This method is called by self.on_ok before the dialogue is destroyed
        and should be overridden if appropriate.

        By default put entered data in self.results and return True.

        """
        self.result = self.getresult()
        return True

    def apply(self):
        """Do nothing.

        This method is called by self.on_ok after the dialogue is destroyed
        and should be overridden because the Ok button calls on_cancel to
        exit.  (Whatever would have been done if ok_pressed() could and did
        return True should be done in the overriding apply() method.)

        """


class _OnEntryApply:
    """Provide _on_ok and _on_cancel methods.

    The ModalEntryApply and ModalEntryApplyGo subclasses will alias these
    as on_ok and on_cancel in their own ways, so the Dialogue._create_widget
    method will do the correct actions setting up these methods.

    _OnEntryApply follows the example of the ok and cancel methods in
    tkinter.simpledialog.Dialog in the way _on_ok and _on_cancel react to
    events.  The dialogue response does not indicate the button used to end
    the dialogue: here Ok provides validated content but Cancel provides no
    content.

    By default content is assumed valid, but no is action taken, before the
    content is exposed when the _EntryApply class is used too.
    """

    def _on_ok(self, event=None):
        """Handle ok button events.

        The _on_ok method is not used directly.  The name 'on_ok' is bound
        and used.
        """
        del event
        if not self.validate():
            self.initial_focus.focus_set()
            return
        self.root.withdraw()
        self.root.update_idletasks()
        try:
            self.apply()
        finally:
            self.on_cancel()

    def _on_cancel(self, event=None):
        """Handle cancel button events.

        The _on_cancel method is not used directly.  The name 'on_cancel'
        is bound and used.
        """
        del event
        if self.parent is not None:
            self.parent.get_widget().focus_set()
        self.root.destroy()


class ModalEntryApply(_OnEntryApply, _EntryApply, ModalDialogue):
    """A data entry modal dialogue which uses the existing event loop.

    The event loop is assumed to be active already.

    The _on_ok and _on_cancel methods from _OnEntryApply are used by the
    button_on_attr method which overrides the version in Dialogue.  The
    two methods are bound to keys Return and Escape respectively.
    """

    bindings = {"Ok": "<Return>", "Cancel": "<Escape>"}

    def button_on_attr(self, action):
        """Override to bind buttons to methods in _OnEntryApply class."""
        on_b_attr_name = "_on_" + "_".join(action.split()).lower()
        on_f = getattr(self, on_b_attr_name)
        self.root.bind(ModalEntryApply.bindings[action], on_f)
        return on_f


class ModalEntryApplyGo(_OnEntryApply, _EntryApply, ModalDialogueGo):
    """A data entry modal dialogue which uses it's own event loop.

    The event loop is activated by the ModalDialogueGo.go() method.

    The _on_ok and _on_cancel methods from _OnEntryApply are aliased as
    on_ok and on_cancel so Dialogue._create_widget() will use these rather
    than create the default methods.  The two methods are bound to keys
    Return and Escape respectively.
    """

    on_ok = _OnEntryApply._on_ok
    on_cancel = _OnEntryApply._on_cancel

    def __init__(self, *args, **kargs):
        """See _EntryApply."""
        super().__init__(*args, **kargs)
        self.root.bind("<Return>", self.on_ok)
        self.root.bind("<Escape>", self.on_cancel)


if __name__ == "__main__":
    # Extend tkinter.Frame with get_widget() method.
    # This case is simple enough to get away with subclassing rather than
    # defining MainFrame as a container for a tkinter.Frame() instance.
    # The dialogue classes expect get_widget, get_appsys, and do_ui_task
    # to be methods of a container, see panel.Panel for example.
    class MainFrame(tkinter.Frame):
        """Provide get_widget method expected by Dialogue classes.

        MainFrame is a subclass of tkinter.Frame, and is defined when the
        dialogue module is run rather than imported.
        """

        def get_widget(self):
            """Return self.

            The get_widget methods in classes like panel.Panel return the
            attribute bound to the tkinter.Frame because Panel contains a
            tkinter.Frame instance rather than subclasses it.
            """
            return self

        def get_appsys(self):
            """Return self.

            The get_appsys method in class panel.Panel returns the object
            containing the application's do_ui_task() method.  Here
            do_ui_task is defined in MainFrame, this class.
            """
            return self

        def do_ui_task(self, method, args=(), kwargs=None):
            """Run method(*args, **kwargs).

            The do_ui_task method in class threadqueue.AppSysThreadQueue
            places the method and it's arguments on a queue which the
            AppSysThreadQueue instance has set up to be read at intervals
            via the tkinter.after command and run the methods found.  Here
            just run the method.
            """
            if kwargs is None:
                kwargs = {}
            method(*args, **kwargs)

    # Define on_* methods corresponding to buttons named in D() call later.
    # The on_* methods generated by default allow the button pressed to be
    # retrieved, but this way the loop to try things exists already.
    # The 'del event' statements in each on_* method are good practice
    # because event is ignored, but are really included to silence reports
    # by pylint.
    class MainDialogue(Dialogue):
        """Provide button event handlers for Dialogue classes.

        MainDialogue is a subclass of Dialogue, and is defined when the
        dialogue module is run rather than imported.

        The on_* method names correspond to the button names in the
        MainDialogue() call made when the dialogue module is run.  These
        methods become the event handlers for the buttons rather than
        the ones which would be created by default.

        The dialogues created by these event handlers use the event
        handlers created by default.
        """

        def on_dialogue(self, event=None):
            """Handle Dialogue button events."""
            del event
            Dialogue(
                parent=mainframe,
                title="Dialogue",
                text="Message longer than width",
                buttons=("Ok",),
                side=tkinter.TOP,
                scroll=False,
                width=10,
                height=1,
                wrap=tkinter.NONE,
            ).root.mainloop()

        def on_modaldialoguego(self, event=None):
            """Handle ModalDialogueGo button events."""
            del event
            ModalDialogueGo(
                parent=mainframe,
                title="ModalDialogueGo",
                text="Message longer than width",
                buttons=("Ok",),
                side=tkinter.TOP,
                scroll=False,
                width=10,
                height=1,
                wrap=tkinter.NONE,
            ).go()

        def on_modaldialogue(self, event=None):
            """Handle ModalDialogue button events."""
            del event
            ModalDialogue(
                parent=mainframe,
                title="ModalDialogue",
                text="Message longer than width",
                buttons=("Ok",),
                side=tkinter.TOP,
                scroll=False,
                width=10,
                height=1,
                wrap=tkinter.NONE,
            ).root.mainloop()

        def on_modalconfirmgo(self, event=None):
            """Handle ModalConfirmGo button events."""
            del event
            ModalConfirmGo(
                parent=mainframe,
                title="ModalConfirmGo",
                text="Message longer than width",
                side=tkinter.TOP,
                scroll=False,
                width=10,
                height=1,
            ).go()

        def on_modalconfirm(self, event=None):
            """Handle ModalConfirm button events."""
            del event
            ModalConfirm(
                parent=mainframe,
                title="ModalConfirm",
                text="Message longer than width",
                side=tkinter.TOP,
                scroll=False,
                width=10,
                height=1,
            ).root.mainloop()

        def on_modalinformationgo(self, event=None):
            """Handle ModalInformationGo button events."""
            del event
            ModalInformationGo(
                parent=mainframe,
                title="ModalInformationGo",
                text="Message longer than width",
                side=tkinter.TOP,
                scroll=False,
                width=10,
                height=1,
                wrap=tkinter.WORD,
            ).go()

        def on_modalinformation(self, event=None):
            """Handle ModalInformation button events."""
            del event
            ModalInformation(
                parent=mainframe,
                title="ModalInformation",
                text="Message longer than width",
                side=tkinter.TOP,
                scroll=False,
                width=10,
                height=1,
                wrap=tkinter.WORD,
            ).root.mainloop()

        def on_modalentrygo_1(self, event=None):
            """Handle ModalEntryGo button events."""
            del event
            ModalEntryGo(parent=mainframe, title="ModalEntryGo").go()

        def on_modalentry_1(self, event=None):
            """Handle ModalEntry button events."""
            del event
            ModalEntry(parent=mainframe, title="ModalEntry").root.mainloop()

        def on_modalentrygo(self, event=None):
            """Handle ModalEntryGo button events."""
            del event
            ModalEntryGo(
                parent=mainframe,
                title="ModalEntryGo",
                body=(
                    ("URL", "", None, False),
                    ("Password", "mypw", "*", True),
                ),
            ).go()

        def on_modalentry(self, event=None):
            """Handle ModalEntry button events."""
            del event
            ModalEntry(
                parent=mainframe,
                title="ModalEntry",
                body=(
                    ("URL", "", None, False),
                    ("Password", "mypw", "*", True),
                ),
            ).root.mainloop()

        def on_modalentryapplygo(self, event=None):
            """Handle ModalEntryApplyGo button events."""
            del event
            ModalEntryApplyGo(
                parent=mainframe,
                title="ModalEntryApplyGo",
                body=(
                    ("URL", "", None, False),
                    ("Password", "mypw", "*", True),
                ),
            ).go()

        def on_modalentryapply(self, event=None):
            """Handle ModalEntryApply button events."""
            del event
            ModalEntryApply(
                parent=mainframe,
                title="ModalEntryApply",
                body=(
                    ("URL", "", None, False),
                    ("Password", "mypw", "*", True),
                ),
            ).root.mainloop()

        def on_report(self, event=None):
            """Handle Report button events."""
            del event
            Report(
                parent=mainframe, title="Report", text="Some report text"
            ).root.mainloop()

        # self.parent to quit application.
        # widget shown by on_dialogue method does 'self.root.destroy()'.
        def on_quit(self, event=None):
            """Handle Quit button events."""
            del event
            self.parent.winfo_toplevel().destroy()

    mainframe = MainFrame(master=tkinter.Tk(), height=300, width=400)
    mainframe.pack()
    mainframe.winfo_toplevel().wm_title("Main Window")

    # So MainDialogue's Toplevel appears above mainframe's Toplevel.
    mainframe.wait_visibility()

    MainDialogue(
        parent=mainframe,
        title="Dialogues",
        text="".join(
            (
                "Try the dialogues associated with each button.\n\nThe *Go ",
                "widgets appear above the Main Window but the others appear ",
                "anywhere.\n\nThis dialogue is non-modal so the focus is not ",
                "moved here.  Press Tab or click pointer on text area to get ",
                "focus and enable the keyboard equivalents of clicking ",
                "on a button.\n\nA different layout of this dialogue, with ",
                "different text, is available via the Dialogue button, and ",
                "many can be open at once.",
            )
        ),
        buttons=(
            "Dialogue",
            "ModalDialogueGo",
            "ModalDialogue",
            "ModalConfirmGo",
            "ModalConfirm",
            "ModalInformationGo",
            "ModalInformation",
            "ModalEntryGo 1",
            "ModalEntry 1",
            "ModalEntryGo",
            "ModalEntry",
            "ModalEntryApplyGo",
            "ModalEntryApply",
            "Report",
            "Quit",
        ),
        side=tkinter.RIGHT,
        width=40,
        wrap=tkinter.WORD,
    ).parent.winfo_toplevel().mainloop()
