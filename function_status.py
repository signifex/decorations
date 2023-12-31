import textwrap
import time
import traceback
import shutil
import sys

from threading import Thread
from io import StringIO
from typing import Optional, Literal, List, NoReturn

from decorations import Colorize

class FunctionStatus:

    """
    Represents the status of a function's execution and provides visualization tools.

    The `FunctionStatus` class offers multiple ways to visualize or track the status
    of a function's execution:

    1. **Manual Usage**: For maximum customization, you can use the class directly
    and call the methods in sequence:

       - open: To open the status. Returns the formatted string.
       - wrap: To wrap text inside the status. Returns the wrapped text as a string.
       - close: To close the status. Returns the closed status string.

    These methods return formatted strings, which can be particularly useful when
    `print_out` is set to `False`, allowing manual handling and printing of the strings.

       Example:

       fs = FunctionStatus(name="Test")
       status_open = fs.open
       wrapped_text = fs.wrap("Function started...")
       status_close = fs.close

    2. **Context Manager**: For simplicity with limited customization, you can use
       the class within a `with` statement. This ensures the correct order of operations
       (`open`, `wrap`, `close`):

       Example:

       fs = FunctionStatus(name="Test")
       with fs:
           fs.wrap("Processing...")

    3. **Decorator**: The decorator provides a way to wrap entire functions and capture
       their stdout. It uses threading to maintain responsiveness and automatically
       manages the opening, wrapping, and closing of the status:

       @function_status(name = "some function")
       def some_function():
           pass

    Attributes:

    - name: A string representing the name of the function.

    - width: An optional integer specifying the width of the status display.
      If not provided, the default width is set to the width of the terminal.

    - style: A string that can be either "line" or "box", determining the
      style of the status display.

    - status: An optional string representing the current status of the function.

    - print_out: An optional boolean indicating whether to print the status
      to the standard output. If set to `True`, the status will be printed
      automatically; if `False`, the formatted status strings can be retrieved
      and handled manually.

    """

    def __init__(self,
                 name: str,
                 width: Optional[int] = None,
                 style: Literal["line", "box"] = "line",
                 status: Optional[str] = "PROCESSING",
                 print_out: Optional[bool] = True):

        self._name = name
        self._status = status
        self._width = width if width else shutil.get_terminal_size().columns
        self._style = style
        self._print = print_out
        self._state = "not_opened" # "not_opened", "opened", "text_wrapped", "closed"

    def __enter__(self):
        if not self._print:
            raise ValueError("FunctionStatus context manager requires the 'print_out' attribute to be set to True")

        self.open

    def __exit__(self, exc_type, exc_value, exc_traceback):

        if exc_type:
            error_message = traceback.format_tb(exc_traceback, limit = 2)
            for line in error_message:
                self.wrap(line)
            self._status = "ERROR"

        elif self._status == "PROCESSING":
            self._status = "SUCCESS"

        self.close
        return True

    @property
    def open(self) -> str:

        if self._state != "not_opened":
            raise RuntimeError("Object can't be opened again without closing.")

        self._state = "opened"

        if self._style == "line":
            current_status = self._simple_line() + "\r"
        else:
            current_status = self._box_opening() + "\n" + self._box_closing() + "\r"

        if self._print:
            sys.stdout.write(current_status)

        return current_status

    def wrap(self, text):

        if self._state not in ["opened", "wrapping"]:
            raise RuntimeError("Object needs to be opened before wrapping.")

        self._state = "wrapping"

        current_status = ""

        if self._style == "line":
            self._style = "box"
            current_status += self._box_opening() + "\n"

        current_status += self._box_wrap(text) + "\n" + self._box_closing() + "\r"

        if self._print:
            sys.stdout.write(current_status)

        return current_status

    @property
    def close(self):

        if self._state not in ["opened", "wrapping"]:
            raise RuntimeError("Object can't be closed without being opened.")

        self._state = "closed"

        current_status = self._simple_line() + "\n" if self._style == "line" else self._box_closing() + "\n"

        if self._print:
            sys.stdout.write(current_status)

        return current_status


    def set_status(self, new_status: str) -> NoReturn:
        self._status = new_status


    def _simple_line(self) -> str:

        '''
        dots amaount:
        2 spaces around dots +
        2 spaces in brackets +
        brackets around status = 6
        '''
        error_line = "It's too tight, sempai"
        base_string = "\r{name} {dots} [ {status} ]"
        dots_amount = self._width - len(self._name) - len(self._status) - 6
        line = base_string.format(
            name = self._name,
            dots = "." * dots_amount,
            status = self._status)

        return line if dots_amount > 5 else error_line


    def _box_opening(self) -> str:
        base_line = "\r┌ {name} {dashes}┐"
        dashes_amount = self._width - len(self._name) - 4
        line = base_line.format(
            name = self._name,
            dashes = "─" * dashes_amount)
        return line


    def _box_closing(self) -> str:
        base_line = "\r└{dashes} [ {status} ] ┘"
        dashes_amount = self._width - len(self._status) - 8
        line = base_line.format(
            status = self._status,
            dashes = '─' * dashes_amount)
        return line


    def _box_wrap(self, text) -> str:

        boxed_lines = []
        lines = text.splitlines()
        boxed_space = self._width - 4

        for line in lines:

            if not line.strip():
                boxed_lines.append(f"│ {''.ljust(boxed_space)} │")

            else:
                wrapped_text = textwrap.fill(line, boxed_space)

                for wrapped_line in wrapped_text.splitlines():
                    boxed_lines.append(f"│ {wrapped_line.ljust(boxed_space)} │")

        return "\r" + "\n".join(boxed_lines)






