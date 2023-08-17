
# Decorations Library
Elevate your Python development experience with a collection of decorators and utilities tailored for improved visibility and presentation in the terminal.

## Installation
To use the decorators library, clone the repository:

```bash
git clone https://github.com/signifex/decorations.git
cd decorations
echo "export PYTHONPATH=\$PYTHONPATH:$(pwd)" >> ~/.bashrc
source ~/.bashrc
```
Then, you can import and utilize the modules in your Python scripts.

> **Note:** only standard python modules are used, so for the time being, adding to pip is not planned, and conflict with other libraries is impossible

## Features

### Function Status Decorator
Monitor the real-time execution of your functions in the terminal, including captured print statements and exception tracebacks.

### Colorize Class
Beautify your terminal outputs with a plethora of color options.

## Usage

### Function Status Decorator
Decorate your functions to receive feedback:

```python
from decorators import function_status
import time

@function_status(name="Simple Function")
def simple_function():
    print("Inside of a simple function.")
    time.sleep(0.5)

@function_status(name="Function with Exception", catch_exceptions=True)
def function_with_exception():
    time.sleep(0.5)
    raise ValueError("Custom message error!")

@function_status(name= "Interrupted function", catch_interruption=True)
def long_running_function():
    time.sleep(5)
    raise KeyboardInterrupt

@function_status(name= "Exit function")
def exit_function():
    exit()
```
![record](https://github.com/signifex/decorations/assets/97762325/d046da18-04a0-4e2e-8097-736ffa0d1af1)

#### Parameters:
- **name**: (Optional) Custom display name for the terminal. Defaults to the function's name.
- **max_width**: (Optional) Maximum width for the status line in the terminal.
- **catch_interruption**: (Optional) Set True to handle KeyboardInterrupt gracefully, default is False.
- **catch_exceptions**: (Optional) Set True to catch exceptions other than KeyboardInterrupt, default is False.

> **Note:** The decorator intercepts sys.stdout. Any alterations to sys.stdout within the decorated function might disrupt both the function and decorator's logic.

### Colorize Class
Elevate your terminal outputs with vibrant colors and styles using the Colorize class.

#### Overview:
The Colorize class leverages ANSI escape codes to offer a variety of text colors, backgrounds, and styles. Whether you need to highlight specific outputs or make your logs more visually appealing, Colorize has got you covered.

#### Features:
- **Rich Color Palette**: Choose from a range of colors including red, green, blue, and more.
- **Background Colors**: Set vibrant backgrounds for your text.
- **Text Styles**: Go beyond colors! Make your text `bold`, `underline`, or even `blink`.
- **Easy access**: using a chain of methods, it's easier to create an object of the class. (Use the `bg_` prefix to access background colors as class method e.g., `bg_red`, `bg_blue`).
- **Quick print**: Instead of wrapping the object, just use classmethod `print`

#### Usage:
The Colorize class offers flexibility in applying styles:

```python
# Initialization Styles, great readability but awkward writing:
colored_text = Colorize("Hello", color="red", background="blue", bold=True)

# Chained Styles: using class methods for faster writing:
Colorize("Hello").red.bg_blue.bold

# And the final print method to awoid wrapping in a standard function
Colorize("Hello").yellow.bg_red.underline.print

# Extract Raw Text: Retrieve the original text without any styles.
colored_text.raw
```

> **Note:** The class is designed to be forgiving. Any unrecognized color or background specifications won't raise an error but will simply be ignored. Background colors can be accessed using the `bg_` prefix, making it slightly different from regular colors in terms of easy access.
