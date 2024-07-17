# colourslider.py
# Copyright 2009 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Provide widgets for selecting red, green, and blue, colour components."""

import tkinter
import base64

from solentware_bind.gui.bindings import Bindings


class _Slider(Bindings):
    """A colour scale widget with a pointer and colour demonstration bar."""

    def __init__(self, master=None, column=None, row=None, resolution=2):
        """Create the slider widget.

        master - the parent widget for the colour slider component widgets
        column - the column in the parent widget for this slider
        row - the row in the parent widget for this slider
        label - description of this slider
        resolution - the number of colour values at each pixel in slider

        The default resolution, 2, gives 128 distinct positions on each
        slider because the colour values are 0 to 255.
        """
        super().__init__()
        self.canvas = tkinter.Canvas(master=master)
        self.canvas.grid_configure(column=column, row=row, sticky="nsew")

        self.lines = lines = []
        self.slider = self.canvas.create_polygon(
            50, 22, 55, 32, 45, 32, fill="black"
        )
        create_line = self.canvas.create_line
        for i, j in enumerate(list(range(0, 256, resolution))):
            lines.append(create_line(i + 10, 0, i + 10, 20))
        left, top, right, bottom = self.canvas.bbox("all")
        self.canvas.configure(height=bottom, width=right + 10)

        self.canvas.bind("<Enter>", self.try_event(self.on_enter))
        self.canvas.bind("<Leave>", self.try_event(self.on_leave))

    def on_enter(self, event=None):
        """Change the colour of this scale's slider to cyan."""
        self.canvas.itemconfigure(self.slider, fill="cyan")

    def on_leave(self, event=None):
        """Change the colour of this scale's slider to black."""
        self.canvas.itemconfigure(self.slider, fill="black")

    def move_slider(self, colour):
        """Move this slider to it's new position on the scale.

        colour - decimal colour component value used to position slider.
        """
        resolution = 256 // len(self.lines)
        left, top, right, bottom = self.canvas.bbox(self.slider)
        position = (left + right) // 2
        newposition = colour // resolution

        # The constant 10 should be same as used in width argument in the
        # self.canvas.configure() call in __init__().
        delta = 10 + newposition - position

        self.canvas.move(self.slider, delta, 0)

    def fill_scale(self, newcolour, redhex, greenhex, bluehex):
        """Redraw lines demonstrating colour scales using the new red value.

        rewcolour - new decimal value for colour if *hex argument is None.
                    Assumed that only one *hex is None.
        redhex - red component for other colour's scales.
        greenhex - green component for other colour's scales.
        bluehex - blue component for other colour's scales.
        """
        encode = base64.b16encode
        itemconfigure = self.canvas.itemconfigure
        resolution = 256 // len(self.lines)
        if redhex is None:
            for i, line in enumerate(self.lines):
                itemconfigure(
                    line,
                    fill=b"".join(
                        (
                            b"#",
                            encode(bytes((i * resolution,))),
                            greenhex,
                            bluehex,
                        )
                    ),
                )
        if greenhex is None:
            for i, line in enumerate(self.lines):
                itemconfigure(
                    line,
                    fill=b"".join(
                        (
                            b"#",
                            redhex,
                            encode(bytes((i * resolution,))),
                            bluehex,
                        )
                    ),
                )
        if bluehex is None:
            for i, line in enumerate(self.lines):
                itemconfigure(
                    line,
                    fill=b"".join(
                        (
                            b"#",
                            redhex,
                            greenhex,
                            encode(bytes((i * resolution,))),
                        )
                    ),
                )
        self.move_slider(newcolour)


class RedSlider(_Slider):
    """Colour slider widget for selecting the value of the red component."""

    def __init__(self, colourslider=None, **kw):
        """Delegate to superclass setting column argument to 1.

        colourslider - a ColourSlider instance.
        **kw - passed to superclass as **kw argument.
        """
        super().__init__(column=1, **kw)
        self.fill_scale(
            colourslider.red, None, colourslider.greenhex, colourslider.bluehex
        )


class GreenSlider(_Slider):
    """Colour slider widget for selecting the value of the green component."""

    def __init__(self, colourslider=None, **kw):
        """Delegate to superclass setting column argument to 2.

        colourslider - a ColourSlider instance.
        **kw - passed to superclass as **kw argument.
        """
        super().__init__(column=2, **kw)
        self.fill_scale(
            colourslider.green, colourslider.redhex, None, colourslider.bluehex
        )


