# frame.py
# Copyright 2007 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Provide classes to support a notebook style database User Interface.

(To do: convert to ttk::notebook, which might mean converting applications
using these classes and not using this module.)

"""

import tkinter

# Do not want solentware_misc to depend on solentware_grid, but the way
# DataRegister is used in AppSysFrame.__init__ implies the dependency.  Can be
# resolved by changing the __init__ arguments, but that is more work than can
# be done right now.  (This is different from the ExceptionHandler case, where
# the class ought to be in solentware_misc but solentware_grid needs to use it
# as well.)
try:
    from solentware_grid.core.dataregister import DataRegister
except ImportError:

    class DataRegister:
        """Provide a 'do-nothing' DataRegister class.

        This class is used if importing DataRegister from
        solentware_grid.core.dataregister raises ImportError.

        The consequence is none of the expected automatic refreshing of
        related widgets will occur.
        """

        def __init__(self, **kargs):
            """Do nothing."""
            self.datasources = frozenset()

        def refresh_at_start_of_file(self):
            """Do nothing."""

        def refresh_after_update(self, dskey, instance):
            """Do nothing."""

        def register_in(self, client, callback):
            """Do nothing."""

        def register_out(self, client):
            """Do nothing."""


from solentware_bind.gui.bindings import Bindings


class AppSysFrameButton(Bindings):
    """This class provides the tab selection buttons for an AppSysFrame."""

    def __init__(self, parent=None, cnf=None, **kargs):
        """Create tab selection button, a tkinter.Button instance.

        parent - the parent widget
        cnf - used as cnf argument in tkinter.Button() call, default {}
        **kargs - used as **kargs argument in tkinter.Button() call

        Note the command entry in kargs, if there is one, for use in
        bind_frame_button method.

        """
        self.button = tkinter.Button(
            master=parent.get_tab_buttons_frame(),
            cnf={} if cnf is None else cnf,
        )
        super().__init__(**kargs)

        self.command = kargs.get("command")

        tags = list(self.button.bindtags())
        tags.insert(0, parent.explicit_focus_tag)
        self.button.bindtags(tuple(tags))

    def bind_frame_button(self, tab):
        """Bind button command to tab in Alt-key style."""
        conf = self.button.configure()
        underline = conf["underline"][-1]
        text = conf["text"][-1]
        if isinstance(text, tuple):
            text = " ".join(text)
        try:
            if not underline < 0:
                tab.panel.bind(
                    sequence="".join(
                        ("<Alt-KeyPress-", text[underline].lower(), ">")
                    ),
                    func=self.try_event(self.command),
                    add=True,
                )
        except:
            pass

    def make_command(self, command, tab):
        """Bind command(tab) to button for KeyPress-Return and mouse click."""

        def on_click(event=None):
            command(tab)

        self.command = on_click
        self.button.configure(command=self.try_command(on_click, self.button))
        self.button.bind(
            sequence="<KeyPress-Return>",
            func=self.try_event(on_click),
            add=True,
        )

    def unbind_frame_button(self, tab):
        """Unbind button command from tab in Alt-key style."""
        conf = self.button.configure()
        underline = conf["underline"][-1]
        text = conf["text"][-1]
        if isinstance(text, tuple):
            text = " ".join(text)
        try:
            if not underline < 0:
                tab.panel.bind(
                    sequence="".join(
                        ("<Alt-KeyPress-", text[underline].lower(), ">")
                    )
                )
        except:
            pass


class AppSysFrame(Bindings):
    """Provide container for tabs of a notebook style user interface.

    The main frame of an application. Contains a frame for buttons that
    switch between the detail frames (panels) of application and a frame
    that contains the selected panel.

    Tabs are defined but not created by the CreateTab method.  A tab is
    created if it does not exist when the associated tab button is invoked.
    A set of actions that cause the tab to be created may be identified in
    define_tab.  A set of actions that cause the tab to be destroyed may
    be given in define_tab.

    A tab, and the tab buttons for the associated state, are not displayed
    if creation of the tab is a consequence of an action that does not
    alter the current state.  The current state is defined by the set of
    tabs displayed.

    """

    explicit_focus_tag = "explicitfocus"

    def __init__(self, master=None, cnf=None, **kargs):
        """Define the basic structure of the notebook-like application.

        Subclasses define the tabs and their interactions.

        The following arguments are passed on to Tkinter.Frame
        cnf = Tkinter.Frame configuration, default {}
        **kargs = Tkinter.Frame arguments.

        """
        if cnf is None:
            cnf = {}
        self._frame = tkinter.Frame(master=master, cnf=cnf)
        self._datasources = DataRegister()
        super().__init__(**kargs)

        self._tab_description = dict()
        self._tab_order = []
        self._tab_state = dict()
        self._switch_state = dict()
        self._tabs = dict()
        self._state = None
        self._current_tab = None

        # create frames for tab switching buttons and tab but leave mapping
        # to screen until a tab is actually created
        self._tab_button_frame = tkinter.Frame(master=self._frame)
        # _TAB_FRAME
        # self._tab_frame = Tkinter.Frame(master=self._frame)

        # Hook for tab __init__ keyword arguments
        self._tab_init_kwargs = None

    def create_tabs(self):
        """Create tab buttons and attach tab switching commands.

        Tab buttons are along top side of frame and switch the tab (notebook
        page) that is displayed.  If the tab does not exist when the button
        is clicked, it is created.  This method does not create the tab.

        """
        for i, j, tab in sorted(self._tab_order):
            if tab not in self._tabs:
                self._tabs[tab] = AppSysTab(
                    parent=self, description=self._tab_description[tab]
                )
                self._tabs[tab].bind_tab_button(self.show_current_tab)

    def get_data_register(self):
        """Return the data register object.

        Tabs should use this interface to register their widgets for update
        notification.

        """
        return self._datasources

    def define_state_transitions(self, tab_state=None, switch_state=None):
        """Define tab navigation for application.

        Subclasses must extend this method to define the application's
        navigation between tabs.  Each tab, an AppSysPanel instance, has
        a set of buttons along its bottom edge which can be used to do
        actions, switch to another tab, or both.

        tab_state - dictionary containning application states as the panels
                    to be available for display and the panel switching
                    buttons displayed.

        switch_state - dictionary containing state changes for application.

        A switch_state looks like:
        {..,(<current state>,<panel button>):[<new state>,<new panel>],..}.

        <current state> and <new state> values must be keys in tab_state.

        """
        if isinstance(tab_state, dict):
            self._tab_state.update(tab_state)
        if isinstance(switch_state, dict):
            self._switch_state.update(switch_state)

    def define_tab(
        self,
        identity,
        text="",
        tooltip="",
        underline=-1,
        tabclass=None,
        position=-1,
        create_actions=None,
        destroy_actions=None,
    ):
        """Create a tab description.

        see AppSysTab for description of remaining arguments.

        It is sensible to ensure that the order of buttons in _tab_order is
        the same as the order of buttons in _tab_state entries.

        """
        if identity in self._tab_description:
            for i in range(len(self._tab_order)):
                tab = self._tab_order.pop(0)
                if tab[-1] != identity:
                    self._tab_order.append(tab)
        if position < 0:
            self._tab_order.append(
                (len(self._tab_order), len(self._tab_order), identity)
            )
        else:
            self._tab_order.append((position, len(self._tab_order), identity))
        self._tab_description[identity] = AppSysTabDefinition(
            identity=identity,
            text=text,
            tooltip=tooltip,
            tabclass=tabclass,
            underline=underline,
            create_actions=create_actions,
            destroy_actions=destroy_actions,
        )

    def get_tab_buttons_frame(self):
        """Return Frame containing tab buttons."""
        return self._tab_button_frame

    def get_state(self):
        """Return current location in tab navigation map."""
        return self._state

    def get_current_tab(self):
        """Return name of tab currently displayed."""
        return self._current_tab

    def get_tab_data(self, tab):
        """Return object which implements widget named tab."""
        try:
            return self._tabs[tab].tab
        except:
            return None

    def get_widget(self):
        """Return the Frame containing application."""
        return self._frame

    def is_state_switch_allowed(self, button):
        """Return True if button is allowed to switch out of current state."""
        return (self._state, button) in self._switch_state

    def set_state(self, state):
        """Set location in tab navigation map to state."""
        self._state = state

    def set_kwargs_for_next_tabclass_call(self, keyword_arguments):
        """Set the keyword arguments to be used in next tabclass call."""
        self._tab_init_kwargs = keyword_arguments

    def set_current_tab(self, tab):
        """Set tab currently displayed to tab."""
        self._current_tab = tab

    def show_current_tab(self, tab):
        """Hide displayed tab then make tab current and display it.

        This method is the command for the AppSysFrame buttons but can be
        used separately.

        """
        self._hide_buttons()
        self._hide_tab()
        self._make_tab(tab)
        self.set_current_tab(tab)
        self._show_tab()
        self._show_buttons()

    def show_state(self, eid=None):
        """Change the displayed tab as directed by eid.

        This method is similar to show_current_tab but takes into account
        the current location in the navigation map and the event (usually
        a button click or equivalent) when choosing the new tab.

        Assumes that the AppSysPanel subclass defines a close method.

        """
        self._hide_buttons()
        state, tab = self._switch_state[(self._state, eid)]
        if state is not None:
            self._hide_tab()
            for k in self._tabs.values():
                # destroy tabs from AppSysTabDefinition.destroy_actions
                if eid in k.description.destroy_actions:
                    if k.tab is not None:
                        k.tab.close()
                        k.tab = None
                # create tabs from AppSysTabDefinition.create_actions
                if eid in k.description.create_actions:
                    self._make_tab(k.description.identity)
            self._make_tab(tab)
            self.set_state(state)
            # display the tab if it is one displayable in new state ??????
            if tab in self._tab_state[state]:
                self.set_current_tab(tab)
                self._show_tab()
            # forget frame containing tab switching buttons and tab if no tab
            # exists
            for k in self._tabs.values():
                if k.tab is not None:
                    break
            else:
                if self._tab_button_frame.winfo_ismapped() == 1:
                    self._tab_button_frame.pack_forget()
                # _TAB_FRAME
            self._show_buttons()

    def switch_context(self, button):
        """Provide switch_context interface to show_state for AppSysPanel.

        This allows AppSysPanel to call switch_context without worrying
        about whether it is calling an AppSysPanel or AppSysFrame method.
        If it is calling the AppSysFrame method show_state does the work.

        """
        self.show_state(eid=button)

    def _hide_buttons(self):
        """Hide the frame buttons."""
        for i, j, tab in self._tab_order:
            if self._current_tab:
                self._tabs[tab].button.unbind_frame_button(
                    self._tabs[self._current_tab].tab
                )
            self._tabs[tab].button.button.pack_forget()

    def _hide_tab(self):
        """Hide the current tab."""
        if self._state is None:
            return
        tab = self._current_tab
        if tab is None:
            return
        if self._tabs[tab].tab is None:
            return
        self._tabs[tab].tab.hide_panel()
        for k in self._frame.bind_class(self.explicit_focus_tag):
            self._frame.unbind_class(self.explicit_focus_tag, k)

    def _make_tab(self, tab):
        """Create tab if it does not exist."""
        if tab is None:
            return
        if self._tabs[tab].tab is not None:
            return
        # Assume some tab will be displayed if a tab is created so ensure
        # that tab switching buttons are displayed.  Actually need this even
        # if no tab is displayed so tabs can be accessed anyway
        if self._tab_button_frame.winfo_ismapped() == 0:
            self._tab_button_frame.pack(fill=tkinter.BOTH)
        # Add parent=self to self._tab_init_kwargs for tabclass call
        tabbuttontext = self._tab_description[tab].text
        kwargs = dict(parent=self)
        if self._tab_init_kwargs is not None:
            if isinstance(self._tab_init_kwargs, dict):
                try:
                    tabbuttontext = self._tab_init_kwargs.pop("tabtitle")
                except KeyError:
                    pass
                kwargs.update(self._tab_init_kwargs)
            self._tab_init_kwargs = None
        # Maybe pass the button to tabclass for setting button text?
        self._tabs[tab].button.button.configure(text=tabbuttontext)
        self._tabs[tab].tab = self._tab_description[tab].tabclass(**kwargs)

    def _show_buttons(self):
        """Show frame buttons for current location in navigation map."""
        for button in self._tab_state[self._state]:
            self._tabs[button].button.button.pack(side=tkinter.LEFT)
            if self._current_tab:
                self._tabs[button].button.bind_frame_button(
                    self._tabs[self._current_tab].tab
                )

    def _show_tab(self):
        """Show current tab and give it the focus."""
        tab = self._current_tab
        if tab is None:
            return
        # pack frame containing tab switch buttons and tab if any tab exists
        for value in self._tabs.values():
            if value.tab is not None:
                if value.description.identity in self._tab_state[self._state]:
                    # _TAB_FRAME
                    break
        self._tabs[tab].tab.show_panel()
        self._tabs[tab].tab.panel.focus_set()


# maybe combine AppSysTab and AppSysTabDefinition classes
class AppSysTab:
    """This class creates a tab using a tab definition."""

    def __init__(self, parent=None, description=None):
        """Create the tab's button in parent frame using the tab description.

        parent - an AppSysFrame instance
        description - an AppSysTabDefinition instance.

        """
        self.tab = None
        self.button = AppSysFrameButton(
            parent=parent,
            cnf=dict(text=description.text, underline=description.underline),
        )
        self.description = description

    def bind_tab_button(self, command):
        """Set bindings to raise tab to front of application.

        command - method to make tab visible, creating tab if necessary.

        """
        self.button.make_command(command, self.description.identity)


# Maybe combine AppSysTab and AppSysTabDefinition classes.
# Does this need to be subclass of ExceptionHandler or not?
# Maybe question now is about Bindings?
class AppSysTabDefinition:
    """This class describes a tab which can be included on an AppSysFrame."""

    def __init__(
        self,
        identity=None,
        text="",
        tooltip="",
        underline=-1,
        tabclass=None,
        position=-1,
        create_actions=None,
        destroy_actions=None,
    ):
        """Create tab definition.

        identity - arbitrary identity number for tab.
        text - text displayed on button associated with tab.
        tooltip - tooltip text for button.
        underline - text position underlined for Alt-<character> action.
        tabclass - class to instantiate to create tab.
        position - button place in tab order relative to other tab buttons.
                    <0 means add at end of list.
        create_actions - set of actions causing tabclass to be instantiated
                        if not already done.  The action causing creation
                        via the switch context method need not be in this
                        set.
        destroy_actions - set of actions causing the current instatiation of
                        tabclass to be destroyed.  All such actions must be
                        in this set.  tabclass must provide a close method
                        to tidy up before destruction.

        The actions are usually associated with an AppSysPanelButton or a
        MenuButton but never with an AppSysFrameButton.

        The identity must be unique within the application for tabs.  It is
        used to keep track of context while navigating the tabs.

        """
        self.identity = identity
        self.text = text
        self.tooltip = tooltip
        self.underline = underline
        self.tabclass = tabclass
        self.position = position
        try:
            self.create_actions = set(create_actions)
        except:
            self.create_actions = set()
        try:
            self.destroy_actions = set(destroy_actions)
        except:
            self.destroy_actions = set()
