import colorsys
import importlib.resources
from tkinter import ttk
from uuid import uuid4
from PIL import ImageTk, Image, ImageDraw, ImageFont

from ttkbootstrap.core.themes import DEFAULT_FONT, ThemeColors
from ttkbootstrap.core.themes import ThemeDefinition
from ttkbootstrap.core.themes import COLORMAP


class Style(ttk.Style):
    """A class for setting the application style.

    Sets the theme of the ``tkinter.Tk`` instance and supports all ttkbootstrap and ttk themes provided. This class is
    meant to be a drop-in replacement for ``ttk.Style`` and inherits all of it's methods and properties. Creating a
    ``Style`` object will instantiate the ``tkinter.Tk`` instance in the ``Style.master`` property, and so it is not
    necessary to explicitly create an instance of ``tkinter.Tk``. For more details on the ``ttk.Style`` class, see the
    python documentation_.

    .. code-block:: python

        # instantiate the style with default theme *flatly*
        style = Style()

        # instantiate the style with another theme
        style = Style(theme='superhero')

        # instantiate the style with a theme from a specific themes file
        style = Style(theme='custom_name',
                      themes_file='C:/example/my_themes.json')

        # available themes
        for theme in style.theme_names():
            print(theme)

    .. _documentation: https://docs.python.org/3.9/library/tkinter.ttk.html#tkinter.ttk.Style
    """

    def __init__(self, themename="flatly", themes_file=None, master=None):
        super().__init__(master=master)

        self.styler = None
        self.theme_definitions = ThemeDefinition.load_themes(themes_file=themes_file)
        self.themes = set(self.theme_names())
        self.theme_objects = dict()
        self.register_themes()
        self.theme_use(themename=themename)

    @property
    def colors(self):
        return self.theme.colors

    def register_themes(self):
        """Registers all themes loaded into the ``theme_definitions`` property"""
        for theme in self.theme_definitions:
            self.themes.add(theme)

    def theme_use(self, themename=None):
        """Changes the theme used in rendering the application widgets.

        If themename is None, returns the theme in use, otherwise, set the current theme to themename, refreshes all
        widgets and emits a ``<<ThemeChanged>>`` event.

        Only use this method if you are changing the theme *during* runtime. Otherwise, pass the theme name into the
        Style constructor to instantiate the style with a theme.

        Keyword Args:
            themename (str): the theme to apply when creating new widgets
        """
        self.theme = self.theme_definitions.get(themename)

        if not themename:
            return super().theme_use()

        if all([themename, themename not in self.themes]):
            print(f"{themename} is not a valid theme name. Please try one of the following:")
            print(list(self.themes))
            return

        if themename not in self.theme_names():
            self.theme_objects[themename] = StylerTTK(self, self.theme)

        super().theme_use(themename)
        self.theme_objects[themename].styler_tk.style_tkinter_widgets()

        return


class StylerTK:
    """A class for styling tkinter widgets (not ttk).

    Several ttk widgets utilize tkinter widgets in some capacity, such as the `popdownlist` on the ``ttk.Combobox``. To
    create a consistent user experience, standard tkinter widgets are themed as much as possible with the look and feel
    of the **ttkbootstrap** theme applied. Tkinter widgets are not the primary target of this project; however, they can
    be used without looking entirely out-of-place in most cases.

    Attributes:
        master (Tk): the root window.
        theme (ThemeDefinition): the color settings defined in the `themes.json` file.
    """

    def __init__(self, styler_ttk):
        """
        Args:
            styler_ttk (StylerTTK): an instance of the ``StylerTTK`` class.
        """
        self.master = styler_ttk.style.master
        self.theme = styler_ttk.theme

    def style_tkinter_widgets(self):
        """A wrapper on all widget style methods. Applies current theme to all standard tkinter widgets"""
        self._style_spinbox()
        self._style_textwidget()
        self._style_button()
        self._style_label()
        self._style_checkbutton()
        self._style_radiobutton()
        self._style_entry()
        self._style_scale()
        self._style_listbox()
        self._style_menu()
        self._style_menubutton()
        self._style_labelframe()
        self._style_canvas()
        self._style_window()

    def _set_option(self, *args):
        """A convenience wrapper method to shorten the call to ``option_add``. *Laziness is next to godliness*.

        Args:
            *args (Tuple[str]): (pattern, value, priority=80)
        """
        self.master.option_add(*args)

    def _style_window(self):
        """Apply global options to all matching ``tkinter`` widgets"""
        self.master.configure(background=self.theme.colors.bg)
        self._set_option("*background", self.theme.colors.bg, 60)
        self._set_option("*font", self.theme.font, 60)
        self._set_option("*activeBackground", self.theme.colors.selectbg, 60)
        self._set_option("*activeForeground", self.theme.colors.selectfg, 60)
        self._set_option("*selectBackground", self.theme.colors.selectbg, 60)
        self._set_option("*selectForeground", self.theme.colors.selectfg, 60)

    def _style_canvas(self):
        """Apply style to ``tkinter.Canvas``"""
        self._set_option("*Canvas.highlightThickness", 1)
        self._set_option("*Canvas.highlightBackground", self.theme.colors.border)
        self._set_option("*Canvas.background", self.theme.colors.bg)

    def _style_button(self):
        """Apply style to ``tkinter.Button``"""
        active_bg = ThemeColors.update_hsv(self.theme.colors.primary, vd=-0.2)
        self._set_option("*Button.relief", "flat")
        self._set_option("*Button.borderWidth", 0)
        self._set_option("*Button.activeBackground", active_bg)
        self._set_option("*Button.foreground", self.theme.colors.selectfg)
        self._set_option("*Button.background", self.theme.colors.primary)

    def _style_label(self):
        """Apply style to ``tkinter.Label``"""
        self._set_option("*Label.foreground", self.theme.colors.fg)
        self._set_option("*Label.background", self.theme.colors.bg)

    def _style_checkbutton(self):
        """Apply style to ``tkinter.Checkbutton``"""
        self._set_option("*Checkbutton.activeBackground", self.theme.colors.bg)
        self._set_option("*Checkbutton.activeForeground", self.theme.colors.primary)
        self._set_option("*Checkbutton.background", self.theme.colors.bg)
        self._set_option("*Checkbutton.foreground", self.theme.colors.fg)
        self._set_option(
            "*Checkbutton.selectColor", self.theme.colors.primary if self.theme.type == "dark" else "white"
        )

    def _style_radiobutton(self):
        """Apply style to ``tkinter.Radiobutton``"""
        self._set_option("*Radiobutton.activeBackground", self.theme.colors.bg)
        self._set_option("*Radiobutton.activeForeground", self.theme.colors.primary)
        self._set_option("*Radiobutton.background", self.theme.colors.bg)
        self._set_option("*Radiobutton.foreground", self.theme.colors.fg)
        self._set_option(
            "*Radiobutton.selectColor", self.theme.colors.primary if self.theme.type == "dark" else "white"
        )

    def _style_entry(self):
        """Apply style to ``tkinter.Entry``"""
        self._set_option("*Entry.relief", "flat")
        self._set_option(
            "*Entry.background",
            (
                self.theme.colors.inputbg
                if self.theme.type == "light"
                else ThemeColors.update_hsv(self.theme.colors.inputbg, vd=-0.1)
            ),
        )
        self._set_option("*Entry.foreground", self.theme.colors.inputfg)
        self._set_option("*Entry.highlightThickness", 1)
        self._set_option("*Entry.highlightBackground", self.theme.colors.border)
        self._set_option("*Entry.highlightColor", self.theme.colors.primary)

    def _style_scale(self):
        """Apply style to ``tkinter.Scale``"""
        active_color = ThemeColors.update_hsv(self.theme.colors.primary, vd=-0.2)

        self._set_option("*Scale.background", self.theme.colors.primary)
        self._set_option("*Scale.showValue", False)
        self._set_option("*Scale.sliderRelief", "flat")
        self._set_option("*Scale.borderWidth", 0)
        self._set_option("*Scale.activeBackground", active_color)
        self._set_option("*Scale.highlightThickness", 1)
        self._set_option("*Scale.highlightColor", self.theme.colors.border)
        self._set_option("*Scale.highlightBackground", self.theme.colors.border)
        self._set_option("*Scale.troughColor", self.theme.colors.inputbg)

    def _style_spinbox(self):
        """Apply style to `tkinter.Spinbox``"""
        self._set_option("*Spinbox.foreground", self.theme.colors.inputfg)
        self._set_option("*Spinbox.relief", "flat")
        self._set_option(
            "*Spinbox.background",
            (
                self.theme.colors.inputbg
                if self.theme.type == "light"
                else ThemeColors.update_hsv(self.theme.colors.inputbg, vd=-0.1)
            ),
        )
        self._set_option("*Spinbox.highlightThickness", 1)
        self._set_option("*Spinbox.highlightColor", self.theme.colors.primary)
        self._set_option("*Spinbox.highlightBackground", self.theme.colors.border)

    def _style_listbox(self):
        """Apply style to ``tkinter.Listbox``"""
        self._set_option("*Listbox.foreground", self.theme.colors.inputfg)
        self._set_option("*Listbox.background", self.theme.colors.inputbg)
        self._set_option("*Listbox.selectBackground", self.theme.colors.selectbg)
        self._set_option("*Listbox.selectForeground", self.theme.colors.selectfg)
        self._set_option("*Listbox.relief", "flat")
        self._set_option("*Listbox.activeStyle", "none")
        self._set_option("*Listbox.highlightThickness", 1)
        self._set_option("*Listbox.highlightColor", self.theme.colors.primary)
        self._set_option("*Listbox.highlightBackground", self.theme.colors.border)

    def _style_menubutton(self):
        """Apply style to ``tkinter.Menubutton``"""
        hover_color = ThemeColors.update_hsv(self.theme.colors.primary, vd=-0.2)
        self._set_option("*Menubutton.activeBackground", hover_color)
        self._set_option("*Menubutton.background", self.theme.colors.primary)
        self._set_option("*Menubutton.foreground", self.theme.colors.selectfg)
        self._set_option("*Menubutton.borderWidth", 0)

    def _style_menu(self):
        """Apply style to ``tkinter.Menu``"""
        self._set_option("*Menu.tearOff", 0)
        self._set_option("*Menu.foreground", self.theme.colors.fg)
        self._set_option("*Menu.selectColor", self.theme.colors.primary)
        self._set_option("*Menu.font", self.theme.font)
        self._set_option(
            "*Menu.background",
            (self.theme.colors.inputbg if self.theme.type == "light" else self.theme.colors.bg),
        )
        self._set_option("*Menu.activeBackground", self.theme.colors.selectbg)
        self._set_option("*Menu.activeForeground", self.theme.colors.selectfg)

    def _style_labelframe(self):
        """Apply style to ``tkinter.Labelframe``"""
        self._set_option("*Labelframe.font", self.theme.font)
        self._set_option("*Labelframe.foreground", self.theme.colors.fg)
        self._set_option("*Labelframe.highlightColor", self.theme.colors.border)
        self._set_option("*Labelframe.borderWidth", 1)
        self._set_option("*Labelframe.highlightThickness", 0)

    def _style_textwidget(self):
        """Apply style to ``tkinter.Text``"""
        self._set_option("*Text.background", self.theme.colors.inputbg)
        self._set_option("*Text.foreground", self.theme.colors.inputfg)
        self._set_option("*Text.highlightColor", self.theme.colors.primary)
        self._set_option("*Text.highlightBackground", self.theme.colors.border)
        self._set_option("*Text.borderColor", self.theme.colors.border)
        self._set_option("*Text.highlightThickness", 1)
        self._set_option("*Text.relief", "flat")
        self._set_option("*Text.font", self.theme.font)
        self._set_option("*Text.padX", 5)
        self._set_option("*Text.padY", 5)


