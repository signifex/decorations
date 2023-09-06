
# Decorations Library
Elevate your Python development experience with a collection of decorators and utilities tailored for improved visibility and presentation in the terminal.

## Table of Contents
- [Installation](#installation)
- [Overview](#overview)
- [Function Status](#function-status)
- [Colorize](#colorize)
- [License](#license)
  
## Installation
To use the decorators library, clone the repository:

```bash
git clone https://github.com/signifex/decorations.git
cd decorations
echo "export PYTHONPATH=\$PYTHONPATH:$(pwd)" >> ~/.bashrc
source ~/.bashrc
```

> **Note**: The library relies solely on standard Python modules, ensuring no conflicts with other libraries.

## Overview

### Function Status
- Get a real-time visual representation of your function's execution, including captured print statements and exceptions.
- Use manually, with a context manager, or as a decorator for flexibility.

### Colorize
- Add a splash of color to your terminal outputs.
- Choose from a range of colors, backgrounds, and styles.


## Function Status 

#### Manual Usage:

```python
from decorations import FunctionStatus

status = FunctionStatus(name="My Function", print_out = False)
line = status.open
print(line, end="")
# Your function logic here
line = status.wrap("first stage")
print(line, end="")
# More logic
line = status.close
print(line, end="")
```

#### Context Manager:

```python
from decorations import FunctionStatus

status = FunctionStatus(name="My Function", print_out = True)
with status:
    # Your function logic here
    status.wrap("Processing ...")
    # More logic
```

#### Decorator:

```python
from decorations import function_status

@function_status(name="Decorated Function")
def my_function():
    # Your function logic here
    ...
```
<details>
  <summary>Animated output</summary>
    <img src="https://github.com/signifex/decorations/assets/97762325/1463251e-9543-4969-83b0-96e6a01f69e4" alt="output">
</details>

<details>
  <summary>Image output</summary>
    <img src="https://github.com/signifex/decorations/assets/97762325/e6b1ddc0-01ed-4e80-93df-fcb7bb82eab8" alt="image">
</details>


#### Parameters:
- **name**: (Optional) Custom display name for the terminal. Defaults to the function's name.
- **width**: (Optional) Maximum width for the status line/box in the terminal.
- **catch_interruption**: (Optional) Set True to handle KeyboardInterrupt gracefully, default is False.
- **catch_exceptions**: (Optional) Set True to catch exceptions other than KeyboardInterrupt and SystemExit, default is False.

<details>
  <summary>How it Works</summary>
  
#### Threaded Execution:
The decorated function runs inside a separate thread using Python's Threading. This allows for concurrent monitoring of the function's execution.
#### Capturing Standard Output:
The module captures the standard output (sys.stdout) of the decorated function. This means any print statements or standard output produced by the function is intercepted.
The captured output can then be formatted, decorated, or manipulated as desired before being displayed to the terminal.
#### Status Reporting:
During the function's execution, the decorator continually checks for any captured output.
It wraps the captured output with visual elements (e.g., boxes, lines) to enhance readability.
The status of the function (e.g., "PROCESSING", "SUCCESS", "ERROR") is displayed in a visually appealing manner.
#### Error Handling:
The decorator is designed to catch various exceptions, including SystemExit, KeyboardInterrupt, and general exceptions.
Depending on the configuration, certain exceptions can either be caught and processed or allowed to propagate.
#### Customization:
Users can customize the name and width of the status display.
Additional options allow users to specify whether interruptions (KeyboardInterrupt) or general exceptions should be caught by the decorator.

</details>


## Colorize
The Colorize class leverages ANSI escape codes to offer a variety of text colors, backgrounds, and styles. Whether you need to highlight specific outputs or make your logs more visually appealing, Colorize has got you covered.

#### Features:
- **Rich Color Palette**: Choose from a range of colors including red, green, blue, and more.
- **Background Colors**: Set vibrant backgrounds for your text.
- **Text Styles**: Go beyond colors! Make your text `bold`, `underline`, or even `blink`.
- **Easy access**: using a chain of methods, it's easier to create an object of the class. (Use the `bg_` prefix to access background colors as class method e.g., `bg_red`, `bg_blue`).
- **Quick print**: Instead of wrapping the object, just use classmethod `print`


#### Basic Usage:

```python
from decorations import Colorize

colored_text = Colorize("Hello World!", color = "red", bold = True)
print(colored_text)
```

#### Chain Styles:

```python
from decorations import Colorize

Colorize("Hello World!").yellow.bg_red.underline.print
```

> **Note:** The class is designed to be forgiving. Any unrecognized color or background specifications won't raise an error but will simply be ignored. Background colors can be accessed using the `bg_` prefix, making it slightly different from regular colors in terms of easy access.


## License
BSD 2-Clause License
