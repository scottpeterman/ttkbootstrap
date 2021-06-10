"""
    A **ttkbootstrap** styled **Scale** widget.

    Created: 2021-06-02
    Author: Israel Dryer, israel.dryer@gmail.com

"""
from uuid import uuid4
from tkinter import ttk
from tkinter import Variable
from ttkbootstrap.core import StylerTTK
from ttkbootstrap.widgets import Widget


class Scale(Widget, ttk.Scale):
    """A Scale widget is typically used to control the numeric value of a linked variable that varies uniformly over 
    some range. A scale displays a slider that can be moved along over a trough, with the relative position of the 
    slider over the trough indicating the value of the variable."""

    def __init__(
        self,

        # widget options
        master=None,
        bootstyle="default",
        command=None,
        cursor=None,
        defaultvalue=None,
        format='%0.2f',
        from_=0,
        length=None,
        orient='horizontal',
        style=None,
        takefocus=False,
        to=100,
        variable=None,

        # custom style options
        slidercolor=None,
        troughcolor=None,
        **kw,
    ):
        """
        Args:
            master: The parent widget.
            bootstyle (str): A string of keywords that controls the widget style; this short-hand API should be preferred over the tkinter ``style`` option, which is still available.
            command (func): A function to invoke whenever the scale's value is changed.
            cursor (str): The `mouse cursor`_ used for the widget. Names and values will vary according to OS.
            defaultvalue (float): Specifies the current and default floating-point value of the variable. If ``variable`` is set to an existing variable, specifying ``value`` has no effect (the variable value takes precedence).
            format (str): A format specifier when returning value from the ``value`` property. To get the unformatted number, use the ``.variable.get()`` method.
            from_ (float): A real value corresponding to the left or top end of the scale. 
            length (int): Specifies the desired long dimension of the scale in screen units.
            orient (str): One of 'horizontal' or 'vertical'.  Specifies the orientation of the Scale.
            takefocus (bool): Adds or removes the widget from focus traversal.
            to (float): Specifies a real value corresponding to the right or bottom end of the scale. This value may be either less than or greater than the ``from`` option.
            variable (Variable): The variable to link to the scale. Whenever the value of the variable changes, the scale will update to reflect this value. Whenever the scale is manipulated interactively, the variable will be modified to reflect the scale's new value. If none is provided, one will be created automatically, and can be accessed or set via the ``value`` property.
            style (str): A ttk style api. Use ``bootstyle`` if possible.
            slidercolor (str): The color of the round slider; setting this will override theme settings.
            troughcolor (str): The color of the trough; setting this will override theme settings.

        .. _`mouse cursor`: https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/cursors.html
        """
        Widget.__init__(self, "TScale", master=master, bootstyle=bootstyle, orient=orient, style=style)

        self.variable = variable or Variable(value=defaultvalue or kw.get('value') or from_)
        self._format = format
        self._from = from_
        self._slidercolor = slidercolor
        self._to = to
        self._troughcolor = troughcolor
        self._orient = orient
        self._bsoptions = ['slidercolor', 'troughcolor', 'bootstyle']
        self._customize_widget()

        ttk.Scale.__init__(
            self,
            master=master,
            command=command,
            cursor=cursor,
            from_=from_,
            length=length,
            orient=orient,
            variable=self.variable,
            style=self.style,
            takefocus=takefocus,
            to=to,
            **kw,
        )

    @property
    def value(self):
        """Get the current value of the spinbox widget. Alias for ``Scale.get``"""
        return self._format.format(self.variable.get())

    @value.setter
    def value(self, value):
        """Set the current value of the spinbox widget. Alias for ``Scale.set``"""
        self.variable.set(value)

    def _customize_widget(self):

        if any([self._troughcolor != None, self._slidercolor != None]):
            self.customized = True

            if not self._widget_id:
                self._widget_id = uuid4() if self._widget_id == None else self._widget_id
                self.style = f"{self._widget_id}.{self.style}"

        if self.customized:
            options = {
                "theme": self.theme,
                "slidercolor": self._slidercolor or self.themed_color,
                "troughcolor": self._troughcolor,
                "orient": self._orient,
                "style": self.style,
            }
            settings = StylerTTK.style_scale(**options)

            self.update_ttk_style(settings)