class StylerTTK:
    """A class to create a new ttk theme.

    Create a new ttk theme by using a combination of built-in themes and some image-based elements using ``pillow``. A
    theme is generated at runtime and is available to use with the ``Style`` class methods. The base theme of all
    **ttkbootstrap** themes is *clam*. In many cases, widget layouts are re-created using an assortment of elements from
    various styles such as *clam*, *alt*, *default*, etc...

    Attributes:
        theme_images (dict): theme assets used for various widgets.
        settings (dict): settings used to build the actual theme using the ``theme_create`` method.
        styler_tk (StylerTk): an object used to style tkinter widgets (not ttk).
        theme (ThemeDefinition): the theme settings defined in the `themes.json` file.
    """

    theme_images = dict()

    def __init__(self, style, definition):
        """
        Args:
            style (Style): an instance of ``ttk.Style``.
            definition (ThemeDefinition): an instance of ``ThemeDefinition``; used to create the theme settings.
        """
        self.style = style
        self.theme = definition
        self.theme_images = StylerTTK.theme_images
        self.settings = {}
        self.styler_tk = StylerTK(self)
        self.create_theme()

    def create_theme(self):
        """Create and style a new ttk theme. A wrapper around internal style methods."""
        self.update_ttk_theme_settings()
        self.style.theme_create(self.theme.name, "clam", self.settings)

    def update_ttk_theme_settings(self):
        """Update the settings dictionary that is used to create a theme. This is a wrapper on all the `_style_widget`
        methods which define the layout, configuration, and styling mapping for each ttk widget.
        """
        self._style_labelframe()
        self._style_spinbox()
        self._style_scale()
        self._style_scrollbar()
        self._style_combobox()
        self._style_exit_button()
        self._style_frame()
        self._style_calendar()
        self._style_entry()
        self._style_label()
        self._style_meter()
        self._style_notebook()
        self._style_outline_menubutton()
        self._style_outline_toolbutton()
        self._style_progressbar()
        self._style_striped_progressbar()
        self._style_floodgauge()
        self._style_radiobutton()
        self._style_solid_menubutton()
        self._style_solid_toolbutton()
        self._style_treeview()
        self._style_panedwindow()
        self._style_roundtoggle_toolbutton()
        self._style_squaretoggle_toolbutton()

        # themed style
        for color in self.theme.colors:
            self.settings.update(self.style_solid_buttons(self.theme, background=color, style=f"{color}.TButton"))
            self.settings.update(self.style_link_buttons(self.theme, foreground=color, style=f"{color}.Link.TButton"))
            self.settings.update(self.style_sizegrip(self.theme, foreground=color, style=f"{color}.TSizegrip"))
            self.settings.update(self.style_checkbutton(self.theme, indicatorcolor=color, style=f"{color}.TCheckbutton"))
            self.settings.update(
                self.style_separator(self.theme, background=color, style=f"{color}.Horizontal.TSeparator")
            )
            self.settings.update(
                self.style_separator(
                    self.theme, background=color, orient="vertical", style=f"{color}.Vertical.TSeparator"
                )
            )
            self.settings.update(
                self.style_outline_buttons(self.theme, foreground=color, style=f"{color}.Outline.TButton")
            )

        # default style
        self.settings.update(self.style_solid_buttons(self.theme, style="TButton"))
        self.settings.update(self.style_outline_buttons(self.theme, style="Outline.TButton"))
        self.settings.update(self.style_link_buttons(self.theme, style="Link.TButton"))
        self.settings.update(self.style_sizegrip(self.theme, style="TSizegrip"))
        self.settings.update(self.style_separator(self.theme, orient="vertical", style="Vertical.TSeparator"))
        self.settings.update(self.style_separator(self.theme))
        self.settings.update(self.style_checkbutton(self.theme, style="TCheckbutton"))

        self._style_defaults()

    def _style_defaults(self):
        """Setup the default ``ttk.Style`` configuration. These defaults are applied to any widget that contains these
        element options. This method should be called *first* before any other style is applied during theme creation.
        """
        self.settings.update(
            {
                ".": {
                    "configure": {
                        "background": self.theme.colors.bg,
                        "darkcolor": self.theme.colors.border,
                        "foreground": self.theme.colors.fg,
                        "troughcolor": self.theme.colors.bg,
                        "selectbg": self.theme.colors.selectbg,
                        "selectfg": self.theme.colors.selectfg,
                        "selectforeground": self.theme.colors.selectfg,
                        "selectbackground": self.theme.colors.selectbg,
                        "fieldbg": "white",
                        "font": self.theme.font,
                        "borderwidth": 1,
                        "focuscolor": "",
                    }
                }
            }
        )

    def _style_combobox(self):
        """Create style configuration for ``ttk.Combobox``. This element style is created with a layout that combines
        *clam* and *default* theme elements.

        The options available in this widget based on this layout include:

            - Combobox.downarrow: arrowsize, background, bordercolor, relief, arrowcolor
            - Combobox.field: bordercolor, lightcolor, darkcolor, fieldbackground
            - Combobox.padding: padding, relief, shiftrelief
            - Combobox.textarea: font, width

        .. info::

            When the dark theme is used, I used the *spinbox.field* from the *default* theme because the background
            shines through the corners using the `clam` theme. This is an unfortuate hack to make it look ok. Hopefully
            there will be a more permanent/better solution in the future.
        """
        disabled_fg = (
            ThemeColors.update_hsv(self.theme.colors.inputbg, vd=-0.2)
            if self.theme.type == "light"
            else ThemeColors.update_hsv(self.theme.colors.inputbg, vd=-0.3)
        )

        if self.theme.type == "dark":
            self.settings.update({"combo.Spinbox.field": {"element create": ("from", "default")}})

        self.settings.update(
            {
                "Combobox.downarrow": {"element create": ("from", "default")},
                "Combobox.padding": {"element create": ("from", "clam")},
                "Combobox.textarea": {"element create": ("from", "clam")},
                "TCombobox": {
                    "layout": [
                        (
                            "combo.Spinbox.field",
                            {
                                "side": "top",
                                "sticky": "we",
                                "children": [
                                    ("Combobox.downarrow", {"side": "right", "sticky": "ns"}),
                                    (
                                        "Combobox.padding",
                                        {
                                            "expand": "1",
                                            "sticky": "nswe",
                                            "children": [("Combobox.textarea", {"sticky": "nswe"})],
                                        },
                                    ),
                                ],
                            },
                        )
                    ],
                    "configure": {
                        "bordercolor": self.theme.colors.border,
                        "darkcolor": self.theme.colors.inputbg,
                        "lightcolor": self.theme.colors.inputbg,
                        "arrowcolor": self.theme.colors.inputfg,
                        "foreground": self.theme.colors.inputfg,
                        "fieldbackground ": self.theme.colors.inputbg,
                        "background ": self.theme.colors.inputbg,
                        "relief": "flat",
                        "borderwidth ": 0,  # only applies to dark theme border
                        "padding": 5,
                        "arrowsize ": 14,
                    },
                    "map": {
                        "foreground": [("disabled", disabled_fg)],
                        "bordercolor": [
                            ("focus !disabled", self.theme.colors.primary),
                            ("hover !disabled", self.theme.colors.bg),
                        ],
                        "lightcolor": [
                            ("focus !disabled", self.theme.colors.primary),
                            ("hover !disabled", self.theme.colors.primary),
                        ],
                        "darkcolor": [
                            ("focus !disabled", self.theme.colors.primary),
                            ("hover !disabled", self.theme.colors.primary),
                        ],
                        "arrowcolor": [
                            ("disabled", disabled_fg),
                            ("pressed !disabled", self.theme.colors.inputbg),
                            ("focus !disabled", self.theme.colors.inputfg),
                            ("hover !disabled", self.theme.colors.primary),
                        ],
                    },
                },
            }
        )

        for color in self.theme.colors:
            self.settings.update(
                {
                    f"{color}.TCombobox": {
                        "map": {
                            "foreground": [("disabled", disabled_fg)],
                            "bordercolor": [
                                ("focus !disabled", self.theme.colors.get(color)),
                                ("hover !disabled", self.theme.colors.get(color)),
                            ],
                            "lightcolor": [
                                ("focus !disabled", self.theme.colors.get(color)),
                                ("pressed !disabled", self.theme.colors.get(color)),
                            ],
                            "darkcolor": [
                                ("focus !disabled", self.theme.colors.get(color)),
                                ("pressed !disabled", self.theme.colors.get(color)),
                            ],
                            "arrowcolor": [
                                ("disabled", disabled_fg),
                                ("pressed !disabled", self.theme.colors.inputbg),
                                ("focus !disabled", self.theme.colors.inputfg),
                                ("hover !disabled", self.theme.colors.primary),
                            ],
                        }
                    }
                }
            )

    @staticmethod
    def style_separator(theme, background=None, orient="horizontal", style="Horizontal.TSeparator"):
        """Create style configuration for ttk separator: *ttk.Separator*. The default style for light will be border,
        but dark will be primary, as this makes the most sense for general use. However, all other colors will be
        available as well through styling.

        Args:
            theme (str): The theme name.
            background (str, optional): The color of the sizegrip background.
            orient (str, optional): One of 'horizontal' or 'vertical'
            style (str, optional): The style used to render the widget.

        Returns:
            dict: A dictionary of theme settings.
        """
        if theme.type == "light":
            background = ThemeColors.normalize(background, theme.colors.border, theme.colors)
        else:
            background = ThemeColors.normalize(background, theme.colors.selectbg, theme.colors)

        # create separator images
        hs_image_id = uuid4()
        hs_im = ImageTk.PhotoImage(Image.new("RGB", (40, 1), background))
        StylerTTK.theme_images[hs_image_id] = hs_im

        vs_image_id = uuid4()
        vs_im = ImageTk.PhotoImage(Image.new("RGB", (1, 40), background))
        StylerTTK.theme_images[vs_image_id] = vs_im

        settings = dict()

        if orient.lower() == "horizontal":
            settings.update(
                {
                    f"{hs_image_id}.Horizontal.Separator.separator": {
                        "element create": ("image", StylerTTK.theme_images[hs_image_id])
                    },
                    f"{style}": {"layout": [(f"{hs_image_id}.Horizontal.Separator.separator", {"sticky": "we"})]},
                }
            )
        else:
            settings.update(
                {
                    f"{vs_image_id}.Vertical.Separator.separator": {
                        "element create": ("image", StylerTTK.theme_images[vs_image_id])
                    },
                    f"{style}": {"layout": [(f"{vs_image_id}.Vertical.Separator.separator", {"sticky": "ns"})]},
                }
            )
        return settings

    def _style_striped_progressbar(self):
        """Apply a striped theme to the progressbar"""
        self.theme_images.update(self._create_striped_progressbar_image("primary"))
        self.settings.update(
            {
                "Striped.Horizontal.Progressbar.pbar": {
                    "element create": (
                        "image",
                        self.theme_images["primary_striped_hpbar"],
                        {"width": 20, "sticky": "ew"},
                    )
                },
                "Striped.Horizontal.TProgressbar": {
                    "layout": [
                        (
                            "Horizontal.Progressbar.trough",
                            {
                                "sticky": "nswe",
                                "children": [("Striped.Horizontal.Progressbar.pbar", {"side": "left", "sticky": "ns"})],
                            },
                        )
                    ],
                    "configure": {
                        "troughcolor": self.theme.colors.inputbg,
                        "thickness": 20,
                        "borderwidth": 1,
                        "lightcolor": self.theme.colors.border
                        if self.theme.type == "light"
                        else self.theme.colors.inputbg,
                    },
                },
            }
        )

        for color in self.theme.colors:
            self.theme_images.update(self._create_striped_progressbar_image(color))
            self.settings.update(
                {
                    f"{color}.Striped.Horizontal.Progressbar.pbar": {
                        "element create": (
                            "image",
                            self.theme_images[f"{color}_striped_hpbar"],
                            {"width": 20, "sticky": "ew"},
                        )
                    },
                    f"{color}.Striped.Horizontal.TProgressbar": {
                        "layout": [
                            (
                                "Horizontal.Progressbar.trough",
                                {
                                    "sticky": "nswe",
                                    "children": [
                                        (
                                            f"{color}.Striped.Horizontal.Progressbar.pbar",
                                            {"side": "left", "sticky": "ns"},
                                        )
                                    ],
                                },
                            )
                        ],
                        "configure": {
                            "troughcolor": self.theme.colors.inputbg,
                            "thickness": 20,
                            "borderwidth": 1,
                            "lightcolor": self.theme.colors.border
                            if self.theme.type == "light"
                            else self.theme.colors.inputbg,
                        },
                    },
                }
            )

    def _create_striped_progressbar_image(self, colorname):
        """Create the striped progressbar image and return as a ``PhotoImage``

        Args:
            colorname (str): the color label assigned to the colors property; eg. `primary`, `secondary`, `success`.

        Returns:
            dict: a dictionary containing the widget images.
        """
        bar_primary = self.theme.colors.get(colorname)

        # calculate value of light color
        brightness = colorsys.rgb_to_hsv(*ThemeColors.hex_to_rgb(bar_primary))[2]
        if brightness < 0.4:
            value_delta = 0.3
        elif brightness > 0.8:
            value_delta = 0
        else:
            value_delta = 0.1
        bar_secondary = ThemeColors.update_hsv(bar_primary, sd=-0.2, vd=value_delta)

        # need to check the darkness of the color before setting the secondary

        # horizontal progressbar
        h_im = Image.new("RGBA", (100, 100), bar_secondary)
        draw = ImageDraw.Draw(h_im)
        draw.polygon([(0, 0), (48, 0), (100, 52), (100, 100), (100, 100)], fill=bar_primary)
        draw.polygon([(0, 52), (48, 100), (0, 100)], fill=bar_primary)
        horizontal_img = ImageTk.PhotoImage(h_im.resize((22, 22), Image.LANCZOS))

        # TODO vertical progressbar

        return {f"{colorname}_striped_hpbar": horizontal_img}

    def _style_progressbar(self):
        """Create style configuration for ttk progressbar: *ttk.Progressbar*

        The options available in this widget include:

            - Progressbar.trough: borderwidth, troughcolor, troughrelief
            - Progressbar.pbar: orient, thickness, barsize, pbarrelief, borderwidth, background
        """
        self.settings.update(
            {
                "Progressbar.trough": {"element create": ("from", "clam")},
                "Progressbar.pbar": {"element create": ("from", "default")},
                "TProgressbar": {
                    "configure": {
                        "thickness": 20,
                        "borderwidth": 1,
                        "bordercolor": self.theme.colors.border
                        if self.theme.type == "light"
                        else self.theme.colors.inputbg,
                        "lightcolor": self.theme.colors.border,
                        "pbarrelief": "flat",
                        "troughcolor": self.theme.colors.inputbg,
                        "background": self.theme.colors.primary,
                    }
                },
            }
        )

        for color in self.theme.colors:
            self.settings.update(
                {
                    f"{color}.Horizontal.TProgressbar": {"configure": {"background": self.theme.colors.get(color)}},
                    f"{color}.Vertical.TProgressbar": {"configure": {"background": self.theme.colors.get(color)}},
                }
            )

    @staticmethod
    def _create_slider_image(color, size=16):
        """Create a circle slider image based on given size and color; used in the slider widget.

        Args:
            color (str): a hexadecimal color value.
            size (int): the size diameter of the slider circle; default=16.

        Returns:
            ImageTk.PhotoImage: an image drawn in the shape of the circle of the theme color specified.
        """
        im = Image.new("RGBA", (100, 100))
        draw = ImageDraw.Draw(im)
        draw.ellipse((0, 0, 95, 95), fill=color)
        return ImageTk.PhotoImage(im.resize((size, size), Image.LANCZOS))

    def _style_scale(self):
        """Create style configuration for ttk scale: *ttk.Scale*

        The options available in this widget include:

            - Scale.trough: borderwidth, troughcolor, troughrelief
            - Scale.slider: sliderlength, sliderthickness, sliderrelief, borderwidth, background, bordercolor, orient
        """
        disabled_fg = (
            ThemeColors.update_hsv(self.theme.colors.inputbg, vd=-0.2)
            if self.theme.type == "light"
            else ThemeColors.update_hsv(self.theme.colors.inputbg, vd=-0.3)
        )

        trough_color = (
            self.theme.colors.inputbg
            if self.theme.type == "dark"
            else ThemeColors.update_hsv(self.theme.colors.inputbg, vd=-0.03)
        )

        pressed_vd = -0.2
        hover_vd = -0.1

        # create widget images
        self.theme_images.update(
            {
                "primary_disabled": self._create_slider_image(disabled_fg),
                "primary_regular": self._create_slider_image(self.theme.colors.primary),
                "primary_pressed": self._create_slider_image(
                    ThemeColors.update_hsv(self.theme.colors.primary, vd=pressed_vd)
                ),
                "primary_hover": self._create_slider_image(
                    ThemeColors.update_hsv(self.theme.colors.primary, vd=hover_vd)
                ),
                "htrough": ImageTk.PhotoImage(Image.new("RGB", (40, 8), trough_color)),
                "vtrough": ImageTk.PhotoImage(Image.new("RGB", (8, 40), trough_color)),
            }
        )

        # The layout is derived from the 'xpnative' theme
        self.settings.update(
            {
                "Horizontal.TScale": {
                    "layout": [
                        (
                            "Scale.focus",
                            {
                                "expand": "1",
                                "sticky": "nswe",
                                "children": [
                                    ("Horizontal.Scale.track", {"sticky": "we"}),
                                    ("Horizontal.Scale.slider", {"side": "left", "sticky": ""}),
                                ],
                            },
                        )
                    ]
                },
                "Vertical.TScale": {
                    "layout": [
                        (
                            "Scale.focus",
                            {
                                "expand": "1",
                                "sticky": "nswe",
                                "children": [
                                    ("Vertical.Scale.track", {"sticky": "ns"}),
                                    ("Vertical.Scale.slider", {"side": "top", "sticky": ""}),
                                ],
                            },
                        )
                    ]
                },
                "Horizontal.Scale.track": {"element create": ("image", self.theme_images["htrough"])},
                "Vertical.Scale.track": {"element create": ("image", self.theme_images["vtrough"])},
                "Scale.slider": {
                    "element create": (
                        "image",
                        self.theme_images["primary_regular"],
                        ("disabled", self.theme_images["primary_disabled"]),
                        ("pressed !disabled", self.theme_images["primary_pressed"]),
                        ("hover !disabled", self.theme_images["primary_hover"]),
                    )
                },
            }
        )

        for color in self.theme.colors:
            self.theme_images.update(
                {
                    f"{color}_regular": self._create_slider_image(self.theme.colors.get(color)),
                    f"{color}_pressed": self._create_slider_image(
                        ThemeColors.update_hsv(self.theme.colors.get(color), vd=pressed_vd)
                    ),
                    f"{color}_hover": self._create_slider_image(
                        ThemeColors.update_hsv(self.theme.colors.get(color), vd=hover_vd)
                    ),
                }
            )

            # The layout is derived from the 'xpnative' theme
            self.settings.update(
                {
                    f"{color}.Horizontal.TScale": {
                        "layout": [
                            (
                                "Scale.focus",
                                {
                                    "expand": "1",
                                    "sticky": "nswe",
                                    "children": [
                                        ("Horizontal.Scale.track", {"sticky": "we"}),
                                        (f"{color}.Scale.slider", {"side": "left", "sticky": ""}),
                                    ],
                                },
                            )
                        ]
                    },
                    f"{color}.Vertical.TScale": {
                        "layout": [
                            (
                                f"{color}.Scale.focus",
                                {
                                    "expand": "1",
                                    "sticky": "nswe",
                                    "children": [
                                        ("Vertical.Scale.track", {"sticky": "ns"}),
                                        (f"{color}.Scale.slider", {"side": "top", "sticky": ""}),
                                    ],
                                },
                            )
                        ]
                    },
                    f"{color}.Scale.slider": {
                        "element create": (
                            "image",
                            self.theme_images[f"{color}_regular"],
                            ("disabled", self.theme_images["primary_disabled"]),
                            ("pressed", self.theme_images[f"{color}_pressed"]),
                            ("hover", self.theme_images[f"{color}_hover"]),
                        )
                    },
                }
            )

    def _create_scrollbar_images(self):
        """Create assets needed for scrollbar arrows. The assets are saved to the ``theme_images`` property."""
        font_size = 13
        with importlib.resources.open_binary("ttkbootstrap.core.files", "Symbola.ttf") as font_path:
            fnt = ImageFont.truetype(font_path, font_size)

        # up arrow
        vs_upim = Image.new("RGBA", (font_size, font_size))
        up_draw = ImageDraw.Draw(vs_upim)
        up_draw.text(
            (1, 5),
            "🞁",
            font=fnt,
            fill=self.theme.colors.inputfg
            if self.theme.type == "light"
            else ThemeColors.update_hsv(self.theme.colors.selectbg, vd=0.35, sd=-0.1),
        )
        self.theme_images["vsup"] = ImageTk.PhotoImage(vs_upim)

        # down arrow
        hsdown_im = Image.new("RGBA", (font_size, font_size))
        down_draw = ImageDraw.Draw(hsdown_im)
        down_draw.text(
            (1, -4),
            "🞃",
            font=fnt,
            fill=self.theme.colors.inputfg
            if self.theme.type == "light"
            else ThemeColors.update_hsv(self.theme.colors.selectbg, vd=0.35, sd=-0.1),
        )
        self.theme_images["vsdown"] = ImageTk.PhotoImage(hsdown_im)

        # left arrow
        vs_upim = Image.new("RGBA", (font_size, font_size))
        up_draw = ImageDraw.Draw(vs_upim)
        up_draw.text(
            (1, 1),
            "🞀",
            font=fnt,
            fill=self.theme.colors.inputfg
            if self.theme.type == "light"
            else ThemeColors.update_hsv(self.theme.colors.selectbg, vd=0.35, sd=-0.1),
        )
        self.theme_images["hsleft"] = ImageTk.PhotoImage(vs_upim)

        # right arrow
        vs_upim = Image.new("RGBA", (font_size, font_size))
        up_draw = ImageDraw.Draw(vs_upim)
        up_draw.text(
            (1, 1),
            "🞂",
            font=fnt,
            fill=self.theme.colors.inputfg
            if self.theme.type == "light"
            else ThemeColors.update_hsv(self.theme.colors.selectbg, vd=0.35, sd=-0.1),
        )
        self.theme_images["hsright"] = ImageTk.PhotoImage(vs_upim)

    def _style_floodgauge(self):
        """Create a style configuration for the *ttk.Progressbar* that makes it into a floodgauge. Which is essentially
        a very large progress bar with text in the middle.

        The options available in this widget include:

            - Floodgauge.trough: borderwidth, troughcolor, troughrelief
            - Floodgauge.pbar: orient, thickness, barsize, pbarrelief, borderwidth, background
            - Floodgauge.text: 'text', 'font', 'foreground', 'underline', 'width', 'anchor', 'justify', 'wraplength',
                'embossed'
        """
        self.settings.update(
            {
                "Floodgauge.trough": {"element create": ("from", "clam")},
                "Floodgauge.pbar": {"element create": ("from", "default")},
                "Horizontal.TFloodgauge": {
                    "layout": [
                        (
                            "Floodgauge.trough",
                            {
                                "children": [
                                    ("Floodgauge.pbar", {"sticky": "ns"}),
                                    ("Floodgauge.label", {"sticky": ""}),
                                ],
                                "sticky": "nswe",
                            },
                        )
                    ],
                    "configure": {
                        "thickness": 50,
                        "borderwidth": 1,
                        "bordercolor": self.theme.colors.primary,
                        "lightcolor": self.theme.colors.primary,
                        "pbarrelief": "flat",
                        "troughcolor": ThemeColors.update_hsv(self.theme.colors.primary, sd=-0.3, vd=0.8),
                        "background": self.theme.colors.primary,
                        "foreground": self.theme.colors.selectfg,
                        "justify": "center",
                        "anchor": "center",
                        "font": "helvetica 14",
                    },
                },
                "Vertical.TFloodgauge": {
                    "layout": [
                        (
                            "Floodgauge.trough",
                            {
                                "children": [
                                    ("Floodgauge.pbar", {"sticky": "we"}),
                                    ("Floodgauge.label", {"sticky": ""}),
                                ],
                                "sticky": "nswe",
                            },
                        )
                    ],
                    "configure": {
                        "thickness": 50,
                        "borderwidth": 1,
                        "bordercolor": self.theme.colors.primary,
                        "lightcolor": self.theme.colors.primary,
                        "pbarrelief": "flat",
                        "troughcolor": ThemeColors.update_hsv(self.theme.colors.primary, sd=-0.3, vd=0.8),
                        "background": self.theme.colors.primary,
                        "foreground": self.theme.colors.selectfg,
                        "justify": "center",
                        "anchor": "center",
                        "font": "helvetica 14",
                    },
                },
            }
        )

        for color in self.theme.colors:
            self.settings.update(
                {
                    f"{color}.Horizontal.TFloodgauge": {
                        "configure": {
                            "thickness": 50,
                            "borderwidth": 1,
                            "bordercolor": self.theme.colors.get(color),
                            "lightcolor": self.theme.colors.get(color),
                            "pbarrelief": "flat",
                            "troughcolor": ThemeColors.update_hsv(self.theme.colors.get(color), sd=-0.3, vd=0.8),
                            "background": self.theme.colors.get(color),
                            "foreground": self.theme.colors.selectfg,
                            "justify": "center",
                            "anchor": "center",
                            "font": "helvetica 14",
                        }
                    },
                    f"{color}.Vertical.TFloodgauge": {
                        "configure": {
                            "thickness": 50,
                            "borderwidth": 1,
                            "bordercolor": self.theme.colors.get(color),
                            "lightcolor": self.theme.colors.get(color),
                            "pbarrelief": "flat",
                            "troughcolor": ThemeColors.update_hsv(self.theme.colors.get(color), sd=-0.3, vd=0.8),
                            "background": self.theme.colors.get(color),
                            "foreground": self.theme.colors.selectfg,
                            "justify": "center",
                            "anchor": "center",
                            "font": "helvetica 14",
                        }
                    },
                }
            )

    def _style_scrollbar(self):
        """Create style configuration for ttk scrollbar: *ttk.Scrollbar*. This theme uses elements from the *alt* theme
        tobuild the widget layout.

        The options available in this widget include:

            - Scrollbar.trough: orient, troughborderwidth, troughcolor, troughrelief, groovewidth
            - Scrollbar.uparrow: arrowsize, background, bordercolor, relief, arrowcolor
            - Scrollbar.downarrow: arrowsize, background, bordercolor, relief, arrowcolor
            - Scrollbar.thumb: width, background, bordercolor, relief, orient
        """
        self._create_scrollbar_images()

        self.settings.update(
            {
                "Vertical.Scrollbar.trough": {"element create": ("from", "alt")},
                "Vertical.Scrollbar.thumb": {"element create": ("from", "alt")},
                "Vertical.Scrollbar.uparrow": {"element create": ("image", self.theme_images["vsup"])},
                "Vertical.Scrollbar.downarrow": {"element create": ("image", self.theme_images["vsdown"])},
                "Horizontal.Scrollbar.trough": {"element create": ("from", "alt")},
                "Horizontal.Scrollbar.thumb": {"element create": ("from", "alt")},
                "Horizontal.Scrollbar.leftarrow": {"element create": ("image", self.theme_images["hsleft"])},
                "Horizontal.Scrollbar.rightarrow": {"element create": ("image", self.theme_images["hsright"])},
                "TScrollbar": {
                    "configure": {
                        "troughrelief": "flat",
                        "relief": "flat",
                        "troughborderwidth": 2,
                        "troughcolor": ThemeColors.update_hsv(self.theme.colors.bg, vd=-0.05),
                        "background": ThemeColors.update_hsv(self.theme.colors.bg, vd=-0.15)
                        if self.theme.type == "light"
                        else ThemeColors.update_hsv(self.theme.colors.selectbg, vd=0.25, sd=-0.1),
                        "width": 16,
                    },
                    "map": {
                        "background": [
                            (
                                "pressed",
                                ThemeColors.update_hsv(self.theme.colors.bg, vd=-0.35)
                                if self.theme.type == "light"
                                else ThemeColors.update_hsv(self.theme.colors.selectbg, vd=0.05),
                            ),
                            (
                                "active",
                                ThemeColors.update_hsv(self.theme.colors.bg, vd=-0.25)
                                if self.theme.type == "light"
                                else ThemeColors.update_hsv(self.theme.colors.selectbg, vd=0.15),
                            ),
                        ]
                    },
                },
            }
        )

    def _style_spinbox(self):
        """Create style configuration for ttk spinbox: *ttk.Spinbox*

        This widget uses elements from the *default* and *clam* theme to create the widget layout.
        For dark themes,the spinbox.field is created from the *default* theme element because the background
        color shines through the corners of the widget when the primary theme background color is dark.

        The options available in this widget include:

            - Spinbox.field: bordercolor, lightcolor, darkcolor, fieldbackground
            - spinbox.uparrow: background, relief, borderwidth, arrowcolor, arrowsize
            - spinbox.downarrow: background, relief, borderwidth, arrowcolor, arrowsize
            - spinbox.padding: padding, relief, shiftrelief
            - spinbox.textarea: font, width
        """
        disabled_fg = (
            ThemeColors.update_hsv(self.theme.colors.inputbg, vd=-0.2)
            if self.theme.type == "light"
            else ThemeColors.update_hsv(self.theme.colors.inputbg, vd=-0.3)
        )

        if self.theme.type == "dark":
            self.settings.update({"custom.Spinbox.field": {"element create": ("from", "default")}})

        self.settings.update(
            {
                "Spinbox.uparrow": {"element create": ("from", "default")},
                "Spinbox.downarrow": {"element create": ("from", "default")},
                "TSpinbox": {
                    "layout": [
                        (
                            "custom.Spinbox.field",
                            {
                                "side": "top",
                                "sticky": "we",
                                "children": [
                                    (
                                        "null",
                                        {
                                            "side": "right",
                                            "sticky": "",
                                            "children": [
                                                ("Spinbox.uparrow", {"side": "top", "sticky": "e"}),
                                                ("Spinbox.downarrow", {"side": "bottom", "sticky": "e"}),
                                            ],
                                        },
                                    ),
                                    (
                                        "Spinbox.padding",
                                        {
                                            "sticky": "nswe",
                                            "children": [("Spinbox.textarea", {"sticky": "nswe"})],
                                        },
                                    ),
                                ],
                            },
                        )
                    ],
                    "configure": {
                        "bordercolor": self.theme.colors.border,
                        "darkcolor": self.theme.colors.inputbg,
                        "lightcolor": self.theme.colors.inputbg,
                        "fieldbackground": self.theme.colors.inputbg,
                        "foreground": self.theme.colors.inputfg,
                        "borderwidth": 0,
                        "background": self.theme.colors.inputbg,
                        "relief": "flat",
                        "arrowcolor": self.theme.colors.inputfg,
                        "arrowsize": 14,
                        "padding": (10, 5),
                    },
                    "map": {
                        "foreground": [("disabled", disabled_fg)],
                        "bordercolor": [
                            ("focus !disabled", self.theme.colors.primary),
                            ("hover !disabled", self.theme.colors.bg),
                        ],
                        "lightcolor": [
                            ("focus !disabled", self.theme.colors.primary),
                            ("hover !disabled", self.theme.colors.primary),
                        ],
                        "darkcolor": [
                            ("focus !disabled", self.theme.colors.primary),
                            ("hover !disabled", self.theme.colors.primary),
                        ],
                        "arrowcolor": [
                            ("disabled !disabled", disabled_fg),
                            ("pressed !disabled", self.theme.colors.primary),
                            ("focus !disabled", self.theme.colors.inputfg),
                            ("hover !disabled", self.theme.colors.inputfg),
                        ],
                    },
                },
            }
        )

        for color in self.theme.colors:
            self.settings.update(
                {
                    f"{color}.TSpinbox": {
                        "map": {
                            "foreground": [("disabled", disabled_fg)],
                            "bordercolor": [
                                ("focus !disabled", self.theme.colors.get(color)),
                                ("hover !disabled", self.theme.colors.get(color)),
                            ],
                            "arrowcolor": [
                                ("disabled !disabled", disabled_fg),
                                ("pressed !disabled", self.theme.colors.get(color)),
                                ("hover !disabled", self.theme.colors.inputfg),
                            ],
                            "lightcolor": [("focus !disabled", self.theme.colors.get(color))],
                            "darkcolor": [("focus !disabled", self.theme.colors.get(color))],
                        }
                    }
                }
            )

    def _style_treeview(self):
        """Create style configuration for ttk treeview: *ttk.Treeview*. This widget uses elements from the *alt* and
        *clam* theme to create the widget layout.

        The options available in this widget include:

            Treeview:

                - Treeview.field: bordercolor, lightcolor, darkcolor, fieldbackground
                - Treeview.padding: padding, relief, shiftrelief
                - Treeview.treearea

            Item:

                - Treeitem.padding: padding, relief, shiftrelief
                - Treeitem.indicator: foreground, diameter, indicatormargins
                - Treeitem.image: image, stipple, background
                - Treeitem.focus: focuscolor, focusthickness
                - Treeitem.text: text, font, foreground, underline, width, anchor, justify, wraplength, embossed

            Heading:

                - Treeheading.cell: background, rownumber
                - Treeheading.border: bordercolor, lightcolor, darkcolor, relief, borderwidth
                - Treeheading.padding: padding, relief, shiftrelief
                - Treeheading.image: image, stipple, background
                - Treeheading.text: text, font, foreground, underline, width, anchor, justify, wraplength, embossed

            Cell:
                - Treedata.padding: padding, relief, shiftrelief
                - Treeitem.text: text, font, foreground, underline, width, anchor, justify, wraplength, embossed

        """
        disabled_fg = (
            ThemeColors.update_hsv(self.theme.colors.inputbg, vd=-0.2)
            if self.theme.type == "light"
            else ThemeColors.update_hsv(self.theme.colors.inputbg, vd=-0.3)
        )

        self.settings.update(
            {
                "Treeview": {
                    "layout": [
                        (
                            "Button.border",
                            {
                                "sticky": "nswe",
                                "border": "1",
                                "children": [
                                    (
                                        "Treeview.padding",
                                        {
                                            "sticky": "nswe",
                                            "children": [("Treeview.treearea", {"sticky": "nswe"})],
                                        },
                                    )
                                ],
                            },
                        )
                    ],
                    "configure": {
                        "background": self.theme.colors.inputbg,
                        "foreground": self.theme.colors.inputfg,
                        "bordercolor": self.theme.colors.bg,
                        "lightcolor": self.theme.colors.border,
                        "darkcolor": self.theme.colors.border,
                        "relief": "raised" if self.theme.type == "light" else "flat",
                        "padding": 0 if self.theme.type == "light" else -2,
                    },
                    "map": {
                        "background": [("selected", self.theme.colors.selectbg)],
                        "foreground": [("disabled", disabled_fg), ("selected", self.theme.colors.selectfg)],
                    },
                },
                "Treeview.Heading": {
                    "configure": {
                        "background": self.theme.colors.primary,
                        "foreground": self.theme.colors.selectfg,
                        "relief": "flat",
                        "padding": 5,
                    }
                },
                "Treeitem.indicator": {"element create": ("from", "alt")},
            }
        )

        for color in self.theme.colors:
            self.settings.update(
                {
                    f"{color}.Treeview.Heading": {
                        "configure": {"background": self.theme.colors.get(color)},
                        "map": {
                            "foreground": [("disabled", disabled_fg)],
                            "bordercolor": [("focus !disabled", self.theme.colors.get(color))],
                        },
                    }
                }
            )

    def _style_frame(self):
        """Create style configuration for ttk frame: *ttk.Frame*

        The options available in this widget include:

            - Frame.border: bordercolor, lightcolor, darkcolor, relief, borderwidth
        """
        self.settings.update({"TFrame": {"configure": {"background": self.theme.colors.bg}}})

        for color in self.theme.colors:
            self.settings.update({f"{color}.TFrame": {"configure": {"background": self.theme.colors.get(color)}}})

    @staticmethod
    def style_solid_buttons(theme, anchor="center", background=None, font=None, foreground=None, style=None):
        """Apply a solid color style to ttk button: *ttk.Button*

        Args:
            theme (str): The theme name.
            anchor (str, optional): The position of the text inside of the button.
            background (str, optional): The color of the button background.
            font (str, optional): The font used to render the button text.
            foreground (str, optional): The color of the button text.
            style (str, optional): The style used to render the widget.

        Returns:
            dict: A dictionary of theme settings.
        """
        # fallback colors
        background = ThemeColors.normalize(background, theme.colors.primary, theme.colors)
        foreground = ThemeColors.normalize(foreground, theme.colors.selectfg, theme.colors)

        # disabled colors
        disabled_fg = theme.colors.inputfg
        disabled_bg = (
            ThemeColors.update_hsv(theme.colors.inputbg, vd=-0.2)
            if theme.type == "light"
            else ThemeColors.update_hsv(theme.colors.inputbg, vd=-0.3)
        )

        # pressed and hover color settings
        pressed_vd = -0.2
        hover_vd = -0.1

        settings = dict()
        settings.update(
            {
                f"{style}": {
                    "configure": {
                        "anchor": anchor or "center",
                        "foreground": foreground,
                        "background": background,
                        "bordercolor": background,
                        "darkcolor": background,
                        "lightcolor": background,
                        "relief": "raised",
                        "font": font or DEFAULT_FONT,
                        "focusthickness": 0,
                        "focuscolor": "",
                        "padding": (10, 5),
                    },
                    "map": {
                        "foreground": [("disabled", disabled_fg)],
                        "background": [
                            ("disabled", disabled_bg),
                            ("pressed !disabled", ThemeColors.update_hsv(background, vd=pressed_vd)),
                            ("hover !disabled", ThemeColors.update_hsv(background, vd=hover_vd)),
                        ],
                        "bordercolor": [
                            ("disabled", disabled_bg),
                            ("hover !disabled", ThemeColors.update_hsv(background, vd=hover_vd)),
                        ],
                        "darkcolor": [
                            ("disabled", disabled_bg),
                            ("pressed !disabled", ThemeColors.update_hsv(background, vd=pressed_vd)),
                            ("hover !disabled", ThemeColors.update_hsv(background, vd=hover_vd)),
                        ],
                        "lightcolor": [
                            ("disabled", disabled_bg),
                            ("pressed !disabled", ThemeColors.update_hsv(background, vd=pressed_vd)),
                            ("hover !disabled", ThemeColors.update_hsv(background, vd=hover_vd)),
                        ],
                    },
                }
            }
        )
        return settings

    @staticmethod
    def style_outline_buttons(theme, anchor="center", background=None, font=None, foreground=None, style=None):
        """Apply an outline style to ttk button: *ttk.Button*.

        The outline and text are colored with the ``foreground``, and the remaining fill is set with the ``background``
        color. When hovered, the widget inverts ``foreground`` and ``background`` colors.

        Args:
            theme (str): The theme name.
            anchor (str, optional): The position of the text inside of the button.
            background (str, optional): The color of the button background.
            font (str, optional): The font used to render the button text.
            foreground (str, optional): The color of the outline and button text.
            style (str, optional): The style used to render the widget.

        Returns:
            dict: A dictionary of theme settings.
        """
        # fallback colors
        background = ThemeColors.normalize(background, theme.colors.bg, theme.colors)
        foreground = ThemeColors.normalize(foreground, theme.colors.primary, theme.colors)

        # disabled color settings
        if theme.type == "light":
            disabled_fg = ThemeColors.update_hsv(theme.colors.inputbg, vd=-0.2)
        else:
            disabled_fg = ThemeColors.update_hsv(theme.colors.inputbg, vd=-0.3)

        # pressed color settings
        pressed_vd = -0.1

        settings = dict()
        settings.update(
            {
                f"{style}": {
                    "configure": {
                        "anchor": anchor or "center",
                        "foreground": foreground,
                        "background": background,
                        "bordercolor": foreground,
                        "darkcolor": background,
                        "lightcolor": background,
                        "relief": "raised",
                        "font": font or DEFAULT_FONT,
                        "focusthickness": 0,
                        "focuscolor": "",
                        "padding": (10, 5),
                    },
                    "map": {
                        "foreground": [("disabled", disabled_fg), ("pressed", background), ("hover", background)],
                        "background": [
                            ("pressed !disabled", ThemeColors.update_hsv(foreground, vd=pressed_vd)),
                            ("hover !disabled", foreground),
                        ],
                        "bordercolor": [
                            ("pressed !disabled", ThemeColors.update_hsv(foreground, vd=pressed_vd)),
                            ("hover !disabled", foreground),
                        ],
                        "darkcolor": [
                            ("pressed !disabled", ThemeColors.update_hsv(foreground, vd=pressed_vd)),
                            ("hover !disabled", foreground),
                        ],
                        "lightcolor": [
                            ("pressed !disabled", ThemeColors.update_hsv(foreground, vd=pressed_vd)),
                            ("hover !disabled", foreground),
                        ],
                    },
                }
            }
        )
        return settings

    @staticmethod
    def style_link_buttons(theme, anchor="center", background=None, font=None, foreground=None, style=None):
        """Apply a hyperlink style to ttk button: *ttk.Button*

        Args:
            theme (str): The theme name.
            anchor (str, optional): The position of the text inside of the button.
            background (str, optional): The color of the button background.
            font (str, optional): The font used to render the button text.
            foreground (str, optional): The color of the button text.
            style (str, optional): The style used to render the widget.

        Returns:
            dict: A dictionary of theme settings.
        """
        # fallback colors
        background = ThemeColors.normalize(background, theme.colors.bg, theme.colors)
        foreground = ThemeColors.normalize(foreground, theme.colors.fg, theme.colors)

        # disabled color settings
        if theme.type == "light":
            disabled_fg = ThemeColors.update_hsv(theme.colors.inputbg, vd=-0.2)
        else:
            disabled_fg = ThemeColors.update_hsv(theme.colors.inputbg, vd=-0.3)

        settings = dict()
        settings.update(
            {
                f"{style}": {
                    "configure": {
                        "anchor": anchor or "center",
                        "foreground": foreground,
                        "background": background,
                        "bordercolor": background,
                        "darkcolor": background,
                        "lightcolor": background,
                        "relief": "raised",
                        "font": font or DEFAULT_FONT,
                        "focusthickness": 0,
                        "focuscolor": "",
                        "padding": (10, 5),
                    },
                    "map": {
                        "foreground": [
                            ("disabled", disabled_fg),
                            ("pressed !disabled", theme.colors.info),
                            ("hover !disabled", theme.colors.info),
                        ],
                        "shiftrelief": [("pressed !disabled", -1)],
                        "background": [],
                        "bordercolor": [],
                        "darkcolor": [],
                        "lightcolor": [],
                    },
                }
            }
        )
        return settings

    def _style_link_buttons(self):
        """Apply a solid color style to ttk button: *ttk.Button*

        The options available in this widget include:

            - Button.border: bordercolor, lightcolor, darkcolor, relief, borderwidth
            - Button.focus: focuscolor, focusthickness
            - Button.padding: padding, relief, shiftrelief
            - Button.label: compound, space, text, font, foreground, underline, width, anchor, justify, wraplength,
                embossed, image, stipple, background
        """
        # disabled settings
        disabled_fg = (
            ThemeColors.update_hsv(self.theme.colors.inputbg, vd=-0.2)
            if self.theme.type == "light"
            else ThemeColors.update_hsv(self.theme.colors.inputbg, vd=-0.3)
        )

        # pressed and hover settings
        pressed_vd = 0
        hover_vd = 0

        self.settings.update(
            {
                "Link.TButton": {
                    "configure": {
                        "foreground": self.theme.colors.fg,
                        "background": self.theme.colors.bg,
                        "bordercolor": self.theme.colors.bg,
                        "darkcolor": self.theme.colors.bg,
                        "lightcolor": self.theme.colors.bg,
                        "relief": "raised",
                        "font": self.theme.font,
                        "focusthickness": 0,
                        "focuscolor": "",
                        "padding": (10, 5),
                    },
                    "map": {
                        "foreground": [
                            ("disabled", disabled_fg),
                            (
                                "pressed !disabled",
                                ThemeColors.update_hsv(self.theme.colors.info, vd=pressed_vd),
                            ),
                            ("hover !disabled", ThemeColors.update_hsv(self.theme.colors.info, vd=hover_vd)),
                        ],
                        "shiftrelief": [("pressed !disabled", -1)],
                        "background": [
                            ("pressed !disabled", self.theme.colors.bg),
                            ("hover !disabled", self.theme.colors.bg),
                        ],
                        "bordercolor": [
                            ("disabled", disabled_fg),
                            ("pressed !disabled", self.theme.colors.bg),
                            ("hover !disabled", self.theme.colors.bg),
                        ],
                        "darkcolor": [
                            ("pressed !disabled", self.theme.colors.bg),
                            ("hover !disabled", self.theme.colors.bg),
                        ],
                        "lightcolor": [
                            ("pressed !disabled", self.theme.colors.bg),
                            ("hover !disabled", self.theme.colors.bg),
                        ],
                    },
                }
            }
        )

        for color in self.theme.colors:
            self.settings.update(
                {
                    f"{color}.Link.TButton": {
                        "configure": {
                            "foreground": self.theme.colors.get(color),
                            "background": self.theme.colors.bg,
                            "bordercolor": self.theme.colors.bg,
                            "darkcolor": self.theme.colors.bg,
                            "lightcolor": self.theme.colors.bg,
                            "relief": "raised",
                            "font": self.theme.font,
                            "focusthickness": 0,
                            "focuscolor": "",
                            "padding": (10, 5),
                        },
                        "map": {
                            "foreground": [
                                ("disabled", disabled_fg),
                                (
                                    "pressed !disabled",
                                    ThemeColors.update_hsv(self.theme.colors.info, vd=pressed_vd),
                                ),
                                (
                                    "hover !disabled",
                                    ThemeColors.update_hsv(self.theme.colors.info, vd=hover_vd),
                                ),
                            ],
                            "shiftrelief": [("pressed !disabled", -1)],
                            "background": [
                                ("pressed !disabled", self.theme.colors.bg),
                                ("hover !disabled", self.theme.colors.bg),
                            ],
                            "bordercolor": [
                                ("disabled", disabled_fg),
                                ("pressed !disabled", self.theme.colors.bg),
                                ("hover !disabled", self.theme.colors.bg),
                            ],
                            "darkcolor": [
                                ("pressed !disabled", self.theme.colors.bg),
                                ("hover !disabled", self.theme.colors.bg),
                            ],
                            "lightcolor": [
                                ("pressed !disabled", self.theme.colors.bg),
                                ("hover !disabled", self.theme.colors.bg),
                            ],
                        },
                    }
                }
            )

    def _create_squaretoggle_image(self, colorname):
        """Create a set of images for the square toggle button and return as ``PhotoImage``

        Args:
            colorname (str): the color label assigned to the colors property

        Returns:
            Tuple[PhotoImage]: a tuple of images (toggle_on, toggle_off, toggle_disabled)
        """
        prime_color = self.theme.colors.get(colorname)
        on_border = prime_color
        on_indicator = prime_color
        on_fill = self.theme.colors.bg
        off_border = self.theme.colors.selectbg if self.theme.type == "light" else self.theme.colors.inputbg
        off_indicator = self.theme.colors.selectbg if self.theme.type == "light" else self.theme.colors.inputbg
        off_fill = self.theme.colors.bg
        disabled_fill = self.theme.colors.bg
        disabled_fg = (
            ThemeColors.update_hsv(self.theme.colors.inputbg, vd=-0.2)
            if self.theme.type == "light"
            else ThemeColors.update_hsv(self.theme.colors.inputbg, vd=-0.3)
        )

        toggle_off = Image.new("RGBA", (226, 130))
        draw = ImageDraw.Draw(toggle_off)
        draw.rectangle([1, 1, 225, 129], outline=off_border, width=6, fill=off_fill)
        draw.rectangle([18, 18, 110, 110], fill=off_indicator)

        toggle_on = Image.new("RGBA", (226, 130))
        draw = ImageDraw.Draw(toggle_on)
        draw.rectangle([1, 1, 225, 129], outline=on_border, width=6, fill=on_fill)
        draw.rectangle([18, 18, 110, 110], fill=on_indicator)
        toggle_on = toggle_on.transpose(Image.ROTATE_180)

        toggle_disabled = Image.new("RGBA", (226, 130))
        draw = ImageDraw.Draw(toggle_disabled)
        draw.rectangle([1, 1, 225, 129], outline=disabled_fg, width=6)
        draw.rectangle([18, 18, 110, 110], fill=disabled_fg)

        images = {}
        images[f"{colorname}_squaretoggle_on"] = ImageTk.PhotoImage(toggle_on.resize((24, 15), Image.LANCZOS))
        images[f"{colorname}_squaretoggle_off"] = ImageTk.PhotoImage(toggle_off.resize((24, 15), Image.LANCZOS))
        images[f"{colorname}_squaretoggle_disabled"] = ImageTk.PhotoImage(
            toggle_disabled.resize((24, 15), Image.LANCZOS)
        )
        return images

    def _create_roundtoggle_image(self, colorname):
        """Create a set of images for the rounded toggle button and return as ``PhotoImage``

        Args:
            colorname (str): the color label assigned to the colors property

        Returns:
            Tuple[PhotoImage]
        """
        prime_color = self.theme.colors.get(colorname)
        on_border = prime_color
        on_indicator = self.theme.colors.selectfg
        on_fill = prime_color
        off_border = self.theme.colors.selectbg if self.theme.type == "light" else self.theme.colors.inputbg
        off_indicator = self.theme.colors.selectbg if self.theme.type == "light" else self.theme.colors.inputbg
        off_fill = self.theme.colors.bg
        disabled_fill = self.theme.colors.bg
        disabled_fg = (
            ThemeColors.update_hsv(self.theme.colors.inputbg, vd=-0.2)
            if self.theme.type == "light"
            else ThemeColors.update_hsv(self.theme.colors.inputbg, vd=-0.3)
        )

        toggle_off = Image.new("RGBA", (226, 130))
        draw = ImageDraw.Draw(toggle_off)
        draw.rounded_rectangle([1, 1, 225, 129], radius=(128 / 2), outline=off_border, width=6, fill=off_fill)
        draw.ellipse([20, 18, 112, 110], fill=off_indicator)

        toggle_on = Image.new("RGBA", (226, 130))
        draw = ImageDraw.Draw(toggle_on)
        draw.rounded_rectangle([1, 1, 225, 129], radius=(128 / 2), outline=on_border, width=6, fill=on_fill)
        draw.ellipse([20, 18, 112, 110], fill=on_indicator)
        toggle_on = toggle_on.transpose(Image.ROTATE_180)

        toggle_disabled = Image.new("RGBA", (226, 130))
        draw = ImageDraw.Draw(toggle_disabled)
        draw.rounded_rectangle([1, 1, 225, 129], radius=(128 / 2), outline=disabled_fg, width=6)
        draw.ellipse([20, 18, 112, 110], fill=disabled_fg)

        images = {}
        images[f"{colorname}_roundtoggle_on"] = ImageTk.PhotoImage(toggle_on.resize((24, 15), Image.LANCZOS))
        images[f"{colorname}_roundtoggle_off"] = ImageTk.PhotoImage(toggle_off.resize((24, 15), Image.LANCZOS))
        images[f"{colorname}_roundtoggle_disabled"] = ImageTk.PhotoImage(
            toggle_disabled.resize((24, 15), Image.LANCZOS)
        )
        return images

    def _style_roundtoggle_toolbutton(self):
        """Apply a rounded toggle switch style to ttk widgets that accept the toolbutton style (for example, a
        checkbutton: *ttk.Checkbutton*)
        """
        self.theme_images.update(self._create_roundtoggle_image("primary"))
        disabled_fg = (
            ThemeColors.update_hsv(self.theme.colors.inputbg, vd=-0.2)
            if self.theme.type == "light"
            else ThemeColors.update_hsv(self.theme.colors.inputbg, vd=-0.3)
        )

        # create indicator element
        self.settings.update(
            {
                "Roundtoggle.Toolbutton.indicator": {
                    "element create": (
                        "image",
                        self.theme_images["primary_roundtoggle_on"],
                        ("disabled", self.theme_images["primary_roundtoggle_disabled"]),
                        ("!selected", self.theme_images["primary_roundtoggle_off"]),
                        {"width": 28, "border": 4, "sticky": "w"},
                    )
                },
                "Roundtoggle.Toolbutton": {
                    "layout": [
                        (
                            "Toolbutton.border",
                            {
                                "sticky": "nswe",
                                "children": [
                                    (
                                        "Toolbutton.padding",
                                        {
                                            "sticky": "nswe",
                                            "children": [
                                                ("Roundtoggle.Toolbutton.indicator", {"side": "left"}),
                                                ("Toolbutton.label", {"side": "left"}),
                                            ],
                                        },
                                    )
                                ],
                            },
                        )
                    ],
                    "configure": {"relief": "flat", "borderwidth": 0, "foreground": self.theme.colors.fg},
                    "map": {
                        "foreground": [("disabled", disabled_fg), ("hover", self.theme.colors.primary)],
                        "background": [
                            ("selected", self.theme.colors.bg),
                            ("!selected", self.theme.colors.bg),
                        ],
                    },
                },
            }
        )

        # color variations
        for color in self.theme.colors:
            self.theme_images.update(self._create_roundtoggle_image(color))

            # create indicator element
            self.settings.update(
                {
                    f"{color}.Roundtoggle.Toolbutton.indicator": {
                        "element create": (
                            "image",
                            self.theme_images[f"{color}_roundtoggle_on"],
                            ("disabled", self.theme_images[f"{color}_roundtoggle_disabled"]),
                            ("!selected", self.theme_images[f"{color}_roundtoggle_off"]),
                            {"width": 28, "border": 4, "sticky": "w"},
                        )
                    },
                    f"{color}.Roundtoggle.Toolbutton": {
                        "layout": [
                            (
                                "Toolbutton.border",
                                {
                                    "sticky": "nswe",
                                    "children": [
                                        (
                                            "Toolbutton.padding",
                                            {
                                                "sticky": "nswe",
                                                "children": [
                                                    (
                                                        f"{color}.Roundtoggle.Toolbutton.indicator",
                                                        {"side": "left"},
                                                    ),
                                                    ("Toolbutton.label", {"side": "left"}),
                                                ],
                                            },
                                        )
                                    ],
                                },
                            )
                        ],
                        "configure": {"relief": "flat", "borderwidth": 0, "foreground": self.theme.colors.fg},
                        "map": {
                            "foreground": [
                                ("disabled", disabled_fg),
                                ("hover", self.theme.colors.get(color)),
                            ],
                            "background": [
                                ("selected", self.theme.colors.bg),
                                ("!selected", self.theme.colors.bg),
                            ],
                        },
                    },
                }
            )

    def _style_squaretoggle_toolbutton(self):
        """Apply a square toggle switch style to ttk widgets that accept the toolbutton style (for example, a
        checkbutton: *ttk.Checkbutton*)
        """
        self.theme_images.update(self._create_squaretoggle_image("primary"))
        disabled_fg = (
            ThemeColors.update_hsv(self.theme.colors.inputbg, vd=-0.2)
            if self.theme.type == "light"
            else ThemeColors.update_hsv(self.theme.colors.inputbg, vd=-0.3)
        )

        # create indicator element
        self.settings.update(
            {
                "Squaretoggle.Toolbutton.indicator": {
                    "element create": (
                        "image",
                        self.theme_images["primary_squaretoggle_on"],
                        ("disabled", self.theme_images["primary_squaretoggle_disabled"]),
                        ("!selected", self.theme_images["primary_squaretoggle_off"]),
                        {"width": 28, "border": 4, "sticky": "w"},
                    )
                },
                "Squaretoggle.Toolbutton": {
                    "layout": [
                        (
                            "Toolbutton.border",
                            {
                                "sticky": "nswe",
                                "children": [
                                    (
                                        "Toolbutton.padding",
                                        {
                                            "sticky": "nswe",
                                            "children": [
                                                ("Squaretoggle.Toolbutton.indicator", {"side": "left"}),
                                                ("Toolbutton.label", {"side": "left"}),
                                            ],
                                        },
                                    )
                                ],
                            },
                        )
                    ],
                    "configure": {"relief": "flat", "borderwidth": 0, "foreground": self.theme.colors.fg},
                    "map": {
                        "foreground": [("disabled", disabled_fg), ("hover", self.theme.colors.primary)],
                        "background": [
                            ("selected", self.theme.colors.bg),
                            ("!selected", self.theme.colors.bg),
                        ],
                    },
                },
            }
        )

        # color variations
        for color in self.theme.colors:
            self.theme_images.update(self._create_squaretoggle_image(color))

            # create indicator element
            self.settings.update(
                {
                    f"{color}.Squaretoggle.Toolbutton.indicator": {
                        "element create": (
                            "image",
                            self.theme_images[f"{color}_squaretoggle_on"],
                            ("disabled", self.theme_images[f"{color}_squaretoggle_disabled"]),
                            ("!selected", self.theme_images[f"{color}_squaretoggle_off"]),
                            {"width": 28, "border": 4, "sticky": "w"},
                        )
                    },
                    f"{color}.Squaretoggle.Toolbutton": {
                        "layout": [
                            (
                                "Toolbutton.border",
                                {
                                    "sticky": "nswe",
                                    "children": [
                                        (
                                            "Toolbutton.padding",
                                            {
                                                "sticky": "nswe",
                                                "children": [
                                                    (
                                                        f"{color}.Squaretoggle.Toolbutton.indicator",
                                                        {"side": "left"},
                                                    ),
                                                    ("Toolbutton.label", {"side": "left"}),
                                                ],
                                            },
                                        )
                                    ],
                                },
                            )
                        ],
                        "configure": {"relief": "flat", "borderwidth": 0, "foreground": self.theme.colors.fg},
                        "map": {
                            "foreground": [
                                ("disabled", disabled_fg),
                                ("hover", self.theme.colors.get(color)),
                            ],
                            "background": [
                                ("selected", self.theme.colors.bg),
                                ("!selected", self.theme.colors.bg),
                            ],
                        },
                    },
                }
            )

    def _style_solid_toolbutton(self):
        """Apply a solid color style to ttk widgets that use the Toolbutton style (for example, a checkbutton:
        *ttk.Checkbutton*)

        The options available in this widget include:

            - Button.border: bordercolor, lightcolor, darkcolor, relief, borderwidth
            - Button.focus: focuscolor, focusthickness
            - Button.padding: padding, relief, shiftrelief
            - Button.label: compound, space, text, font, foreground, underline, width, anchor, justify, wraplength,
                embossed, image, stipple, background
        """
        # disabled settings
        disabled_fg = self.theme.colors.inputfg
        disabled_bg = (
            ThemeColors.update_hsv(self.theme.colors.inputbg, vd=-0.2)
            if self.theme.type == "light"
            else ThemeColors.update_hsv(self.theme.colors.inputbg, vd=-0.3)
        )

        # pressed and hover settings
        pressed_vd = -0.2
        hover_vd = -0.1
        normal_sd = -0.5
        normal_vd = 0.1

        self.settings.update(
            {
                "Toolbutton": {
                    "configure": {
                        "foreground": self.theme.colors.selectfg,
                        "background": ThemeColors.update_hsv(self.theme.colors.primary, sd=normal_sd, vd=normal_vd),
                        "bordercolor": ThemeColors.update_hsv(self.theme.colors.primary, sd=normal_sd, vd=normal_vd),
                        "darkcolor": ThemeColors.update_hsv(self.theme.colors.primary, sd=normal_sd, vd=normal_vd),
                        "lightcolor": ThemeColors.update_hsv(self.theme.colors.primary, sd=normal_sd, vd=normal_vd),
                        "font": self.theme.font,
                        "anchor": "center",
                        "relief": "raised",
                        "focusthickness": 0,
                        "focuscolor": "",
                        "padding": (10, 5),
                    },
                    "map": {
                        "foreground": [("disabled", disabled_fg)],
                        "background": [
                            ("disabled", disabled_bg),
                            ("pressed !disabled", self.theme.colors.primary),
                            ("selected !disabled", self.theme.colors.primary),
                            ("hover !disabled", self.theme.colors.primary),
                        ],
                        "bordercolor": [
                            ("disabled", disabled_bg),
                            ("selected !disabled", self.theme.colors.primary),
                            ("pressed !disabled", self.theme.colors.primary),
                            ("hover !disabled", self.theme.colors.primary),
                        ],
                        "darkcolor": [
                            ("disabled", disabled_bg),
                            ("pressed !disabled", self.theme.colors.primary),
                            ("selected !disabled", self.theme.colors.primary),
                            ("hover !disabled", self.theme.colors.primary),
                        ],
                        "lightcolor": [
                            ("disabled", disabled_bg),
                            ("pressed !disabled", self.theme.colors.primary),
                            ("selected !disabled", self.theme.colors.primary),
                            ("hover !disabled", self.theme.colors.primary),
                        ],
                    },
                }
            }
        )

        for color in self.theme.colors:
            self.settings.update(
                {
                    f"{color}.Toolbutton": {
                        "configure": {
                            "foreground": self.theme.colors.selectfg,
                            "background": ThemeColors.update_hsv(
                                self.theme.colors.get(color), sd=normal_sd, vd=normal_vd
                            ),
                            "bordercolor": ThemeColors.update_hsv(
                                self.theme.colors.get(color), sd=normal_sd, vd=normal_vd
                            ),
                            "darkcolor": ThemeColors.update_hsv(
                                self.theme.colors.get(color), sd=normal_sd, vd=normal_vd
                            ),
                            "lightcolor": ThemeColors.update_hsv(
                                self.theme.colors.get(color), sd=normal_sd, vd=normal_vd
                            ),
                            "relief": "raised",
                            "focusthickness": 0,
                            "focuscolor": "",
                            "padding": (10, 5),
                        },
                        "map": {
                            "foreground": [("disabled", disabled_fg)],
                            "background": [
                                ("disabled", disabled_bg),
                                ("pressed !disabled", self.theme.colors.get(color)),
                                ("selected !disabled", self.theme.colors.get(color)),
                                ("hover !disabled", self.theme.colors.get(color)),
                            ],
                            "bordercolor": [
                                ("disabled", disabled_bg),
                                ("pressed !disabled", self.theme.colors.get(color)),
                                ("selected !disabled", self.theme.colors.get(color)),
                                ("hover !disabled", self.theme.colors.get(color)),
                            ],
                            "darkcolor": [
                                ("disabled", disabled_bg),
                                ("pressed !disabled", self.theme.colors.get(color)),
                                ("selected !disabled", self.theme.colors.get(color)),
                                ("hover !disabled", self.theme.colors.get(color)),
                            ],
                            "lightcolor": [
                                ("disabled", disabled_bg),
                                ("pressed !disabled", self.theme.colors.get(color)),
                                ("selected !disabled", self.theme.colors.get(color)),
                                ("hover !disabled", self.theme.colors.get(color)),
                            ],
                        },
                    }
                }
            )

    def _style_outline_toolbutton(self):
        """Apply an outline style to ttk widgets that use the Toolbutton style (for example, a checkbutton:
        *ttk.Checkbutton*). This button has a solid button look on focus and hover.

        The options available in this widget include:

            - Button.border: bordercolor, lightcolor, darkcolor, relief, borderwidth
            - Button.focus: focuscolor, focusthickness
            - Button.padding: padding, relief, shiftrelief
            - Button.label: compound, space, text, font, foreground, underline, width, anchor, justify, wraplength,
                embossed, image, stipple, background
        """
        # disabled settings
        disabled_fg = (
            ThemeColors.update_hsv(self.theme.colors.inputbg, vd=-0.2)
            if self.theme.type == "light"
            else ThemeColors.update_hsv(self.theme.colors.inputbg, vd=-0.3)
        )

        # pressed and hover settings
        pressed_vd = -0.10

        self.settings.update(
            {
                "Outline.Toolbutton": {
                    "configure": {
                        "foreground": self.theme.colors.primary,
                        "background": self.theme.colors.bg,
                        "bordercolor": self.theme.colors.border,
                        "darkcolor": self.theme.colors.bg,
                        "lightcolor": self.theme.colors.bg,
                        "relief": "raised",
                        "font": self.theme.font,
                        "focusthickness": 0,
                        "focuscolor": "",
                        "borderwidth": 1,
                        "padding": (10, 5),
                    },
                    "map": {
                        "foreground": [
                            ("disabled", disabled_fg),
                            ("pressed !disabled", self.theme.colors.selectfg),
                            ("selected !disabled", self.theme.colors.selectfg),
                            ("hover !disabled", self.theme.colors.selectfg),
                        ],
                        "background": [
                            (
                                "pressed !disabled",
                                ThemeColors.update_hsv(self.theme.colors.primary, vd=pressed_vd),
                            ),
                            (
                                "selected !disabled",
                                ThemeColors.update_hsv(self.theme.colors.primary, vd=pressed_vd),
                            ),
                            ("hover !disabled", self.theme.colors.primary),
                        ],
                        "bordercolor": [
                            ("disabled", disabled_fg),
                            (
                                "pressed !disabled",
                                ThemeColors.update_hsv(self.theme.colors.primary, vd=pressed_vd),
                            ),
                            (
                                "selected !disabled",
                                ThemeColors.update_hsv(self.theme.colors.primary, vd=pressed_vd),
                            ),
                            ("hover !disabled", self.theme.colors.primary),
                        ],
                        "darkcolor": [
                            (
                                "pressed !disabled",
                                ThemeColors.update_hsv(self.theme.colors.primary, vd=pressed_vd),
                            ),
                            (
                                "selected !disabled",
                                ThemeColors.update_hsv(self.theme.colors.primary, vd=pressed_vd),
                            ),
                            ("hover !disabled", self.theme.colors.primary),
                        ],
                        "lightcolor": [
                            (
                                "pressed !disabled",
                                ThemeColors.update_hsv(self.theme.colors.primary, vd=pressed_vd),
                            ),
                            (
                                "selected !disabled",
                                ThemeColors.update_hsv(self.theme.colors.primary, vd=pressed_vd),
                            ),
                            ("hover !disabled", self.theme.colors.primary),
                        ],
                    },
                }
            }
        )

        for color in self.theme.colors:
            self.settings.update(
                {
                    f"{color}.Outline.Toolbutton": {
                        "configure": {
                            "foreground": self.theme.colors.get(color),
                            "background": self.theme.colors.bg,
                            "bordercolor": self.theme.colors.border,
                            "darkcolor": self.theme.colors.bg,
                            "lightcolor": self.theme.colors.bg,
                            "relief": "raised",
                            "focusthickness": 0,
                            "focuscolor": "",
                            "borderwidth": 1,
                            "padding": (10, 5),
                        },
                        "map": {
                            "foreground": [
                                ("disabled", disabled_fg),
                                ("pressed !disabled", self.theme.colors.selectfg),
                                ("selected !disabled", self.theme.colors.selectfg),
                                ("hover !disabled", self.theme.colors.selectfg),
                            ],
                            "background": [
                                (
                                    "pressed !disabled",
                                    ThemeColors.update_hsv(self.theme.colors.get(color), vd=pressed_vd),
                                ),
                                (
                                    "selected !disabled",
                                    ThemeColors.update_hsv(self.theme.colors.get(color), vd=pressed_vd),
                                ),
                                ("hover !disabled", self.theme.colors.get(color)),
                            ],
                            "bordercolor": [
                                ("disabled", disabled_fg),
                                (
                                    "pressed !disabled",
                                    ThemeColors.update_hsv(self.theme.colors.get(color), vd=pressed_vd),
                                ),
                                (
                                    "selected !disabled",
                                    ThemeColors.update_hsv(self.theme.colors.get(color), vd=pressed_vd),
                                ),
                                ("hover !disabled", self.theme.colors.get(color)),
                            ],
                            "darkcolor": [
                                (
                                    "pressed !disabled",
                                    ThemeColors.update_hsv(self.theme.colors.get(color), vd=pressed_vd),
                                ),
                                (
                                    "selected !disabled",
                                    ThemeColors.update_hsv(self.theme.colors.get(color), vd=pressed_vd),
                                ),
                                ("hover !disabled", self.theme.colors.get(color)),
                            ],
                            "lightcolor": [
                                (
                                    "pressed !disabled",
                                    ThemeColors.update_hsv(self.theme.colors.get(color), vd=pressed_vd),
                                ),
                                (
                                    "selected !disabled",
                                    ThemeColors.update_hsv(self.theme.colors.get(color), vd=pressed_vd),
                                ),
                                ("hover !disabled", self.theme.colors.get(color)),
                            ],
                        },
                    }
                }
            )

    def _style_entry(self):
        """Create style configuration for ttk entry: *ttk.Entry*

        The options available in this widget include:

            - Entry.field: bordercolor, lightcolor, darkcolor, fieldbackground
            - Entry.padding: padding, relief, shiftrelief
            - Entry.textarea: font, width
        """
        disabled_fg = (
            ThemeColors.update_hsv(self.theme.colors.inputbg, vd=-0.2)
            if self.theme.type == "light"
            else ThemeColors.update_hsv(self.theme.colors.inputbg, vd=-0.3)
        )

        if self.theme.type == "dark":
            self.settings.update({"Entry.field": {"element create": ("from", "default")}})

        self.settings.update(
            {
                "TEntry": {
                    "configure": {
                        "bordercolor": self.theme.colors.border,
                        "darkcolor": self.theme.colors.inputbg,
                        "lightcolor": self.theme.colors.inputbg,
                        "fieldbackground": self.theme.colors.inputbg,
                        "foreground": self.theme.colors.inputfg,
                        "borderwidth": 0,  # only applies to border on darktheme
                        "padding": 5,
                    },
                    "map": {
                        "foreground": [("disabled", disabled_fg)],
                        "bordercolor": [
                            ("focus !disabled", self.theme.colors.primary),
                            ("hover !disabled", self.theme.colors.bg),
                        ],
                        "lightcolor": [
                            ("focus !disabled", self.theme.colors.primary),
                            ("hover !disabled", self.theme.colors.primary),
                        ],
                        "darkcolor": [
                            ("focus !disabled", self.theme.colors.primary),
                            ("hover !disabled", self.theme.colors.primary),
                        ],
                    },
                }
            }
        )

        for color in self.theme.colors:
            self.settings.update(
                {
                    f"{color}.TEntry": {
                        "map": {
                            "foreground": [("disabled", disabled_fg)],
                            "bordercolor": [
                                ("focus !disabled", self.theme.colors.get(color)),
                                ("hover !disabled", self.theme.colors.bg),
                            ],
                            "lightcolor": [
                                ("focus !disabled", self.theme.colors.get(color)),
                                ("hover !disabled", self.theme.colors.get(color)),
                            ],
                            "darkcolor": [
                                ("focus !disabled", self.theme.colors.get(color)),
                                ("hover !disabled", self.theme.colors.get(color)),
                            ],
                        }
                    }
                }
            )

    def _style_radiobutton(self):
        """Create style configuration for ttk radiobutton: *ttk.Radiobutton*

        The options available in this widget include:

            - Radiobutton.padding: padding, relief, shiftrelief
            - Radiobutton.indicator: indicatorsize, indicatormargin, indicatorbackground, indicatorforeground,
                upperbordercolor, lowerbordercolor
            - Radiobutton.label: compound, space, text, font, foreground, underline, width, anchor, justify, wraplength,
                embossed, image, stipple, background
        """
        disabled_fg = (
            ThemeColors.update_hsv(self.theme.colors.inputbg, vd=-0.2)
            if self.theme.type == "light"
            else ThemeColors.update_hsv(self.theme.colors.inputbg, vd=-0.3)
        )
        disabled_bg = self.theme.colors.inputbg if self.theme.type == "light" else disabled_fg

        self.theme_images.update(self._create_radiobutton_images("primary"))
        self.settings.update(
            {
                "Radiobutton.indicator": {
                    "element create": (
                        "image",
                        self.theme_images["primary_radio_on"],
                        ("disabled", self.theme_images["primary_radio_disabled"]),
                        ("!selected", self.theme_images["primary_radio_off"]),
                        {"width": 20, "border": 4, "sticky": "w"},
                    )
                },
                "TRadiobutton": {
                    "layout": [
                        (
                            "Radiobutton.padding",
                            {
                                "children": [
                                    ("Radiobutton.indicator", {"side": "left", "sticky": ""}),
                                    (
                                        "Radiobutton.focus",
                                        {
                                            "children": [("Radiobutton.label", {"sticky": "nswe"})],
                                            "side": "left",
                                            "sticky": "",
                                        },
                                    ),
                                ],
                                "sticky": "nswe",
                            },
                        )
                    ],
                    "configure": {"font": self.theme.font},
                    "map": {
                        "foreground": [("disabled", disabled_fg), ("active", self.theme.colors.primary)],
                        "indicatorforeground": [
                            ("disabled", disabled_fg),
                            ("active selected !disabled", self.theme.colors.primary),
                        ],
                    },
                },
            }
        )

        # variations change the indicator color
        for color in self.theme.colors:
            self.theme_images.update(self._create_radiobutton_images(color))
            self.settings.update(
                {
                    f"{color}.Radiobutton.indicator": {
                        "element create": (
                            "image",
                            self.theme_images[f"{color}_radio_on"],
                            ("disabled", self.theme_images[f"{color}_radio_disabled"]),
                            ("!selected", self.theme_images[f"{color}_radio_off"]),
                            {"width": 20, "border": 4, "sticky": "w"},
                        )
                    },
                    f"{color}.TRadiobutton": {
                        "layout": [
                            (
                                "Radiobutton.padding",
                                {
                                    "children": [
                                        (f"{color}.Radiobutton.indicator", {"side": "left", "sticky": ""}),
                                        (
                                            "Radiobutton.focus",
                                            {
                                                "children": [("Radiobutton.label", {"sticky": "nswe"})],
                                                "side": "left",
                                                "sticky": "",
                                            },
                                        ),
                                    ],
                                    "sticky": "nswe",
                                },
                            )
                        ],
                        "configure": {"font": self.theme.font},
                        "map": {
                            "foreground": [
                                ("disabled", disabled_fg),
                                ("active", ThemeColors.update_hsv(self.theme.colors.get(color), vd=-0.2)),
                            ],
                            "indicatorforeground": [
                                ("disabled", disabled_fg),
                                (
                                    "active selected !disabled",
                                    ThemeColors.update_hsv(self.theme.colors.get(color), vd=-0.2),
                                ),
                            ],
                        },
                    },
                }
            )

    def _create_radiobutton_images(self, colorname):
        """Create radiobutton assets

        Args:
            colorname (str): the name of the color to use for the button on state

        Returns:
            Tuple[PhotoImage]: a tuple of widget images.
        """
        prime_color = self.theme.colors.get(colorname)
        on_border = prime_color if self.theme.type == "light" else self.theme.colors.selectbg
        on_indicator = self.theme.colors.selectfg if self.theme.type == "light" else prime_color
        on_fill = prime_color if self.theme.type == "light" else self.theme.colors.selectfg
        off_border = self.theme.colors.selectbg
        off_fill = self.theme.colors.inputbg if self.theme.type == "light" else self.theme.colors.selectfg
        disabled_fg = (
            ThemeColors.update_hsv(self.theme.colors.inputbg, vd=-0.2)
            if self.theme.type == "light"
            else ThemeColors.update_hsv(self.theme.colors.inputbg, vd=-0.3)
        )
        disabled_bg = self.theme.colors.inputbg if self.theme.type == "light" else disabled_fg

        # radio off
        radio_off = Image.new("RGBA", (134, 134))
        draw = ImageDraw.Draw(radio_off)
        draw.ellipse([2, 2, 132, 132], outline=off_border, width=3, fill=off_fill)

        # radio on
        radio_on = Image.new("RGBA", (134, 134))
        draw = ImageDraw.Draw(radio_on)
        draw.ellipse([2, 2, 132, 132], outline=on_border, width=12 if self.theme.type == "light" else 6, fill=on_fill)
        if self.theme.type == "light":
            # small indicator for light theme
            draw.ellipse([40, 40, 94, 94], fill=on_indicator)
        else:
            # large indicator for dark theme
            draw.ellipse([30, 30, 104, 104], fill=on_indicator)

        # radio disabled
        radio_disabled = Image.new("RGBA", (134, 134))
        draw = ImageDraw.Draw(radio_disabled)
        draw.ellipse([2, 2, 132, 132], outline=disabled_fg, width=3, fill=off_fill)

        return {
            f"{colorname}_radio_off": ImageTk.PhotoImage(radio_off.resize((14, 14), Image.LANCZOS)),
            f"{colorname}_radio_on": ImageTk.PhotoImage(radio_on.resize((14, 14), Image.LANCZOS)),
            f"{colorname}_radio_disabled": ImageTk.PhotoImage(radio_disabled.resize((14, 14), Image.LANCZOS)),
        }

    def _style_calendar(self):
        """Create style configuration for the ttkbootstrap.widgets.datechooser

        The options available in this widget include:

            - Label.border: bordercolor, lightcolor, darkcolor, relief, borderwidth
            - Label.padding: padding, relief, shiftrelief
            - Label.label: compound, space, text, font, foreground, underline, width, anchor, justify, wraplength,
                embossed, image, stipple, background
        """
        # disabled settings
        disabled_fg = (
            ThemeColors.update_hsv(self.theme.colors.inputbg, vd=-0.2)
            if self.theme.type == "light"
            else ThemeColors.update_hsv(self.theme.colors.inputbg, vd=-0.3)
        )

        # pressed and hover settings
        pressed_vd = -0.10

        self.settings.update(
            {
                "TCalendar": {
                    "layout": [
                        (
                            "Toolbutton.border",
                            {
                                "sticky": "nswe",
                                "children": [
                                    (
                                        "Toolbutton.padding",
                                        {
                                            "sticky": "nswe",
                                            "children": [("Toolbutton.label", {"sticky": "nswe"})],
                                        },
                                    )
                                ],
                            },
                        )
                    ],
                    "configure": {
                        "foreground": self.theme.colors.fg,
                        "background": self.theme.colors.bg,
                        "bordercolor": self.theme.colors.bg,
                        "darkcolor": self.theme.colors.bg,
                        "lightcolor": self.theme.colors.bg,
                        "relief": "raised",
                        "font": self.theme.font,
                        "focusthickness": 0,
                        "focuscolor": "",
                        "borderwidth": 1,
                        "anchor": "center",
                        "padding": (10, 5),
                    },
                    "map": {
                        "foreground": [
                            ("disabled", disabled_fg),
                            ("pressed !disabled", self.theme.colors.selectfg),
                            ("selected !disabled", self.theme.colors.selectfg),
                            ("hover !disabled", self.theme.colors.selectfg),
                        ],
                        "background": [
                            (
                                "pressed !disabled",
                                ThemeColors.update_hsv(self.theme.colors.primary, vd=pressed_vd),
                            ),
                            (
                                "selected !disabled",
                                ThemeColors.update_hsv(self.theme.colors.primary, vd=pressed_vd),
                            ),
                            ("hover !disabled", self.theme.colors.primary),
                        ],
                        "bordercolor": [
                            ("disabled", disabled_fg),
                            (
                                "pressed !disabled",
                                ThemeColors.update_hsv(self.theme.colors.primary, vd=pressed_vd),
                            ),
                            (
                                "selected !disabled",
                                ThemeColors.update_hsv(self.theme.colors.primary, vd=pressed_vd),
                            ),
                            ("hover !disabled", self.theme.colors.primary),
                        ],
                        "darkcolor": [
                            (
                                "pressed !disabled",
                                ThemeColors.update_hsv(self.theme.colors.primary, vd=pressed_vd),
                            ),
                            (
                                "selected !disabled",
                                ThemeColors.update_hsv(self.theme.colors.primary, vd=pressed_vd),
                            ),
                            ("hover !disabled", self.theme.colors.primary),
                        ],
                        "lightcolor": [
                            (
                                "pressed !disabled",
                                ThemeColors.update_hsv(self.theme.colors.primary, vd=pressed_vd),
                            ),
                            (
                                "selected !disabled",
                                ThemeColors.update_hsv(self.theme.colors.primary, vd=pressed_vd),
                            ),
                            ("hover !disabled", self.theme.colors.primary),
                        ],
                    },
                },
                "chevron.TButton": {"configure": {"font": "helvetica 14"}},
            }
        )

        for color in self.theme.colors:
            self.settings.update(
                {
                    f"{color}.TCalendar": {
                        "configure": {
                            "foreground": self.theme.colors.fg,
                            "background": self.theme.colors.bg,
                            "bordercolor": self.theme.colors.bg,
                            "darkcolor": self.theme.colors.bg,
                            "lightcolor": self.theme.colors.bg,
                            "relief": "raised",
                            "focusthickness": 0,
                            "focuscolor": "",
                            "borderwidth": 1,
                            "padding": (10, 5),
                        },
                        "map": {
                            "foreground": [
                                ("disabled", disabled_fg),
                                ("pressed !disabled", self.theme.colors.selectfg),
                                ("selected !disabled", self.theme.colors.selectfg),
                                ("hover !disabled", self.theme.colors.selectfg),
                            ],
                            "background": [
                                (
                                    "pressed !disabled",
                                    ThemeColors.update_hsv(self.theme.colors.get(color), vd=pressed_vd),
                                ),
                                (
                                    "selected !disabled",
                                    ThemeColors.update_hsv(self.theme.colors.get(color), vd=pressed_vd),
                                ),
                                ("hover !disabled", self.theme.colors.get(color)),
                            ],
                            "bordercolor": [
                                ("disabled", disabled_fg),
                                (
                                    "pressed !disabled",
                                    ThemeColors.update_hsv(self.theme.colors.get(color), vd=pressed_vd),
                                ),
                                (
                                    "selected !disabled",
                                    ThemeColors.update_hsv(self.theme.colors.get(color), vd=pressed_vd),
                                ),
                                ("hover !disabled", self.theme.colors.get(color)),
                            ],
                            "darkcolor": [
                                (
                                    "pressed !disabled",
                                    ThemeColors.update_hsv(self.theme.colors.get(color), vd=pressed_vd),
                                ),
                                (
                                    "selected !disabled",
                                    ThemeColors.update_hsv(self.theme.colors.get(color), vd=pressed_vd),
                                ),
                                ("hover !disabled", self.theme.colors.get(color)),
                            ],
                            "lightcolor": [
                                (
                                    "pressed !disabled",
                                    ThemeColors.update_hsv(self.theme.colors.get(color), vd=pressed_vd),
                                ),
                                (
                                    "selected !disabled",
                                    ThemeColors.update_hsv(self.theme.colors.get(color), vd=pressed_vd),
                                ),
                                ("hover !disabled", self.theme.colors.get(color)),
                            ],
                        },
                    },
                    f"chevron.{color}.TButton": {"configure": {"font": "helvetica 14"}},
                }
            )

    def _style_exit_button(self):
        """Create style configuration for the toolbutton exit button"""
        disabled_bg = (
            ThemeColors.update_hsv(self.theme.colors.inputbg, vd=-0.2)
            if self.theme.type == "light"
            else ThemeColors.update_hsv(self.theme.colors.inputbg, vd=-0.3)
        )
        pressed_vd = -0.2

        self.settings.update(
            {
                "exit.TButton": {
                    "configure": {"relief": "flat", "font": "helvetica 12"},
                    "map": {
                        "background": [
                            ("disabled", disabled_bg),
                            (
                                "pressed !disabled",
                                ThemeColors.update_hsv(self.theme.colors.primary, vd=pressed_vd),
                            ),
                            ("hover !disabled", self.theme.colors.danger),
                        ]
                    },
                }
            }
        )

        for color in self.theme.colors:
            self.settings.update(
                {
                    f"exit.{color}.TButton": {
                        "configure": {"relief": "flat", "font": "helvetica 12"},
                        "map": {
                            "background": [
                                ("disabled", disabled_bg),
                                (
                                    "pressed !disabled",
                                    ThemeColors.update_hsv(self.theme.colors.get(color), vd=pressed_vd),
                                ),
                                ("hover !disabled", self.theme.colors.danger),
                            ]
                        },
                    }
                }
            )

    def _style_meter(self):
        """Create style configuration for the ttkbootstrap.widgets.meter

        The options available in this widget include:

            - Label.border: bordercolor, lightcolor, darkcolor, relief, borderwidth
            - Label.padding: padding, relief, shiftrelief
            - Label.label: compound, space, text, font, foreground, underline, width, anchor, justify, wraplength,
                embossed, image, stipple, background
        """
        self.settings.update(
            {
                "TMeter": {
                    "layout": [
                        (
                            "Label.border",
                            {
                                "sticky": "nswe",
                                "border": "1",
                                "children": [
                                    (
                                        "Label.padding",
                                        {
                                            "sticky": "nswe",
                                            "border": "1",
                                            "children": [("Label.label", {"sticky": "nswe"})],
                                        },
                                    )
                                ],
                            },
                        )
                    ],
                    "configure": {"foreground": self.theme.colors.fg, "background": self.theme.colors.bg},
                }
            }
        )

        for color in self.theme.colors:
            self.settings.update({f"{color}.TMeter": {"configure": {"foreground": self.theme.colors.get(color)}}})

    def _style_label(self):
        """Create style configuration for ttk label: *ttk.Label*

        The options available in this widget include:

            - Label.border: bordercolor, lightcolor, darkcolor, relief, borderwidth
            - Label.padding: padding, relief, shiftrelief
            - Label.label: compound, space, text, font, foreground, underline, width, anchor, justify, wraplength,
                embossed, image, stipple, background
        """
        self.settings.update(
            {
                "TLabel": {"configure": {"foreground": self.theme.colors.fg, "background": self.theme.colors.bg}},
                "Inverse.TLabel": {
                    "configure": {"foreground": self.theme.colors.bg, "background": self.theme.colors.fg}
                },
            }
        )

        for color in self.theme.colors:
            self.settings.update(
                {
                    f"{color}.TLabel": {"configure": {"foreground": self.theme.colors.get(color)}},
                    f"{color}.Inverse.TLabel": {
                        "configure": {
                            "foreground": self.theme.colors.selectfg,
                            "background": self.theme.colors.get(color),
                        }
                    },
                    # TODO deprecate this version down the road
                    f"{color}.Invert.TLabel": {
                        "configure": {
                            "foreground": self.theme.colors.selectfg,
                            "background": self.theme.colors.get(color),
                        }
                    },
                }
            )

    def _style_labelframe(self):
        """Create style configuration for ttk labelframe: *ttk.LabelFrame*

        The options available in this widget include:

            - Labelframe.border: bordercolor, lightcolor, darkcolor, relief, borderwidth
            - Label.fill: background
            - Label.text: text, font, foreground, underline, width, anchor, justify, wraplength, embossed
        """
        self.settings.update(
            {
                "Labelframe.Label": {"element create": ("from", "clam")},
                "Label.fill": {"element create": ("from", "clam")},
                "Label.text": {"element create": ("from", "clam")},
                "TLabelframe.Label": {
                    "layout": [("Label.fill", {"sticky": "nswe", "children": [("Label.text", {"sticky": "nswe"})]})],
                    "configure": {"foreground": self.theme.colors.fg},
                },
                "TLabelframe": {
                    "layout": [("Labelframe.border", {"sticky": "nswe"})],
                    "configure": {
                        "relief": "raised",
                        "borderwidth": "1",
                        "bordercolor": (
                            self.theme.colors.border if self.theme.type == "light" else self.theme.colors.selectbg
                        ),
                        "lightcolor": self.theme.colors.bg,
                        "darkcolor": self.theme.colors.bg,
                    },
                },
            }
        )

        for color in self.theme.colors:
            self.settings.update(
                {
                    f"{color}.TLabelframe": {
                        "configure": {
                            "background": self.theme.colors.get(color),
                            "lightcolor": self.theme.colors.get(color),
                            "darkcolor": self.theme.colors.get(color),
                        }
                    },
                    f"{color}.TLabelframe.Label": {
                        "configure": {
                            "foreground": self.theme.colors.selectfg,
                            "background": self.theme.colors.get(color),
                            "lightcolor": self.theme.colors.get(color),
                            "darkcolor": self.theme.colors.get(color),
                        }
                    },
                }
            )

    @staticmethod
    def style_checkbutton(theme, background=None, font=None, foreground=None, indicatorcolor=None, style=None):
        """Create an image-based checkbutton style.

        Args:
            theme (ThemeSettings): The current theme.
            background (str, optional): The normal color of the widget background.
            font (str, optional): The font used to render the button text.
            foreground (str, optional): The text color.
            indicatorcolor (str, optional): The color of the widget indicator.
            style (str, optional): The style used to render the widget.

        Returns:
            dict: A dictionary of theme settings.
        """
        # fallback colors
        background = ThemeColors.normalize(background, theme.colors.bg, theme.colors)
        foreground = ThemeColors.normalize(foreground, theme.colors.fg, theme.colors)
        indicatorcolor = ThemeColors.normalize(indicatorcolor, theme.colors.primary, theme.colors)

        # create widget images
        element_id = uuid4()
        StylerTTK.style_checkbutton_images(theme, indicatorcolor, element_id)
        cb_off = StylerTTK.theme_images[f"{element_id}_cb_off"]
        cb_on = StylerTTK.theme_images[f"{element_id}_cb_on"]
        cb_disabled = StylerTTK.theme_images[f"{element_id}_cb_disabled"]

        # create the widget style
        settings = dict()
        settings.update(
            {
                f"{element_id}.Checkbutton.indicator": {
                    "element create": (
                        "image",
                        cb_on,
                        ("disabled", cb_disabled),
                        ("!selected", cb_off),
                        {"width": 20, "border": 4, "sticky": "w"},
                    )
                },
                style: {
                    "configure": {"background": background, "foreground": foreground, "focuscolor": ""},
                    "layout": [
                        (
                            "Checkbutton.padding",
                            {
                                "children": [
                                    (f"{element_id}.Checkbutton.indicator", {"side": "left", "sticky": ""}),
                                    (
                                        "Checkbutton.focus",
                                        {
                                            "children": [("Checkbutton.label", {"sticky": "nswe"})],
                                            "side": "left",
                                            "sticky": "",
                                        },
                                    ),
                                ],
                                "sticky": "nswe",
                            },
                        )
                    ],
                    "map": {
                        "foreground": [
                            ("disabled", theme.colors.inputfg),
                            ("active", ThemeColors.update_hsv(indicatorcolor, vd=-0.2)),
                        ]
                    },
                },
            }
        )
        return settings

    @staticmethod
    def style_checkbutton_images(theme, indicatorcolor, element_id):
        """ "Create assets for checkbutton layout

        Args:
            theme (ThemeSettings): The current theme.
            indicator_color (str): The indicator color.
            element_id (UUID): A unique element identification number.
        """
        outline = theme.colors.selectbg
        if theme.type == "light":
            fill = theme.colors.inputbg
            disabled_fg = ThemeColors.update_hsv(theme.colors.inputbg, vd=0.2)
            disabled_bg = theme.colors.inputbg
        else:
            fill = theme.colors.selectfg
            disabled_fg = ThemeColors.update_hsv(theme.colors.inputbg, vd=0.3)
            disabled_bg = disabled_fg

        # checkbutton off
        cb_off = Image.new("RGBA", (134, 134))
        draw = ImageDraw.Draw(cb_off)
        draw.rounded_rectangle([2, 2, 132, 132], radius=16, outline=outline, width=3, fill=fill)

        # checkbutton on
        with importlib.resources.open_binary("ttkbootstrap.core.files", "Symbola.ttf") as fontpath:
            font = ImageFont.truetype(fontpath, 130)
        cb_on = Image.new("RGBA", (134, 134))
        draw = ImageDraw.Draw(cb_on)
        draw.rounded_rectangle([2, 2, 132, 132], radius=16, outline=indicatorcolor, width=3, fill=indicatorcolor)
        draw.text((20, 8), "✓", font=font, fill=theme.colors.selectfg)

        # checkbutton disabled
        cb_disabled = Image.new("RGBA", (134, 134))
        draw = ImageDraw.Draw(cb_disabled)
        draw.rounded_rectangle([2, 2, 132, 132], radius=16, outline=disabled_fg, width=3, fill=disabled_bg)

        # save images
        StylerTTK.theme_images.update(
            {
                f"{element_id}_cb_off": ImageTk.PhotoImage(cb_off.resize((14, 14)), Image.LANCZOS),
                f"{element_id}_cb_on": ImageTk.PhotoImage(cb_on.resize((14, 14)), Image.LANCZOS),
                f"{element_id}_cb_disabled": ImageTk.PhotoImage(cb_disabled.resize((14, 14)), Image.LANCZOS),
            }
        )

    def _style_solid_menubutton(self):
        """Apply a solid color style to ttk menubutton: *ttk.Menubutton*

        The options available in this widget include:

            - Menubutton.border: bordercolor, lightcolor, darkcolor, relief, borderwidth
            - Menubutton.focus: focuscolor, focusthickness
            - Menubutton.indicator: arrowsize, arrowcolor, arrowpadding
            - Menubutton.padding: compound, space, text, font, foreground, underline, width, anchor, justify,
                wraplength, embossed, image, stipple, background
            - Menubutton.label:
        """
        # disabled settings
        disabled_fg = self.theme.colors.inputfg
        disabled_bg = (
            ThemeColors.update_hsv(self.theme.colors.inputbg, vd=-0.2)
            if self.theme.type == "light"
            else ThemeColors.update_hsv(self.theme.colors.inputbg, vd=-0.3)
        )

        # pressed and hover settings
        pressed_vd = -0.2
        hover_vd = -0.1

        self.settings.update(
            {
                "TMenubutton": {
                    "configure": {
                        "foreground": self.theme.colors.selectfg,
                        "background": self.theme.colors.primary,
                        "bordercolor": self.theme.colors.primary,
                        "darkcolor": self.theme.colors.primary,
                        "lightcolor": self.theme.colors.primary,
                        "arrowsize": 4,
                        "arrowcolor": self.theme.colors.bg if self.theme.type == "light" else "white",
                        "arrowpadding": (0, 0, 15, 0),
                        "relief": "raised",
                        "focusthickness": 0,
                        "focuscolor": "",
                        "padding": (10, 5),
                    },
                    "map": {
                        "arrowcolor": [("disabled", disabled_fg)],
                        "foreground": [("disabled", disabled_fg)],
                        "background": [
                            ("disabled", disabled_bg),
                            (
                                "pressed !disabled",
                                ThemeColors.update_hsv(self.theme.colors.primary, vd=pressed_vd),
                            ),
                            (
                                "hover !disabled",
                                ThemeColors.update_hsv(self.theme.colors.primary, vd=hover_vd),
                            ),
                        ],
                        "bordercolor": [
                            ("disabled", disabled_bg),
                            (
                                "pressed !disabled",
                                ThemeColors.update_hsv(self.theme.colors.primary, vd=pressed_vd),
                            ),
                            (
                                "hover !disabled",
                                ThemeColors.update_hsv(self.theme.colors.primary, vd=hover_vd),
                            ),
                        ],
                        "darkcolor": [
                            ("disabled", disabled_bg),
                            (
                                "pressed !disabled",
                                ThemeColors.update_hsv(self.theme.colors.primary, vd=pressed_vd),
                            ),
                            (
                                "hover !disabled",
                                ThemeColors.update_hsv(self.theme.colors.primary, vd=hover_vd),
                            ),
                        ],
                        "lightcolor": [
                            ("disabled", disabled_bg),
                            (
                                "pressed !disabled",
                                ThemeColors.update_hsv(self.theme.colors.primary, vd=pressed_vd),
                            ),
                            (
                                "hover !disabled",
                                ThemeColors.update_hsv(self.theme.colors.primary, vd=hover_vd),
                            ),
                        ],
                    },
                }
            }
        )

        for color in self.theme.colors:
            self.settings.update(
                {
                    f"{color}.TMenubutton": {
                        "configure": {
                            "foreground": self.theme.colors.selectfg,
                            "background": self.theme.colors.get(color),
                            "bordercolor": self.theme.colors.get(color),
                            "darkcolor": self.theme.colors.get(color),
                            "lightcolor": self.theme.colors.get(color),
                            "arrowsize": 4,
                            "arrowcolor": self.theme.colors.bg if self.theme.type == "light" else "white",
                            "arrowpadding": (0, 0, 15, 0),
                            "relief": "raised",
                            "focusthickness": 0,
                            "focuscolor": "",
                            "padding": (10, 5),
                        },
                        "map": {
                            "arrowcolor": [("disabled", disabled_fg)],
                            "foreground": [("disabled", disabled_fg)],
                            "background": [
                                ("disabled", disabled_bg),
                                (
                                    "pressed !disabled",
                                    ThemeColors.update_hsv(self.theme.colors.get(color), vd=pressed_vd),
                                ),
                                (
                                    "hover !disabled",
                                    ThemeColors.update_hsv(self.theme.colors.get(color), vd=hover_vd),
                                ),
                            ],
                            "bordercolor": [
                                ("disabled", disabled_bg),
                                (
                                    "pressed !disabled",
                                    ThemeColors.update_hsv(self.theme.colors.get(color), vd=pressed_vd),
                                ),
                                (
                                    "hover !disabled",
                                    ThemeColors.update_hsv(self.theme.colors.get(color), vd=hover_vd),
                                ),
                            ],
                            "darkcolor": [
                                ("disabled", disabled_bg),
                                (
                                    "pressed !disabled",
                                    ThemeColors.update_hsv(self.theme.colors.get(color), vd=pressed_vd),
                                ),
                                (
                                    "hover !disabled",
                                    ThemeColors.update_hsv(self.theme.colors.get(color), vd=hover_vd),
                                ),
                            ],
                            "lightcolor": [
                                ("disabled", disabled_bg),
                                (
                                    "pressed !disabled",
                                    ThemeColors.update_hsv(self.theme.colors.get(color), vd=pressed_vd),
                                ),
                                (
                                    "hover !disabled",
                                    ThemeColors.update_hsv(self.theme.colors.get(color), vd=hover_vd),
                                ),
                            ],
                        },
                    }
                }
            )

    def _style_outline_menubutton(self):
        """Apply and outline style to ttk menubutton: *ttk.Menubutton*

        The options available in this widget include:

            - Menubutton.border: bordercolor, lightcolor, darkcolor, relief, borderwidth
            - Menubutton.focus: focuscolor, focusthickness
            - Menubutton.indicator: arrowsize, arrowcolor, arrowpadding
            - Menubutton.padding: compound, space, text, font, foreground, underline, width, anchor, justify,
                wraplength, embossed, image, stipple, background
            - Menubutton.label:
        """
        # disabled settings
        disabled_fg = (
            ThemeColors.update_hsv(self.theme.colors.inputbg, vd=-0.2)
            if self.theme.type == "light"
            else ThemeColors.update_hsv(self.theme.colors.inputbg, vd=-0.3)
        )

        # pressed and hover settings
        pressed_vd = -0.2
        hover_vd = -0.1

        self.settings.update(
            {
                "Outline.TMenubutton": {
                    "configure": {
                        "font": self.theme.font,
                        "foreground": self.theme.colors.primary,
                        "background": self.theme.colors.bg,
                        "bordercolor": self.theme.colors.primary,
                        "darkcolor": self.theme.colors.bg,
                        "lightcolor": self.theme.colors.bg,
                        "arrowcolor": self.theme.colors.primary,
                        "arrowpadding": (0, 0, 15, 0),
                        "relief": "raised",
                        "focusthickness": 0,
                        "focuscolor": "",
                        "padding": (10, 5),
                    },
                    "map": {
                        "foreground": [
                            ("disabled", disabled_fg),
                            ("pressed !disabled", self.theme.colors.selectfg),
                            ("hover !disabled", self.theme.colors.selectfg),
                        ],
                        "background": [
                            (
                                "pressed !disabled",
                                ThemeColors.update_hsv(self.theme.colors.primary, vd=pressed_vd),
                            ),
                            (
                                "hover !disabled",
                                ThemeColors.update_hsv(self.theme.colors.primary, vd=hover_vd),
                            ),
                        ],
                        "bordercolor": [
                            ("disabled", disabled_fg),
                            (
                                "pressed !disabled",
                                ThemeColors.update_hsv(self.theme.colors.primary, vd=pressed_vd),
                            ),
                            (
                                "hover !disabled",
                                ThemeColors.update_hsv(self.theme.colors.primary, vd=hover_vd),
                            ),
                        ],
                        "darkcolor": [
                            (
                                "pressed !disabled",
                                ThemeColors.update_hsv(self.theme.colors.primary, vd=pressed_vd),
                            ),
                            (
                                "hover !disabled",
                                ThemeColors.update_hsv(self.theme.colors.primary, vd=hover_vd),
                            ),
                        ],
                        "lightcolor": [
                            (
                                "pressed !disabled",
                                ThemeColors.update_hsv(self.theme.colors.primary, vd=pressed_vd),
                            ),
                            (
                                "hover !disabled",
                                ThemeColors.update_hsv(self.theme.colors.primary, vd=hover_vd),
                            ),
                        ],
                        "arrowcolor": [
                            ("disabled", disabled_fg),
                            ("pressed !disabled", self.theme.colors.selectfg),
                            ("hover !disabled", self.theme.colors.selectfg),
                        ],
                    },
                }
            }
        )

        for color in self.theme.colors:
            self.settings.update(
                {
                    f"{color}.Outline.TMenubutton": {
                        "configure": {
                            "foreground": self.theme.colors.get(color),
                            "background": self.theme.colors.bg,
                            "bordercolor": self.theme.colors.get(color),
                            "darkcolor": self.theme.colors.bg,
                            "lightcolor": self.theme.colors.bg,
                            "arrowcolor": self.theme.colors.get(color),
                            "arrowpadding": (0, 0, 15, 0),
                            "relief": "raised",
                            "focusthickness": 0,
                            "focuscolor": "",
                            "padding": (10, 5),
                        },
                        "map": {
                            "foreground": [
                                ("disabled", disabled_fg),
                                ("pressed !disabled", self.theme.colors.selectfg),
                                ("hover !disabled", self.theme.colors.selectfg),
                            ],
                            "background": [
                                (
                                    "pressed !disabled",
                                    ThemeColors.update_hsv(self.theme.colors.get(color), vd=pressed_vd),
                                ),
                                (
                                    "hover !disabled",
                                    ThemeColors.update_hsv(self.theme.colors.get(color), vd=hover_vd),
                                ),
                            ],
                            "bordercolor": [
                                ("disabled", disabled_fg),
                                (
                                    "pressed !disabled",
                                    ThemeColors.update_hsv(self.theme.colors.get(color), vd=pressed_vd),
                                ),
                                (
                                    "hover !disabled",
                                    ThemeColors.update_hsv(self.theme.colors.get(color), vd=hover_vd),
                                ),
                            ],
                            "darkcolor": [
                                (
                                    "pressed !disabled",
                                    ThemeColors.update_hsv(self.theme.colors.get(color), vd=pressed_vd),
                                ),
                                (
                                    "hover !disabled",
                                    ThemeColors.update_hsv(self.theme.colors.get(color), vd=hover_vd),
                                ),
                            ],
                            "lightcolor": [
                                (
                                    "pressed !disabled",
                                    ThemeColors.update_hsv(self.theme.colors.get(color), vd=pressed_vd),
                                ),
                                (
                                    "hover !disabled",
                                    ThemeColors.update_hsv(self.theme.colors.get(color), vd=hover_vd),
                                ),
                            ],
                            "arrowcolor": [
                                ("disabled", disabled_fg),
                                ("pressed !disabled", self.theme.colors.selectfg),
                                ("hover !disabled", self.theme.colors.selectfg),
                            ],
                        },
                    }
                }
            )

    def _style_notebook(self):
        """Create style configuration for ttk notebook: *ttk.Notebook*

        The options available in this widget include:

            - Notebook.client: background, bordercolor, lightcolor, darkcolor
            - Notebook.tab: background, bordercolor, lightcolor, darkcolor
            - Notebook.padding: padding, relief, shiftrelief
            - Notebook.focus: focuscolor, focusthickness
            - Notebook.label: compound, space, text, font, foreground, underline, width, anchor, justify, wraplength,
                embossed, image, stipple, background
        """
        border_color = self.theme.colors.border if self.theme.type == "light" else self.theme.colors.selectbg
        fg_color = self.theme.colors.inputfg if self.theme.type == "light" else self.theme.colors.inputbg
        bg_color = self.theme.colors.inputbg if self.theme.type == "light" else border_color

        self.settings.update(
            {
                "TNotebook": {
                    "configure": {
                        "bordercolor": border_color,
                        "lightcolor": self.theme.colors.bg,
                        "darkcolor": self.theme.colors.bg,
                        "borderwidth": 1,
                    }
                },
                "TNotebook.Tab": {
                    "configure": {
                        "bordercolor": border_color,
                        "lightcolor": self.theme.colors.bg,
                        "foreground": self.theme.colors.fg,
                        "padding": (10, 5),
                    },
                    "map": {
                        "background": [("!selected", bg_color)],
                        "lightcolor": [("!selected", bg_color)],
                        "darkcolor": [("!selected", bg_color)],
                        "bordercolor": [("!selected", border_color)],
                        "foreground": [("!selected", fg_color)],
                    },
                },
            }
        )

    def _style_panedwindow(self):
        """Create style configuration for ttk paned window: *ttk.PanedWindow*

        The options available in this widget include:

            Paned Window:

                - Panedwindow.background: background

            Sash:

                - Sash.hsash: sashthickness
                - Sash.hgrip: lightcolor, bordercolor, gripcount
                - Sash.vsash: sashthickness
                - Sash.vgrip: lightcolor, bordercolor, gripcount
        """
        self.settings.update(
            {
                "TPanedwindow": {"configure": {"background": self.theme.colors.bg}},
                "Sash": {
                    "configure": {
                        "bordercolor": self.theme.colors.bg,
                        "lightcolor": self.theme.colors.bg,
                        "sashthickness": 8,
                        "sashpad": 0,
                        "gripcount": 0,
                    }
                },
            }
        )

    @staticmethod
    def style_sizegrip(theme, background=None, foreground=None, style="TSizegrip"):
        """Create an image-based ``Sizegrip`` style.

        Args:
            theme (str): The theme name.
            background (str, optional): The color of the sizegrip background.
            foreground (str, optional): The color of the grip.
            style (str, optional): The style used to render the widget.

        Returns:
            dict: A dictionary of theme settings.
        """
        background = ThemeColors.normalize(background, theme.colors.bg, theme.colors)
        if theme.type == "light":
            foreground = ThemeColors.normalize(foreground, theme.colors.border, theme.colors)
        else:
            foreground = ThemeColors.normalize(foreground, theme.colors.inputbg, theme.colors)

        settings = dict()
        element_id = uuid4()
        StylerTTK.theme_images.update({element_id: StylerTTK.style_sizegrip_images(foreground)})
        sizegrip_image = StylerTTK.theme_images[element_id]

        settings.update(
            {
                f"{style}": {
                    "configure": {"background": background},
                    "layout": [(f"{element_id}.Sizegrip.sizegrip", {"side": "bottom", "sticky": "se"})],
                },
                f"{element_id}.Sizegrip.sizegrip": {"element create": ("image", sizegrip_image)},
            }
        )
        return settings

    def style_sizegrip_images(color):
        """Create assets for sizegrip layout
        Args:
            color (str): The grip color.
        Returns:
            PhotoImage: The tkinter photoimage used for the sizegrip layout.
        """
        im = Image.new("RGBA", (14, 14))
        draw = ImageDraw.Draw(im)
        # top row
        draw.rectangle((9, 3, 10, 4), fill=color)
        # middle row
        draw.rectangle((6, 6, 7, 7), fill=color)  # middle row
        draw.rectangle((9, 6, 10, 7), fill=color)
        # bottom row
        draw.rectangle((3, 9, 4, 10), fill=color)  # bottom row
        draw.rectangle((6, 9, 7, 10), fill=color)
        draw.rectangle((9, 9, 10, 10), fill=color)
        return ImageTk.PhotoImage(im)