class BlueSlider(_Slider):
    """Colour slider widget for selecting the value of the blue component."""

    def __init__(self, colourslider=None, **kw):
        """Delegate to superclass setting column argument to 3.

        colourslider - a ColourSlider instance.
        **kw - passed to superclass as **kw argument.
        """
        super().__init__(column=3, **kw)
        self.fill_scale(
            colourslider.blue, colourslider.redhex, colourslider.greenhex, None
        )


class ColourSlider(Bindings):
    """Provide a colour chooser widget.

    It has sliders for red, green, and blue, colour proportion selection
    arranged in a row in that order.

    """

    def __init__(
        self, master=None, row=None, label="", resolution=2, colour="grey"
    ):
        """Create the colour chooser widget.

        master - the parent widget for the colour slider component widgets
        row - the row in the parent widget for this slider
        label - description of this slider
        resolution - the number of colour values at each pixel in slider
        colour - the colour used to set the initial slider positions

        The default resolution, 2, gives 128 distinct positions on each
        slider because the colour values are 0 to 255.
        """
        super().__init__()
        self.resolution = resolution
        self.convert_RGB_colour_to_hex(master.winfo_rgb(colour))

        canvas = tkinter.Canvas(master=master, width=100, height=32)
        label = canvas.create_text(50, 16, text=label)
        canvas.grid_configure(column=0, row=row, sticky="nsew")
        self.redslider = RedSlider(
            colourslider=self, master=master, row=row, resolution=resolution
        )
        self.greenslider = GreenSlider(
            colourslider=self, master=master, row=row, resolution=resolution
        )
        self.blueslider = BlueSlider(
            colourslider=self, master=master, row=row, resolution=resolution
        )
        for widget, sequence, function in (
            (self.redslider, "<ButtonPress-1>", self.delta_red_colour),
            (self.redslider, "<ButtonPress-3>", self.set_red_colour),
            (self.greenslider, "<ButtonPress-1>", self.delta_green_colour),
            (self.greenslider, "<ButtonPress-3>", self.set_green_colour),
            (self.blueslider, "<ButtonPress-1>", self.delta_blue_colour),
            (self.blueslider, "<ButtonPress-3>", self.set_blue_colour),
        ):
            widget.canvas.bind(sequence, self.try_event(function))

    def get_colour(self):
        """Return the #RGB value of the selected colour (like #a0b0c6)."""
        return b"".join((b"#", self.redhex, self.greenhex, self.bluehex))

    def convert_RGB_colour_to_hex(self, colour):
        """Convert the red, green, blue values in colour to hex (for #RGB)."""
        red, green, blue = colour
        self.red = red // 256
        self.green = green // 256
        self.blue = blue // 256
        self.redhex = self._encode(self.red)
        self.greenhex = self._encode(self.green)
        self.bluehex = self._encode(self.blue)

    def delta_red_colour(self, event=None):
        """Adjust Red by value implied by position of Button-1 click."""
        self.red += self._increment(event, self.red)
        self.redhex = self._encode(self.red)
        self._fill_scales()

    def set_red_colour(self, event=None):
        """Set Red value implied by position of Button-3 click."""
        self.red = self._set(event)
        self.redhex = self._encode(self.red)
        self._fill_scales()

    def delta_green_colour(self, event=None):
        """Adjust Green by value implied by position of Button-1 click."""
        self.green += self._increment(event, self.green)
        self.greenhex = self._encode(self.green)
        self._fill_scales()

    def set_green_colour(self, event=None):
        """Set Green value implied by position of Button-3 click."""
        self.green = self._set(event)
        self.greenhex = self._encode(self.green)
        self._fill_scales()

    def delta_blue_colour(self, event=None):
        """Adjust Blue by value implied by position of Button-1 click."""
        self.blue += self._increment(event, self.blue)
        self.bluehex = self._encode(self.blue)
        self._fill_scales()

    def set_blue_colour(self, event=None):
        """Set Blue value implied by position of Button-3 click."""
        self.blue = self._set(event)
        self.bluehex = self._encode(self.blue)
        self._fill_scales()

    def _encode(self, colourcode):
        return base64.b16encode(bytes((colourcode,))).lower()

    def _fill_scales(self):
        self.redslider.fill_scale(self.red, None, self.greenhex, self.bluehex)
        self.greenslider.fill_scale(
            self.green, self.redhex, None, self.bluehex
        )
        self.blueslider.fill_scale(self.blue, self.redhex, self.greenhex, None)

    def _increment(self, event, colour):
        i = (event.x - 10) * self.resolution
        if colour < i:
            if colour < 255:
                return 1
        if colour > i:
            if colour > 0:
                return -1
        return 0

    def _set(self, event):
        i = (event.x - 10) * self.resolution
        if i > 255:
            return 255
        if i < 0:
            return 0
        return i
