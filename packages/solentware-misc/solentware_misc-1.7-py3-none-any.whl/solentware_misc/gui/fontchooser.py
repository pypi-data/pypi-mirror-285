# fontchooser.py
# Copyright 2009 Roger Marsh
# License: See LICENSE.TXT (BSD license)

"""This module provides the AppSysFontChooser class.

It displays a dialogue for choosing a font in a tkinter.Toplevel widget.

"""

import tkinter
import tkinter.font
import tkinter.messagebox

from solentware_bind.gui.bindings import Bindings
from solentware_bind.gui.exceptionhandler import FOCUS_ERROR


class AppSysFontChooser(Bindings):
    """Display a dialogue for choosing a font and it's properties.

    Call the get_chosen_font() method to get the chosen font.

    """

    restore_focus = None

    def __init__(self, master=None, title=None, cnf=None, **kargs):
        """Create the font chooser dialogue.

        master - the parent widget of the dialogue
        title - the title of the dialogue
        cnf - not used (cnf argument in tkinter.Toplevel call), default {}.
        kargs - not used (intended as argments in tkinter.Toplevel call)

        """
        super().__init__(**kargs)
        self.chosenfont = None

        self.confirm = tkinter.Toplevel(master)
        self.confirm.wm_title(title)
        self.buttons_frame = tkinter.Frame(master=self.confirm)
        self.buttons_frame.pack(side=tkinter.BOTTOM, fill=tkinter.X)
        self.create_buttons()

        self.fontpanel = framefonts = tkinter.Frame(self.confirm)
        self.families = tkinter.Listbox(framefonts)
        scrollfont = tkinter.Scrollbar(framefonts)
        scrollfont.configure(
            command=self.try_command(self.families.yview, scrollfont)
        )
        self.families.configure(
            yscrollcommand=self.try_command(scrollfont.set, self.families)
        )
        for font_family in sorted(tkinter.font.families()):
            self.families.insert(tkinter.END, font_family)
        self.families.pack(
            side=tkinter.LEFT, expand=tkinter.TRUE, fill=tkinter.X
        )
        scrollfont.pack(side=tkinter.LEFT, fill=tkinter.Y)
        framefonts.pack(fill=tkinter.X)

        wssf = tkinter.Frame(master=self.confirm)
        self.weight = tkinter.IntVar()
        self.slant = tkinter.IntVar()
        self.normal = tkinter.Radiobutton(
            master=wssf,
            text="Normal",
            variable=self.weight,
            value=1,
            command=self.try_command(self.on_show_font, wssf),
        )
        self.bold = tkinter.Radiobutton(
            master=wssf,
            text="Bold",
            variable=self.weight,
            value=2,
            command=self.try_command(self.on_show_font, wssf),
        )
        self.roman = tkinter.Radiobutton(
            master=wssf,
            text="Roman",
            variable=self.slant,
            value=1,
            command=self.try_command(self.on_show_font, wssf),
        )
        self.italic = tkinter.Radiobutton(
            master=wssf,
            text="Italic",
            variable=self.slant,
            value=2,
            command=self.try_command(self.on_show_font, wssf),
        )
        tkinter.Label(master=wssf, text="Size").grid_configure(column=1, row=3)
        self.normal.grid_configure(column=0, row=0)
        self.bold.grid_configure(column=0, row=1)
        self.roman.grid_configure(column=2, row=0)
        self.italic.grid_configure(column=2, row=1)
        wssf.grid_columnconfigure(0, weight=1)
        wssf.grid_columnconfigure(1, weight=1)
        wssf.grid_columnconfigure(2, weight=1)
        wssf.grid_columnconfigure(3, weight=1)
        wssf.pack(fill=tkinter.X)

        size_frame = tkinter.Frame(master=self.confirm)
        self.size = tkinter.IntVar()
        for i, size in enumerate((7, 8, 9, 10, 11, 12, 13, 14, 16, 18, 20)):
            size_button = tkinter.Radiobutton(
                master=size_frame,
                text=str(size),
                variable=self.size,
                value=size,
                indicatoron=0,
                command=self.try_command(self.on_show_font, size_frame),
            )
            size_button.grid_configure(column=i, row=0, sticky="ew")
            size_frame.grid_columnconfigure(i, weight=1, uniform="fsb")
        size_frame.pack(fill=tkinter.X)

        self.families.bind(
            "<<ListboxSelect>>", self.try_event(self.on_show_font)
        )

        self.sample = tkinter.Label(self.confirm)
        self.sample.pack(fill=tkinter.BOTH, expand=tkinter.TRUE)

        self.restore_focus = self.confirm.focus_get()
        self.confirm.wait_visibility()
        self.confirm.grab_set()
        self.confirm.wait_window()

    def get_chosen_font(self):
        """Return the chosen font."""
        return self.chosenfont

    def create_buttons(self):
        """Create the buttons used to control the dialogue (Ok and Cancel)."""
        buttons = (
            ("OK", "OK button Tooltip.", True, -1, self.on_ok),
            ("Cancel", "OK button Tooltip.", True, -1, self.on_cancel),
        )

        buttonrow = self.buttons_frame.pack_info()["side"] in ("top", "bottom")

        for i, button_def in enumerate(buttons):
            button = tkinter.Button(
                master=self.buttons_frame,
                text=button_def[0],
                underline=button_def[3],
                command=self.try_command(button_def[4], self.buttons_frame),
            )
            if buttonrow:
                self.buttons_frame.grid_columnconfigure(i * 2, weight=1)
                button.grid_configure(column=i * 2 + 1, row=0)
            else:
                self.buttons_frame.grid_rowconfigure(i * 2, weight=1)
                button.grid_configure(row=i * 2 + 1, column=0)
        if buttonrow:
            self.buttons_frame.grid_columnconfigure(len(buttons * 2), weight=1)
        else:
            self.buttons_frame.grid_rowconfigure(len(buttons * 2), weight=1)

    def on_cancel(self, event=None):
        """Close the font chooser dialogue."""
        self.confirm.destroy()

    def on_ok(self, event=None):
        """Close the font chooser dialogue if a font has been chosen."""
        if self.chosenfont:
            self.confirm.destroy()
        else:
            tkinter.messagebox.showerror(
                title="Font Chooser", message="No font chosen"
            )

    def on_show_font(self, event=None):
        """Display the sample text using the selected font and properties."""
        selection = self.families.curselection()
        if not selection:
            tkinter.messagebox.showerror(
                title="Font Chooser", message="No font chosen"
            )
            return

        if self.weight.get() == 2:
            weight = tkinter.font.BOLD
        else:
            weight = tkinter.font.NORMAL
        if self.slant.get() == 2:
            slant = tkinter.font.ITALIC
        else:
            slant = tkinter.font.ROMAN
        size = self.size.get()
        if not size:
            size = 12
        self.chosenfont = tkinter.font.Font(
            family=self.families.get(selection[0]),
            weight=weight,
            slant=slant,
            size=size,
        )
        self.sample.configure(
            font=self.chosenfont,
            text="\n".join(
                (
                    "ABCDEFGHIJKLMNOPQRSTWXYZ",
                    "abcdefghijklmnopqrstuvwxyz",
                    "0123456789",
                    r'!@#$%^&*()-_=+[{]};:"\|,<.>/?`~',
                )
            ),
        )

    def __del__(self):
        """Delete fontchooser instance."""
        self.chosenfont = None
        if self.restore_focus is not None:
            try:
                # restore focus on dismissing dialogue
                self.restore_focus.focus_set()
            except tkinter._tkinter.TclError as error:
                # application destroyed while confirm dialogue exists
                if str(error) != FOCUS_ERROR:
                    raise
        super().__del__()
