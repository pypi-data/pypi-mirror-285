# panel.py
# Copyright 2007 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Provide base classes for pages in notebook style user interfaces.

The classes are written to work with the classes provided in the frame
module.

The *Grid* classes assume the solentware_grid.datagrid classes are available,
and behaviour is undefined if the solentware_grid package is not available.

"""

import tkinter

from solentware_bind.gui.bindings import Bindings


class AppSysPanelError(Exception):
    """Exception for AppSysPanel class."""


class AppSysPanelButton(Bindings):
    """Put a tkinter.Button in the frame of a parent reserved for buttons."""

    def __init__(
        self, parent=None, identity=None, switchpanel=None, cnf=None, **kargs
    ):
        """Create page action button.

        parent - parent AppSysPanel.
        identity - arbitrary identity number for button.
        switchpanel - if True button is allowed to change page in notebook.
        cnf - passed to tkinter.Button() as cnf argument, default {}.
        **kargs - passed to super().__init__() call as **kargs argument.

        The identity must be unique within the application for buttons.  It
        is used to keep track of context while navigating tabs.

        """
        self.parent = parent
        self.switchpanel = switchpanel
        self.identity = identity
        # The method must be invoked via the <ButtonPress-1> binding set in
        # bind_panel_button(), not via the tkinter.Button command argument,
        # and certainly not both routes.
        # Then all the relevant switch context stuff gets done too.
        # The pop() call replaces a get() call.
        # The fault was introduced at version 1.5 of solentware_misc when
        # moving the tkinter.Button arguments from **kargs to cnf, causing
        # several problems when event handlers were called twice rather
        # than once.
        self.command = cnf.pop("command", None)

        # When converted to tkinter.ttk.Button cnf will be passed as **cnf.
        self.button = tkinter.Button(
            master=parent.get_buttons_frame(),
            cnf={} if cnf is None else cnf,
        )
        super().__init__(**kargs)

        self.obeycontextswitch = True

        tags = list(self.button.bindtags())
        tags.insert(0, parent.get_appsys().explicit_focus_tag)
        self.button.bindtags(tuple(tags))

    def bind_panel_button(self):
        """Bind key and button events to button actions."""
        if self.switchpanel:

            def switch_context(event):
                # invoke the AppSysPanel or the AppSysFrame (via appsys
                # attribute of AppSysPanel) switch_context method
                self.parent.switch_context(button=self.identity)

        self.button.bind(
            sequence="".join(("<ButtonPress-1>")),
            func=self.try_event(self.command),
        )
        self.button.bind(
            sequence="<KeyPress-Return>", func=self.try_event(self.command)
        )
        if self.switchpanel:
            for method in (self.switch_context_check, switch_context):
                self.button.bind(
                    sequence="".join(("<ButtonPress-1>")),
                    func=self.try_event(method),
                    add=True,
                )
                self.button.bind(
                    sequence="<KeyPress-Return>",
                    func=self.try_event(method),
                    add=True,
                )

        conf = self.button.configure()
        underline = conf["underline"][-1]
        text = conf["text"][-1]
        if isinstance(text, tuple):
            text = " ".join(text)
        try:
            if not underline < 0:
                self.parent.get_widget().bind(
                    sequence="".join(
                        ("<Alt-KeyPress-", text[underline].lower(), ">")
                    ),
                    func=self.try_event(self.command),
                )
                if self.switchpanel:
                    for method in (self.switch_context_check, switch_context):
                        self.parent.get_widget().bind(
                            sequence="".join(
                                (
                                    "<Alt-KeyPress-",
                                    text[underline].lower(),
                                    ">",
                                )
                            ),
                            func=self.try_event(method),
                            add=True,
                        )
        except:
            print("AppSysPanelButton bind exception", self.identity)
            # pass

    def inhibit_context_switch(self):
        """Inhibit change of panel displayed.

        Usually called when validation before an action proceeds has not
        been passed.

        """
        self.obeycontextswitch = False

    def obey_context_switch(self):
        """Return self.obeycontextswitch value prior to setting it True.

        Validation may occur prior to performing an action.  obeycontextswitch
        should be True when an action is invoked and set False during
        validation if needed.  This method is used to check if navigation
        may proceed at end of validation and set obeycontextswitch True for
        the next action invoked.

        """
        switch, self.obeycontextswitch = self.obeycontextswitch, True
        return switch

    def raise_action_button(self):
        """Raise button in stacking order.

        When called for buttons in the order they appear on the panel gives
        a sensible tab order provided buttons are in a dedicated frame.

        """
        self.button.tkraise()

    def switch_context_check(self, event=None):
        """Return 'break' to tk interpreter if obey_context_switch()==False.

        In other words abandon processing the event.

        """
        if not self.obey_context_switch():
            return "break"
        return None

    def unbind_panel_button(self):
        """Unbind key and button events from button actions."""
        self.button.bind(sequence="".join(("<ButtonPress-1>")), func="")
        self.button.bind(sequence="<KeyPress-Return>", func="")

        conf = self.button.configure()
        underline = conf["underline"][-1]
        text = conf["text"][-1]
        if isinstance(text, tuple):
            text = " ".join(text)

        try:
            if not underline < 0:
                self.parent.get_widget().bind(
                    sequence="".join(
                        ("<Alt-KeyPress-", text[underline].lower(), ">")
                    ),
                    func="",
                )
        except:
            print("AppSysPanelButton unbind exception")
            # pass


class AppSysPanel(Bindings):
    """This is the base class for pages in a notebook style user interface.

    It provides the main frame of a page.  A frame for buttons that invoke
    actions is packed at bottom of page.  The rest of the page is filled by
    widgets providing application features.

    """

    def __init__(self, parent=None, cnf=None, **kargs):
        """Define basic structure of a page of a notebook style application.

        parent - AppSysFrame instance that owns this AppSysPanel instance.
        cnf - passed to main tkinter.Frame() call as cnf argument, default {}.
        **kargs - passed to super().__init__() call as **kargs argument.

        Subclasses define the content of the page and the action buttons.

        """
        if cnf is None:
            cnf = {}

        # When converted to tkinter.ttk.Frame cnf will be passed as **cnf.
        self.panel = tkinter.Frame(master=parent.get_widget(), cnf=cnf)

        self.buttons_frame = tkinter.Frame(master=self.panel)
        self._give_focus_widget = None
        self.buttons_frame.pack(side=tkinter.BOTTOM, fill=tkinter.X)

        self.appsys = parent

        self.button_definitions = {}
        self.button_order = []
        self.buttons = {}
        self.describe_buttons()
        super().__init__(**kargs)

    def close(self):
        """Raise AppSysPanelError('close not implemented') error.

        Subclasses must override this method.

        """
        raise AppSysPanelError("close not implemented")

    def create_buttons(self):
        """Create the action buttons defined for the page."""
        buttonrow = self.buttons_frame.pack_info()["side"] in ("top", "bottom")
        definitions = self.button_definitions
        for widget in self.buttons_frame.grid_slaves():
            widget.grid_forget()
        for i, button in enumerate(self.button_order):
            if button not in self.buttons:
                self.buttons[button] = AppSysPanelButton(
                    parent=self,
                    identity=button,
                    switchpanel=definitions[button][2],
                    cnf=dict(
                        text=definitions[button][0],
                        underline=definitions[button][3],
                        command=self.try_command(
                            definitions[button][4], self.buttons_frame
                        ),
                    ),
                )
            self.buttons[button].raise_action_button()
            self.buttons[button].bind_panel_button()
            if buttonrow:
                self.buttons_frame.grid_columnconfigure(i * 2, weight=1)
                self.buttons[button].button.grid_configure(
                    column=i * 2 + 1, row=0
                )
            else:
                self.buttons_frame.grid_rowconfigure(i * 2, weight=1)
                self.buttons[button].button.grid_configure(
                    row=i * 2 + 1, column=0
                )
        if buttonrow:
            self.buttons_frame.grid_columnconfigure(
                len(self.button_order * 2), weight=1
            )
        else:
            self.buttons_frame.grid_rowconfigure(
                len(self.button_order * 2), weight=1
            )

    def define_button(
        self,
        identity,
        text="",
        tooltip="",
        switchpanel=False,
        underline=-1,
        command=None,
        position=-1,
    ):
        """Define an action button for the page.

        identity - unique identification number for button
        text - text displayed on button
        tooltip - tooltip text for button (not used at present)
        switchpanel - if True button is allowed to change page in notebook
        underline - position in text for use in Alt-<character> invokation
                    <0 means no Alt binding
        command - function implementing button action.
        position - button position in tab order relative to other buttons
                    <0 means add at end of list

        """
        self.button_definitions[identity] = (
            text,
            tooltip,
            switchpanel,
            underline,
            command,
        )
        if identity in self.button_order:
            del self.button_order[self.button_order.index(identity)]
        if position < 0:
            self.button_order.append(identity)
        else:
            self.button_order.insert(position, identity)

    def describe_buttons(self):
        """Do nothing.  Subclasses should extend this method.

        Subclasses should extend this method to do a sequence of
        self.define_button(...) calls.
        AppSysPanel.__init__ calls self.describe_buttons()

        """

    def explicit_focus_bindings(self):
        """Do nothing.  Subclasses should extend this method.

        Subclasses should extend this method to set up event bindings for
        the page.
        AppSysPanel.show_panel calls self.explicit_focus_bindings()

        """

    def get_appsys(self):
        """Return application object."""
        return self.appsys

    def get_buttons_frame(self):
        """Return frame containing action buttons."""
        return self.buttons_frame

    def get_context(self):
        """Return None.  Context replaced by location in navigation map."""
        return

    def get_widget(self):
        """Return Tkinter.Frame containing all widgets for page."""
        return self.panel

    def give_focus(self, widget=None):
        """Set widget to be given focus when page is displayed."""
        self._give_focus_widget = widget

    def hide_panel(self):
        """Remove page from display."""
        self.panel.pack_forget()

    def hide_panel_buttons(self):
        """Remove event bindings for action buttons."""
        for button in self.buttons:
            self.buttons[button].unbind_panel_button()
        del self.button_order[:]

    def inhibit_context_switch(self, button):
        """Prevent next attempt to change context for button succeeding."""
        self.buttons[button].inhibit_context_switch()

    def make_explicit_focus_bindings(self, bindings):
        """Define bindings to change focus to grid from buttons."""

        def focus_bindings():
            for sequence, function in bindings.items():
                self.get_widget().bind_class(
                    self.get_appsys().explicit_focus_tag,
                    sequence=sequence,
                    func=function,
                    add=None,
                )

        self.explicit_focus_bindings = focus_bindings

    def refresh_controls(self, widgets=None):
        """Notify all widgets registered for update notification.

        widgets = [DataClient instance | (db, file, index), ...]

        When widget is a DataClient the current DataSource is used if there
        is not an entry in DataRegister naming a callback.
        Naming the source by (db, file, index) causes refresh to happen
        only if the DataClient is registered.
        Calling DataSource.refresh_widgets refreshes all DataClients with
        that DataSource.

        DataClient, DataRegister, and DataSource, are classes defined in
        the solentware_grid package.

        """
        if widgets is None:
            return

        dataregister = self.get_appsys().get_data_register()
        datasources = set()
        databases = set()
        for widget in widgets:
            if not isinstance(widget, tuple):
                if not dataregister.datasources:
                    datasources.add(widget.datasource)
                else:
                    databases.add(
                        (
                            widget.datasource.dbhome,
                            widget.datasource.dbset,
                            widget.datasource.dbname,
                        )
                    )
            elif len(dataregister.datasources):
                databases.add(widget)
        for k in datasources:
            k.refresh_widgets(None)
        for k in databases:
            dataregister.refresh_after_update(k, None)

    def show_panel(self):
        """Pack page and button frames and define event bindings."""
        self.explicit_focus_bindings()
        self.panel.pack(fill=tkinter.BOTH, expand=True)
        if self._give_focus_widget is None:
            self.panel.focus_set()
        else:
            self._give_focus_widget.focus_set()

    def show_panel_buttons(self, buttons):
        """Ensure all action buttons for page are visible."""
        for button in buttons:
            if button in self.button_definitions:
                if button not in self.button_order:
                    self.button_order.append(button)

    def switch_context(self, button):
        """Call the application switch_context method."""
        # Could build this call directly into the switch_context function
        # built in AppSysButton. The parent argument to AppSysButton is
        # an AppSysPanel instance whose appsys attribute is the AppSysFrame
        # containing the context switch data structures.
        # But a hook at this point could be useful.
        self.appsys.switch_context(button)

    def __del__(self):
        """Call the close() method."""
        self.close()
        super().__del__()


class PlainPanel(AppSysPanel):
    """Base class for pages without grids in notebook style user interface."""

    def make_grids(self, gridarguments):
        """Raise exception because *grid* classes are not supported.

        Subclasses can use classes from solentware_grid, but must be
        responsible for managing them.
        """
        raise AppSysPanelError("solentware_grid *grid* classes not supported")


class PanelWithGrids(AppSysPanel):
    """Base class for pages with grids in a notebook style user interface.

    One or more grids may be put on the panel, with a record selector for
    each grid if the useselector argument is True.

    The record selector is a tkinter.Entry widget whose content is used to
    control the records shown in the grid.  Multiple selectors are put in
    a row at the top of the panel.

    Subclasses of PanelWithGrids may arrange grids and selectors differently.
    """

    def __init__(self, useselector=True, gridhorizontal=True, **kargs):
        """Create panel to which grids and selectors may be added.

        useselector - if True a selector is provided for each grid.
        gridhorizontal - if True grids are arranged horizontally.
        **kargs - passed to superclass as **kargs argument.

        Selectors are either present for all grids or absent for all grids.

        Grids are arranged horizontally or vertically.

        """
        super().__init__(**kargs)
        self.useselector = useselector is True
        self.gridhorizontal = gridhorizontal is True
        self.gridselector = dict()
        self.activegridhint = dict()

    def add_grid_to_panel(
        self,
        gridmaster,
        selector,
        grid=None,
        selectlabel=None,
        gridfocuskey=None,
        selectfocuskey=None,
        keypress_grid_to_select=True,
        **kargs
    ):
        """Add selector and grid to panel.

        gridmaster - to be passed as master argument in grid() call.
        selector - the grid's selector instance (a tkinter.Entry widget).
        grid - class or function to create the grid.
        selectlabel - the text displayed as the selector's name.
        gridfocuskey - sequence to give keyboard focus to grid.
        selectfocuskey - sequence to give keyboard focus to grid's selector.
        keypress_grid_to_select - if True pressing a key while grid has
                                keyboard focus switches keyboard focus to
                                grid's selector.
        **kargs - not used.

        The gridfocuskey and selectfocuskey sequences switch the keyboard
        focus to the grid and selector respectively from any widget in
        the panel.

        The gridmaster argument is usually self.frame.
        """
        gridframe = grid(
            parent=gridmaster,
            selecthintlabel=selectlabel,
            appsyspanel=self,
            receivefocuskey=gridfocuskey,
            focus_selector=selectfocuskey,
            keypress_grid_to_select=keypress_grid_to_select,
        )
        if selector:
            (
                self.activegridhint[gridframe],
                self.gridselector[gridframe],
            ) = selector
            gridframe.set_select_hint_label()
        return gridframe

    def clear_selector(self, grid):
        """Clear the record selector tkentry.Entry widget for grid.

        grid - a solentware_grid.DataGrid instance.
        """
        if grid is True:
            for widget in set(self.gridselector.values()):
                widget.delete(0, tkinter.END)
        else:
            widget = self.gridselector.get(grid)
            if widget is not None:
                widget.delete(0, tkinter.END)

    def get_active_grid_hint(self, grid):
        """Return Tkinter.Label for grid.

        grid - a solentware_grid.DataGrid instance.
        """
        return self.activegridhint.get(grid)

    def get_grid_selector(self, grid):
        """Return Tkinter.Entry containing selection text for grid.

        grid - a solentware_grid.DataGrid instance.
        """
        return self.gridselector.get(grid)

    def set_panels_grid_bindings(self, grids, gridarguments):
        """Set grid navigation bindings for grids on page."""
        # Each grid sets bindings to switch focus to all the other grids
        gridargs = list(gridarguments)
        for i in range(len(grids)):
            widget = grids.pop(0)
            gargs = gridargs.pop(0)
            widget.grid_bindings(grids, gridargs, **gargs)
            grids.append(widget)
            gridargs.append(gargs)
        bindmap = {}
        for gargs, widget in zip(gridarguments, grids):
            bindmap[gargs["gridfocuskey"]] = widget.focus_to_grid
        self.make_explicit_focus_bindings(bindmap)


class PanelGridSelector(PanelWithGrids):
    """Display data grids in equal share of space next to their selectors."""

    def __init__(self, **kargs):
        """Delegate to superclass then create Tkinter.Frame widget.

        **kargs - passed to superclass as **kargs argument.

        The extra widget in the hierarchy adjusts the behaviour of the
        widgets when the application is resized.
        """
        super().__init__(**kargs)

        self.gridpane = tkinter.Frame(master=self.get_widget())
        self.gridpane.pack(
            side=tkinter.TOP, expand=tkinter.TRUE, fill=tkinter.BOTH
        )

    def make_grids(self, gridarguments):
        """Create data grids and selectors controlled by grid geometry manager.

        gridarguments is a list of dictionaries of arguments for method
        add_grid_to_panel.

        The creation order of widgets is chosen to cause a selector widget
        to disappear after the associated data grid, which is adjacent above
        or below, and to cause widgets lower in the application window to
        disappear before higher ones; except panel buttons are the last of
        the panel widgets to go when the application is resized smaller.

        Selector widgets are fixed size and data grid widgets grow and
        shrink equally to fill the remaining space in the application
        window.

        """

        def make_selector(arg):
            if arg.get("selectfocuskey") is None:
                return (None, None)
            frame = tkinter.Frame(master=self.gridpane)
            label = tkinter.Label(master=frame)
            entry = tkinter.Entry(master=frame)
            return (frame, (label, entry))

        grids = []
        for i, gargs in enumerate(gridarguments):
            selector, selector_widgets = make_selector(gargs)
            grids.append(
                self.add_grid_to_panel(
                    self.gridpane, selector_widgets, **gargs
                )
            )
            gframe = grids[-1]
            if selector:
                selector.grid_columnconfigure(0, weight=1)
                self.activegridhint[gframe].grid(column=0, row=0, sticky="nes")
                selector.grid_columnconfigure(1, weight=1)
                self.gridselector[gframe].grid(column=1, row=0, sticky="nsw")
                if self.gridhorizontal:
                    if self.useselector:
                        selector.grid(column=i, row=0, sticky="nesw")
                    else:
                        selector.grid(column=i, row=1, sticky="nesw")
                elif self.useselector:
                    self.gridpane.grid_rowconfigure(
                        i * 2, weight=0, uniform="select"
                    )
                    selector.grid(column=0, row=i * 2, sticky="nesw")
                else:
                    self.gridpane.grid_rowconfigure(
                        i * 2 + 1, weight=0, uniform="select"
                    )
                    selector.grid(column=0, row=i * 2 + 1, sticky="nesw")
            if self.gridhorizontal:
                self.gridpane.grid_columnconfigure(i, weight=1, uniform="data")
                if self.useselector:
                    gframe.get_frame().grid(column=i, row=1, sticky="nesw")
                else:
                    gframe.get_frame().grid(column=i, row=0, sticky="nesw")
            elif self.useselector:
                self.gridpane.grid_rowconfigure(
                    i * 2 + 1, weight=1, uniform="data"
                )
                gframe.get_frame().grid(column=0, row=i * 2 + 1, sticky="nesw")
            else:
                self.gridpane.grid_rowconfigure(
                    i * 2, weight=1, uniform="data"
                )
                gframe.get_frame().grid(column=0, row=i * 2, sticky="nesw")
        if self.gridhorizontal:
            self.gridpane.grid_rowconfigure(1, weight=1)
        else:
            self.gridpane.grid_columnconfigure(0, weight=1)

        self.set_panels_grid_bindings(grids, gridarguments)
        if grids:
            self.give_focus(grids[0].get_frame())
        return grids


class PanelGridSelectorBar(PanelWithGrids):
    """Display data grids in equal share of space with selectors in own row."""

    def __init__(self, **kargs):
        """Delegate to superclass then create Tkinter.Frame widget.

        **kargs - passed to superclass as **kargs argument.

        The extra widget in the hierarchy adjusts the behaviour of the
        widgets when the application is resized.
        """
        super().__init__(**kargs)

        self.gridpane = tkinter.Frame(master=self.get_widget(), cnf={})
        self.gridpane.pack(
            side=tkinter.TOP, expand=tkinter.TRUE, fill=tkinter.BOTH
        )

    def make_grids(self, gridarguments):
        """Create data grids and selectors controlled by grid geometry manager.

        gridarguments is a list of dictionaries of arguments for method
        add_grid_to_panel.

        Selector widgets are in a row above or below all data grid widgets.

        The creation order of widgets is chosen to cause the row of selector
        widgets to disappear after all the data grids and to cause widgets
        lower in the application window to disappear before higher ones;
        except panel buttons are the last of the panel widgets to go when
        the application is resized smaller.

        Selector widgets are fixed size and data grid widgets grow and
        shrink equally to fill the remaining space in the application
        window.

        """

        def make_selector(arg):
            if arg.get("selectfocuskey") is None:
                return (None, None)
            frame = tkinter.Frame(master=self.gridpane)
            label = tkinter.Label(master=frame)
            entry = tkinter.Entry(master=frame)
            return (frame, (label, entry))

        gsize = len(gridarguments)
        grids = []
        for i, gargs in enumerate(gridarguments):
            selector, selector_widgets = make_selector(gargs)
            grids.append(
                self.add_grid_to_panel(
                    self.gridpane, selector_widgets, **gargs
                )
            )
            gframe = grids[-1]
            if selector:
                selector.grid_columnconfigure(0, weight=1)
                self.activegridhint[gframe].grid(column=0, row=0, sticky="nes")
                selector.grid_columnconfigure(1, weight=1)
                self.gridselector[gframe].grid(column=1, row=0, sticky="nsw")
                if self.useselector:
                    selector.grid(column=i, row=0, sticky="nesw")
                else:
                    selector.grid(column=i, row=gsize, sticky="nesw")
                if not self.gridhorizontal:
                    self.gridpane.grid_columnconfigure(
                        i, weight=1, uniform="select"
                    )
            if self.gridhorizontal:
                self.gridpane.grid_columnconfigure(i, weight=1, uniform="data")
                if self.useselector:
                    gframe.get_frame().grid(column=i, row=1, sticky="nesw")
                else:
                    gframe.get_frame().grid(column=i, row=0, sticky="nesw")
            else:
                if self.useselector:
                    row = i + 1
                else:
                    row = i
                gframe.get_frame().grid(
                    column=0, row=row, sticky="nesw", columnspan=gsize
                )
                self.gridpane.grid_rowconfigure(row, weight=1, uniform="data")
        if self.gridhorizontal:
            if self.useselector:
                self.gridpane.grid_rowconfigure(1, weight=1)
            else:
                self.gridpane.grid_rowconfigure(0, weight=1)

        self.set_panels_grid_bindings(grids, gridarguments)
        if grids:
            self.give_focus(grids[0].get_frame())
        return grids


class PanelGridSelectorShared(PanelWithGrids):
    """Display data grids in equal share of space with a shared selector."""

    def __init__(self, **kargs):
        """Delegate to superclass then create Tkinter.Frame widget.

        **kargs - passed to superclass as **kargs argument.

        The extra widget in the hierarchy adjusts the behaviour of the
        widgets when the application is resized.
        """
        super().__init__(**kargs)

        self.gridpane = tkinter.Frame(master=self.get_widget())
        self.gridpane.pack(
            side=tkinter.TOP, expand=tkinter.TRUE, fill=tkinter.BOTH
        )

    def make_grids(self, gridarguments):
        """Create data grids and selectors controlled by grid geometry manager.

        gridarguments is a list of dictionaries of arguments for method
        add_grid_to_panel.

        The selector widget is shared by the data grid widgets and is on a
        row above or below all the data grids.

        The creation order of widgets is chosen to cause the row with the
        selector widget to disappear after all the data grids and to cause
        widgets lower in the application window to disappear before higher
        ones; except panel buttons are the last of the panel widgets to go
        when the application is resized smaller.

        Selector widgets are fixed size and data grid widgets grow and
        shrink equally to fill the remaining space in the application
        window.

        """
        for gargs in gridarguments:
            if gargs.get("selectfocuskey"):

                def csf():
                    frame = tkinter.Frame(master=self.gridpane)
                    label = tkinter.Label(master=frame)
                    entry = tkinter.Entry(master=frame)

                    def rcsf():
                        return (frame, (label, entry))

                    return rcsf

                make_selector = csf()
                break
        else:

            def make_selector():
                return (None, None)

        selector, selector_widgets = make_selector()
        gsize = len(gridarguments)
        grids = []
        for i, gargs in enumerate(gridarguments):
            grids.append(
                self.add_grid_to_panel(
                    self.gridpane, selector_widgets, **gargs
                )
            )
            gframe = grids[-1]
            if self.gridhorizontal:
                self.gridpane.grid_columnconfigure(i, weight=1, uniform="data")
                if self.useselector:
                    gframe.get_frame().grid(column=i, row=1, sticky="nesw")
                else:
                    gframe.get_frame().grid(column=i, row=0, sticky="nesw")
            else:
                if self.useselector:
                    row = i + 1
                else:
                    row = i
                gframe.get_frame().grid(
                    column=0, row=row, sticky="nesw", columnspan=gsize
                )
                self.gridpane.grid_rowconfigure(row, weight=1, uniform="data")
        if selector:
            selector.grid_columnconfigure(0, weight=1)
            selector_widgets[0].grid(column=0, row=0, sticky="nes")
            selector.grid_columnconfigure(1, weight=1)
            selector_widgets[1].grid(column=1, row=0, sticky="nsw")
            if self.useselector:
                if self.gridhorizontal:
                    selector.grid(
                        column=0, row=0, sticky="nesw", columnspan=gsize
                    )
                else:
                    selector.grid(column=0, row=0, sticky="nesw")
            elif self.gridhorizontal:
                selector.grid(
                    column=0, row=gsize, sticky="nesw", columnspan=gsize
                )
            else:
                selector.grid(column=0, row=gsize, sticky="nesw")
        if self.gridhorizontal:
            if self.useselector:
                self.gridpane.grid_rowconfigure(1, weight=1)
            else:
                self.gridpane.grid_rowconfigure(0, weight=1)
        else:
            self.gridpane.grid_columnconfigure(0, weight=1)

        self.set_panels_grid_bindings(grids, gridarguments)
        if grids:
            self.give_focus(grids[0].get_frame())
            if selector:
                grids[0].bind_return(setbinding=True)
        return grids


class PanedPanelGridSelector(PanelWithGrids):
    """Display data grids in adjustable space next to their selectors."""

    def __init__(self, **kargs):
        """Delegate to superclass then create Tkinter.PanedWindow widget.

        **kargs - passed to superclass as **kargs argument.

        The extra widget in the hierarchy adjusts the behaviour of the
        widgets when the application is resized.
        """
        super().__init__(**kargs)

        if self.gridhorizontal:
            orient = tkinter.HORIZONTAL
        else:
            orient = tkinter.VERTICAL
        self.gridpane = tkinter.PanedWindow(
            master=self.get_widget(), opaqueresize=tkinter.FALSE, orient=orient
        )
        self.gridpane.pack(side=tkinter.TOP, expand=True, fill=tkinter.BOTH)

    def make_grids(self, gridarguments):
        """Create data grids and selectors controlled by paned window.

        gridarguments is a list of dictionaries of arguments for method
        add_grid_to_panel.

        The creation order of widgets is chosen to cause a selector widget
        to disappear after the associated data grid, which is adjacent above
        or below, and to cause widgets lower in the application window to
        disappear before higher ones; except panel buttons are the last of
        the panel widgets to go when the application is resized smaller.

        Selector widgets are fixed size.  Data grid widgets are created with
        equal size each in a pane with the associated selector.  Extra space
        is added to the rightmost or bottommost pane and shrinking removes
        space in reverse order to add.  Panes can be resized by dragging the
        sash between two panes.

        """

        def make_selector(arg, master):
            if arg.get("selectfocuskey") is None:
                return (None, None)
            frame = tkinter.Frame(master=master)
            label = tkinter.Label(master=frame)
            entry = tkinter.Entry(master=frame)
            frame.grid_columnconfigure(0, weight=1)
            label.grid(column=0, row=0, sticky="nes")
            frame.grid_columnconfigure(1, weight=1)
            entry.grid(column=1, row=0, sticky="nsw")
            return (frame, (label, entry))

        grids = []
        for gargs in gridarguments:
            gridmaster = tkinter.Frame(master=self.gridpane)
            selector, selector_widgets = make_selector(gargs, gridmaster)
            grids.append(
                self.add_grid_to_panel(gridmaster, selector_widgets, **gargs)
            )
            gframe = grids[-1]
            if self.useselector:
                if selector:
                    selector.pack(side=tkinter.TOP, fill=tkinter.X)
                    gframe.bind_return(setbinding=True)
                gframe.get_frame().pack(
                    side=tkinter.TOP, fill=tkinter.BOTH, expand=tkinter.TRUE
                )
            else:
                gframe.get_frame().pack(
                    side=tkinter.TOP, fill=tkinter.BOTH, expand=tkinter.TRUE
                )
                if selector:
                    selector.pack(side=tkinter.TOP, fill=tkinter.X)
                    gframe.bind_return(setbinding=True)
            self.gridpane.add(gridmaster)

        self.set_panels_grid_bindings(grids, gridarguments)
        if grids:
            self.give_focus(grids[0].get_frame())
        return grids


class PanedPanelGridSelectorBar(PanelWithGrids):
    """Display data grids in adjustable space with selectors in own row."""

    def __init__(self, **kargs):
        """Delegate to superclass then create Tkinter.PanedWindow widget.

        **kargs - passed to superclass as **kargs argument.

        The extra widget in the hierarchy adjusts the behaviour of the
        widgets when the application is resized.
        """
        super().__init__(**kargs)

        if self.gridhorizontal:
            orient = tkinter.HORIZONTAL
        else:
            orient = tkinter.VERTICAL
        self.gridpane = tkinter.PanedWindow(
            master=self.get_widget(), opaqueresize=tkinter.FALSE, orient=orient
        )
        self.selectormaster = tkinter.Frame(master=self.get_widget())
        if self.useselector:
            self.selectormaster.pack(side=tkinter.TOP, fill=tkinter.X)
            self.gridpane.pack(
                side=tkinter.BOTTOM, expand=tkinter.TRUE, fill=tkinter.BOTH
            )
        else:
            self.selectormaster.pack(side=tkinter.BOTTOM, fill=tkinter.X)
            self.gridpane.pack(
                side=tkinter.TOP, expand=tkinter.TRUE, fill=tkinter.BOTH
            )

    def make_grids(self, gridarguments):
        """Create data grids and selectors controlled by paned window.

        gridarguments is a list of dictionaries of arguments for method
        add_grid_to_panel.

        Selector widgets are in a row above or below all the data grid
        widgets not controlled by panes.

        The creation order of widgets is chosen to cause the row of selector
        widgets to disappear after all the data grids.  The panel buttons
        are the last of the panel widgets to go when the application is
        resized smaller.

        Selector widgets are fixed size.  Data grid widgets are created with
        equal size each in a separate pane.  Extra space is added to the
        rightmost or bottommost pane and shrinking removes space in reverse
        order to add.  Panes can be resized by dragging the sash between two
        panes.

        """

        def make_selector(arg, col):
            if arg.get("selectfocuskey") is None:
                return (None, None)
            label = tkinter.Label(master=self.selectormaster)
            entry = tkinter.Entry(master=self.selectormaster)
            self.selectormaster.grid_columnconfigure(col * 2, weight=1)
            label.grid(column=col * 2, row=0, sticky="nes")
            self.selectormaster.grid_columnconfigure(col * 2 + 1, weight=1)
            entry.grid(column=col * 2 + 1, row=0, sticky="nsw")
            return (self.selectormaster, (label, entry))

        selector = False
        grids = []
        for i, gargs in enumerate(gridarguments):
            selector, selector_widgets = make_selector(gargs, i)
            grids.append(
                self.add_grid_to_panel(
                    self.gridpane, selector_widgets, **gargs
                )
            )
            gframe = grids[-1]
            self.gridpane.add(gframe.get_frame())
        if not selector:
            self.selectormaster.pack_forget()

        self.set_panels_grid_bindings(grids, gridarguments)
        if grids:
            self.give_focus(grids[0].get_frame())
            if selector:
                grids[0].bind_return(setbinding=True)
        return grids


class PanedPanelGridSelectorShared(PanelWithGrids):
    """Display data grids in adjustable space with a shared selector."""

    def __init__(self, **kargs):
        """Delegate to superclass then create Tkinter.PanedWindow widget.

        **kargs - passed to superclass as **kargs argument.

        The extra widget in the hierarchy adjusts the behaviour of the
        widgets when the application is resized.
        """
        super().__init__(**kargs)

        if self.gridhorizontal:
            orient = tkinter.HORIZONTAL
        else:
            orient = tkinter.VERTICAL
        self.gridpane = tkinter.PanedWindow(
            master=self.get_widget(), opaqueresize=tkinter.FALSE, orient=orient
        )
        self.selectormaster = tkinter.Frame(master=self.get_widget())
        if self.useselector:
            self.selectormaster.pack(side=tkinter.TOP, fill=tkinter.X)
            self.gridpane.pack(
                side=tkinter.BOTTOM, expand=tkinter.TRUE, fill=tkinter.BOTH
            )
        else:
            self.selectormaster.pack(side=tkinter.BOTTOM, fill=tkinter.X)
            self.gridpane.pack(
                side=tkinter.TOP, expand=tkinter.TRUE, fill=tkinter.BOTH
            )

    def make_grids(self, gridarguments):
        """Create data grids and selectors controlled by paned window.

        gridarguments is a list of dictionaries of arguments for method
        add_grid_to_panel.

        The selector widget is shared by the data grid widgets and is on a
        row above or below all the data grids.

        The creation order of widgets is chosen to cause the row with the
        selector widget to disappear after all the data grids.  The panel
        buttons are the last of the panel widgets to go when the application
        is resized smaller.

        The selector widget is fixed size and data grid widgets are created
        with equal size each in a separate pane.  Extra space is added to
        the rightmost or bottommost pane and shrinking removes space in
        reverse order to add.  Panes can be resized by dragging the sash
        between two panes.

        """
        for gargs in gridarguments:
            if gargs.get("selectfocuskey"):

                def csf():
                    label = tkinter.Label(master=self.selectormaster)
                    entry = tkinter.Entry(master=self.selectormaster)
                    self.selectormaster.grid_columnconfigure(0, weight=1)
                    label.grid(column=0, row=0, sticky="nes")
                    self.selectormaster.grid_columnconfigure(1, weight=1)
                    entry.grid(column=1, row=0, sticky="nsw")

                    def rcsf():
                        return (self.selectormaster, (label, entry))

                    return rcsf

                make_selector = csf()
                break
        else:

            def make_selector():
                return (None, None)

        selector, selector_widgets = make_selector()
        grids = []
        for gargs in gridarguments:
            grids.append(
                self.add_grid_to_panel(
                    self.gridpane, selector_widgets, **gargs
                )
            )
            gframe = grids[-1]
            self.gridpane.add(gframe.get_frame())
        if not selector:
            self.selectormaster.pack_forget()

        self.set_panels_grid_bindings(grids, gridarguments)
        if grids:
            self.give_focus(grids[0].get_frame())
            if selector:
                grids[0].bind_return(setbinding=True)
        return grids
