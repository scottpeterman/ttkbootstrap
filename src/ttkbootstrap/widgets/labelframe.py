"""
    A **ttkbootstrap** styled **Labelframe** widget.

    Created: 2021-05-28
    Author: Israel Dryer, israel.dryer@gmail.com

"""
from uuid import uuid4
from tkinter import ttk
from ttkbootstrap.style import StylerTTK
from ttkbootstrap.themes import DEFAULT_COLORS
from ttkbootstrap.widgets import Widget
from ttkbootstrap.constants import *

# TODO dark theme needs to default to light text ... it's not working.

class LabelFrame(Widget, ttk.Label):
    """A Labelframe widget is a container used to group other widgets together. It has an optional label, which may be
    a plain text string or another widget."""

    def __init__(
        self,
        # widget options
        master=None,
        bootstyle=DEFAULT,
        cursor=None,
        height=None,
        labelanchor=None,
        labelwidget=None,
        padding=None,
        takefocus=False,
        text=None,
        underline=None,
        width=None,
        style=None,
        # custom style options
        background=None,
        bordercolor=None,
        foreground=None,
        **kw,
    ):
        """
        Args:
            master: The parent widget.
            bootstyle (str): A string of keywords that controls the widget style; this short-hand API should be preferred over the tkinter ``style`` option, which is still available.
            bordercolor (str): The labelframe border color; setting this option will override theme settings.
            cursor (str): The `mouse cursor`_ used for the widget. Names and values will vary according to OS.
            height (int): The widget's requested height in pixels.
            labelanchor (str): The position of the label. Legal values include: `nw`,`n`,`ne`,`en`,`e`,`es`,`se`,`s`,`sw`, `ws`, `w` and `wn`.
            labelwidget (str): The widget to use for the label. If set, overrides the ``text`` option; must be a child of the ancestors, and must belong to the same top-level widget as the labelframe.
            padding (Any): Sets the internal widget padding: (left, top, right, bottom), (horizontal, vertical), (left, vertical, right), a single number pads all sides.
            takefocus (bool): Adds or removes the widget from focus traversal.
            text (str): Specifies a text string to be displayed inside the label.
            underline (int): The index of the character to underline.
            width (int): The widget's requested width in pixels.
            style (str): A ttk style api. Use ``bootstyle`` if possible.
            background (str): The labelframe background color; setting this option will override theme settings.
            foreground (str): The label text color; setting this option will override theme settings.

        .. _`mouse cursor`: https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/cursors.html
        """
        Widget.__init__(self, "TLabelframe", master=master, bootstyle=bootstyle, style=style)

        # colors
        self._background = background
        self._bordercolor = bordercolor
        default_fg = self.colors.fg if self.theme.type == LIGHT else self.colors.selectfg
        self._foreground = foreground or default_fg if bootstyle == DEFAULT else self.colors.selectfg
        
        self._bsoptions = ["background", "bordercolor", "foreground", "bootstyle"]
        self.register_style()

        ttk.Labelframe.__init__(
            self,
            master=master,
            cursor=cursor,
            height=height,
            labelanchor=labelanchor,
            labelwidget=labelwidget,
            padding=padding,
            style=self.style,
            takefocus=takefocus,
            text=text,
            underline=underline,
            width=width,
            **kw,
        )

    def style_widget(self):

        # custom styles
        if any([self._background != None, self._foreground != None, self._bordercolor != None]):
            self.customized = True
            if not self._widget_id:
                self._widget_id = uuid4() if self._widget_id == None else self._widget_id
                self.style = f"{self._widget_id}.{self.style}"

            options = {
                "theme": self.theme,
                "settings": self.settings,
                "background": self._background or self.themed_color,
                "bordercolor": self._bordercolor,
                "foreground": self._foreground,
                "style": self.style,
            }
            StylerTTK.style_labelframe(**options)
        
        # ttkbootstrap styles
        else:
            options = {
                "theme": self.theme,
                "settings": self.settings,
                "background": self.themed_color,
                "foreground": self._foreground,
                "style": self.style,
            }
            StylerTTK.style_labelframe(**options)
