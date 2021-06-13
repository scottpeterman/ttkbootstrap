"""
    A **ttkbootstrap** styled **Sizegrip** widget.

    Created: 2021-05-21
    Author: Israel Dryer, israel.dryer@gmail.com

"""
from uuid import uuid4
from tkinter import ttk
from ttkbootstrap.style import StylerTTK
from ttkbootstrap.widgets import Widget
from ttkbootstrap.constants import *


class Sizegrip(Widget, ttk.Sizegrip):
    """A Sizegrip widget allows the user to resize the containing toplevel window by pressing and dragging the grip."""

    def __init__(
        self,
        # widget options
        master=None,
        bootstyle=DEFAULT,
        cursor=None,
        takefocus=True,
        style=None,
        # custom style options
        background=None,
        foreground=None,
        **kw,
    ):
        """
        Args:
            master: The parent widget.
            bootstyle (str): A string of keywords that controls the widget style; this short-hand API should be preferred over the tkinter ``style`` option, which is still available.
            cursor (str): The `mouse cursor`_ used for the widget. Names and values will vary according to OS.
            takefocus (bool): Adds or removes the widget from focus traversal.
            style (str): A ttk style api. Use ``bootstyle`` if possible.
            background (str): The sizegrip background color; setting this option will override theme settings.
            foreground (str): The color of the grips; setting this option will override theme settings.

        .. _`mouse cursor`: https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/cursors.html
        """

        Widget.__init__(self, "TSizegrip", master=master, bootstyle=bootstyle, style=style)

        self._background = background
        self._foreground = foreground
        self._bsoptions = ["background", "foreground", "bootstyle"]
        self.register_style()

        ttk.Sizegrip.__init__(
            self,
            master=master,
            cursor=cursor,
            style=self.style,
            takefocus=takefocus,
            **kw,
        )

    def style_widget(self):

        # custom styles
        if any([self._background != None, self._foreground != None]):
            self.customized = True
            if not self._widget_id:
                self._widget_id = uuid4() if self._widget_id == None else self._widget_id
                self.style = f"{self._widget_id}.{self.style}"

            options = {
                "theme": self.theme,
                "settings": self.settings,
                "background": self._background,
                "foreground": self._foreground or self.themed_color,
                "style": self.style,
            }
            StylerTTK.style_sizegrip(**options)

        # ttkbootstrap styles
        else:
            options = {
                "theme": self.theme,
                "settings": self.settings,
                "foreground": self.themed_color,
                "style": self.style,
            }
            StylerTTK.style_sizegrip(**options)
