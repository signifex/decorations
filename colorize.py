from typing import Optional, NoReturn

class Colorize:

    """
    A class to colorize and style text for terminal output using ANSI escape codes.

    Parameters:
    - text (str): The actual text content to be formatted.
    - color (str): Text color. If not recognized, it won't have an effect. Default is None.
    - background (str): Text background color. If not recognized, it won't have an effect. Default is None.
    - bold (bool): Whether the text should be bold. Default is False.
    - underline (bool): Whether the text should be underlined. Default is False.
    - blink (bool): Whether the text should blink. Default is False.

    Usage:
    The Colorize class can be used in two primary ways:
    1. By specifying styles during instantiation:
       `colored_text = Colorize("Hello", color="red", bold=True)`
    2. By chaining style methods after instantiation:
       `colored_text = Colorize("Hello").red.bold`
    3. To print the colored text directly without wrapping into `print()`, simply add `.print` at the end:
       `Colorize("Hello").print`
    4. You can also store the `Colorize` object and chain additional methods to it later:
       `colored_text = Colorize("Hello").red`
       `colored_text.bold.print`
    5. To take the text back, use method `.raw`
       `colored_text.raw`

    Note:
    Any unrecognized color or background specification won't raise an error but won't affect the text either.

    """

    RESET_COLOR = "\033[0m"

    COLORS = {
    "white": "\033[37m",
    "gray": "\033[90m",
    "black": "\033[30m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "bright_white": "\033[97m",
    "bright_red": "\033[91m",
    "bright_green": "\033[92m",
    "bright_yellow": "\033[93m",
    "bright_blue": "\033[94m",
    "bright_magenta": "\033[95m",
    "bright_cyan": "\033[96m",
    }

    BACKGROUNDS = {
    "white": "\033[47m",
    "medium_gray": "\033[100m",
    "black": "\033[40m",
    "red": "\033[41m",
    "green": "\033[42m",
    "yellow": "\033[43m",
    "blue": "\033[44m",
    "magenta": "\033[45m",
    "cyan": "\033[46m",
    "bright_white": "\033[107m",
    "bright_red": "\033[101m",
    "bright_green": "\033[102m",
    "bright_yellow": "\033[103m",
    "bright_blue": "\033[104m",
    "bright_magenta": "\033[105m",
    "bright_cyan": "\033[106m",
    }

    STYLES = {
        "bold": "\033[1m",
        "underline": "\033[4m",
        "blink": "\033[5m",
    }

    END_STYLES = {
        "bold": "\033[22m",
        "underline": "\033[24m",
        "blink": "\033[25m"
    }

    def __init__(self,
                 text: str,
                 color: Optional[str] = None,
                 background: Optional[str] = None,
                 bold: Optional[bool] = False,
                 underline: Optional[bool] = False,
                 blink: Optional[bool] = False,
                 ) -> NoReturn:

        self._color = color
        self._background = background
        self._text = text
        self._bold = bold
        self._underline = underline
        self._blink = blink


    def __str__(self) -> str:

        style_code = []
        style_end = []

        if self._bold:
            style_code.append(self.STYLES["bold"])
            style_end.append(self.END_STYLES["bold"])

        if self._underline:
            style_code.append(self.STYLES["underline"])
            style_end.append(self.END_STYLES["underline"])

        if self._blink:
            style_code.append(self.STYLES["blink"])
            style_end.append(self.END_STYLES["blink"])

        if self._background:
            style_code.append(self.BACKGROUNDS.get(self._background, ""))
            style_end.append(self.RESET_COLOR)

        if self._color:
            style_code.append(self.COLORS.get(self._color, ""))
            style_end.append(self.RESET_COLOR)

        return ''.join(style_code) + self._text + ''.join(reversed(style_end))

    def __repr__(self):

        default_repr = super().__repr__()

        attributes = f"\ncolor: {self._color}, background: {self._background}, bold: {self._bold}, underline: {self._underline}, blink: {self._blink}\n"

        text = f"text: {self._text}\n"

        hint = ("Hint: use method Colorize(<text>).<color>.print to print the text")
        return default_repr + attributes + text + hint

    @property
    def raw(self):
        return self._text

    @property
    def bold(self):
        self._bold = True
        return self

    @property
    def underline(self):
        self._underline = True
        return self

    @property
    def blink(self):
        self._blink = True
        return self

    @property
    def print(self):
        print(self.__str__())

    # dinamicly create class attributes from colors.
    # now you able to use it like "Colorize("text").color.bg_color"
    # pretty cool, yeah?

    for color in COLORS:
        exec(f"""
@property
def {color}(self):
    self._color = "{color}"
    return self
        """)

    for color in BACKGROUNDS:
        exec(f"""
@property
def bg_{color}(self):
    self._background = "{color}"
    return self
        """)


if __name__ == "__main__":
    i = 0
    for color in Colorize.COLORS:
        for bg_color in Colorize.BACKGROUNDS:
            bold = (i % 3 == 0)
            underline = (i % 2  == 0)
            i += 1
            print(Colorize("example", background = bg_color, color = color, bold = bold, underline = underline), end = "")
        print("")