def function_status(name: Optional[str] = None,
                    width: Optional[int] = None,
                    catch_interruption: Optional[bool] = False,
                    catch_exceptions: Optional[bool] = False,
                    colorize: Optional[bool] = True):

    """
    A decorator that wraps a function to provide a real-time visual status of its execution.

    This decorator captures the standard output (stdout) of the decorated function and
    displays its execution status using the `FunctionStatus` class. It visually
    represents the function's progress, providing real-time feedback to users about ongoing operations.

    Utilizing threading, the decorator ensures that the decorated function runs without interruption,
    while concurrently updating its status. This is especially beneficial for long-running functions where
    real-time feedback is crucial.

    The decorator also redirects the stdout of the function. Hence, any print statements or other outputs
    from the function will be encapsulated and displayed within the status visualization class.

    Parameters:

    - name (str, optional): Specifies the name of the function. Defaults to the decorated function's name.

    - width (int, optional): Sets the width of the status display. By default, it adjusts to the terminal's width.

    - catch_interruption (bool, optional): Determines if the decorator should catch and handle keyboard
      interruptions (KeyboardInterrupt). Defaults to False.

    - catch_exceptions (bool, optional): Determines if the decorator should catch and display general exceptions
      without halting the program. Defaults to False.

    - colorize (bool, optional): If set to True, the status messages will be colorized for better visual feedback.
      Defaults to True.

    Returns:
    - Callable: The decorated function, wrapped with real-time status visualization.

    Example:
    @function_status(name="Processing Data", width=50)
    def process_data():
        # function logic here
        ...
    """
    ...




    def first_layer(func):

        def second_layer(*args, **kwargs):

            nonlocal name, width, catch_interruption, catch_exceptions

            name = name if name else func.__name__

            main_function_processing = True
            func_result = None
            error_message = None

            def checking_thread():
                while main_function_processing:
                    check_prints()
                    time.sleep(0.1)

            def check_prints():
                text = buffer.getvalue()
                if text:
                    buffer.truncate(0)
                    buffer.seek(0)
                    wrapped_text = current_status.wrap(text)
                    original_stdout.write(wrapped_text)

            current_status = FunctionStatus(name = name, width = width, print_out = False)

            # Catching text output stream
            original_stdout = sys.stdout
            sys.stdout = buffer = StringIO()

            original_stdout.write(current_status.open)

            thread = Thread(target = checking_thread)
            thread.start()

            try:

                func_result = func(*args, **kwargs)
                new_status = Colorize(text = "SUCCESS", color = "green") if colorize else "SUCCESS"
                current_status.set_status(new_status)

            except SystemExit as e:

                new_status = Colorize(text = "EXIT", color = "red", bold = True) if colorize else "EXIT"
                current_status.set_status(new_status)

                if str(e):
                    error_message = str(e)
                raise

            except KeyboardInterrupt as e:

                new_status = Colorize(text = "ABORTED", color = "yellow") if colorize else "ABORTED"
                current_status.set_status(new_status)

                if str(e) != "KeyboardInterrupt":
                    error_message = str(e)

                if not catch_interruption:
                    raise e from e

            except Exception as e:

                new_status = Colorize(text = "ERROR", color = "red") if colorize else "ERROR"
                current_status.set_status(new_status)

                if not catch_exceptions:
                    raise e from e

                else:
                    error_message = traceback.format_exc(limit = -1)

            finally:

                main_function_processing = False
                thread.join()
                check_prints()

                if error_message:
                    error_message = current_status.wrap(error_message)
                    original_stdout.write(error_message)

                original_stdout.write(current_status.close)
                # restoring text current_status stream
                sys.stdout = original_stdout
                buffer.close()
                del(current_status)

            return func_result

        return second_layer

    return first_layer






if __name__ == "__main__":

    @function_status(name = "Basic line test")
    def line_text():
        pass

    line_text()

    @function_status()
    def no_arguments_test():
        pass

    no_arguments_test()

    @function_status(name = "Line error test")
    def error_in_line():
        1/0

    try:
        error_in_line()
    except ZeroDivisionError as e:
        pass

    @function_status(name = "Catching error test", catch_exceptions = True)
    def error_in_box():
        print("Here must be this line, empty line, traceback for zero devision error", end = "\n\n")
        1/0

    error_in_box()

    @function_status(name = "Text formatting test")
    def formatting_test():
        print("Testing multiple lines of text\n" * 3)
        print("\tTesting tab character.")
        print("Testing \tsplit tab characters.")
        print("Testing carriage return: ABC\rXYZ")
        print("Mixing\ttabs and\nnewlines.")

    formatting_test()

    @function_status(name = "Long Text Test")
    def long_text_test():
        for i in range(5):
            print(f"This is a long line of text number {i}. " * 10)
            time.sleep(0.2)

    long_text_test()

    @function_status(name = "Interrupt Test", catch_interruption = True)
    def interruption_test():
        print("Simulating a keyboard interrupt...")
        raise KeyboardInterrupt

    interruption_test()

    @function_status(name = "Custom width line test", width = 60)
    def custom_width_line():
        pass

    custom_width_line()

    @function_status(name = "Custom wifth box test", width = 60)
    def custom_width_box():
        for i in range(5):
            print(f"Intermittent print {i}")
            time.sleep(0.5)

    custom_width_box()

    @function_status(name = "INTERRUPT ME", catch_interruption = True)
    def long_function():
        time.sleep(10)
        print("text")

    long_function()

    @function_status(name = "Print & SystemExit")
    def print_and_raise_error_function():
        print("This function is printing this text and then raise the systemexit error")
        raise SystemExit

    print_and_raise_error_function()

