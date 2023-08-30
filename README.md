
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
> **Note:** The decorator intercepts sys.stdout. Any alterations to sys.stdout within the decorated function might disrupt both the function and decorator's logic.

```python
@function_status(name="Line Test")
def line_text():
    return "returned from line test."

print(line_text())

@function_status(name="Basic Test")
def basic_function():
    print("Inside basic function.")
    return "Good!"

print(basic_function())

@function_status(name="Text Formatting Test")
def formatting_function():
    print("Testing multiple lines of text\n" * 3)
    print("\tTesting tab character.")
    print("Testing \tsplit tab characters.")
    print("Testing carriage return: ABC\rXYZ")
    print("Mixing\ttabs and\nnewlines.")
    return "Done with formatting tests!"

```
![output](https://github.com/signifex/decorations/assets/97762325/1463251e-9543-4969-83b0-96e6a01f69e4)
> **Note:** Result from running the module on its own, contains a number of test functions to check the output

#### Parameters:
- **name**: (Optional) Custom display name for the terminal. Defaults to the function's name.
- **width**: (Optional) Maximum width for the status line/box in the terminal.
- **catch_interruption**: (Optional) Set True to handle KeyboardInterrupt gracefully, default is False.
- **catch_exceptions**: (Optional) Set True to catch exceptions other than KeyboardInterrupt and SystemExit, default is False.

### How it Works:
#### Threaded Execution:
The decorated function runs inside a separate thread using Python's ThreadPoolExecutor. This allows for concurrent monitoring of the function's execution.
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
