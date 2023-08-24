import io
import inspect
import time
import traceback
import shutil
import sys

from typing import Optional, Literal


class Colorize:

    '''
    Donno how it works in other shells, so be careful about it. I dont dive a fuck.
    Actually it is a shorted version of my another module, but I want to make this script
    as independent, as possible
    '''

    RESET_COLOR = "\033[0m"

    COLORS = {
    "black": "\033[30m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    }

    STYLES = {
        "bold": "\033[1m",
    }

    END_STYLES = {
        "bold": "\033[22m",
    }

    def __init__(self,
                 text: str,
                 color: Optional[str] = None,
                 bold: Optional[bool] = False,
                 ) -> NoReturn:

        self._color = color
        self._text = text
        self._bold = bold

    def __str__(self) -> str:

        style_code = []
        style_end = []

        if self._bold:
            style_code.append(self.STYLES["bold"])
            style_end.append(self.END_STYLES["bold"])

        if self._color:
            style_code.append(self.COLORS.get(self._color, ""))
            style_end.append(self.RESET_COLOR)

        return ''.join(style_code) + self._text + ''.join(reversed(style_end))

    def __add__(self, adding_str: str) -> str:
        return self.__str__() + adding_str

    def __len__(self) -> int:
        return len(self._text)

class PrintingStyle:

    STYLES = Literal["box", "line"]

    STATUS = Literal["EXIT", "SECCESS", "ABORTED", "ERROR"]


    def __init__(self, name: str, width: int, function_status: STATUS = "SECCESS", style: STYLES = "line"):

        self.name = name

        self.width = width

        self.boxed_space = width - 6

        self.style = style

        self.splited_lines = [] #cache

        elif function_status == "EXIT":
            self.ending = Colorize(text = function_status, color = "red", bold = True)

        elif function_status == "ERROR":
            self.ending = Colorize(text = function_status, color = "red")

        elif function_status == "SUCCESS":
            self.ending = Colorize(text = function_status, color = "green")

        elif function_status == "ABORTED":
            self.ending = Colorize(text = function_status, color = "green")

    def line(self):

        # 2 spaces around line + 2 spaces around dots + 2 spaces in brackets + 2 brackets = 8

        short_string = Colorize(text = "It's too tight, sempai", color = "red")

        if dot_count_processing >= 15:
            yield short_string
            yield short_string

        else:
            dot_count_processing = self.width - len(self.name) - len("PROCESSED") - 8
            process = "\r " + self.name + " " + (dot_count_processing * ".") + " [ " + "PROCESSED" + " ]"
            ready = "\r " + self.name + " " + (dot_count_processing * ".") + " [ " + self.ending + " ]"

            yield process
            yield ready

    def box(self, text):

        top = "\r ┌" + self.name + "─" * (self.width - len(self.name) - 4) + "┐ "
        bottom= "\r └" + "─" * (self.width - len(self.ending) - 4) + self.ending + "┘ "

        yield top_part

        while True:
            text = (yield)

            yield self._boxed_text(text) if text else break

        yield bottom

    def _boxed_text(self, text):

        lines = text.splitlines()
        boxed_lines = []

        for line in lines:

            if len(line) <= self.boxed_space:
                self._border_wrapper(line)

            else:
                self.splited_lines.clear()
                self._split_line(line)

        return "\n".join(boxed_lines)

    def _split_line(self, line):

        cuted_text, left_text = line[:self.boxed_space], line[self.boxed_space:]

        if len(cuted_text) <= self.boxed_space:
            self._border_wrapper(cuted_text)

        elif len(left_text) > self.boxed_space:
            self._border_wrapper(cuted_text)
            self._split_line(left_text)

        else:
            self._border_wrapper(left_text)

        return splited_lines

    def _border_wrapper(self, text):
        splited_lines.append(f" │ {text.ljust(self.boxed_space)} │ ")

    def __str__(self, text = None):

        if text:
            if self.style == "line":
                g = next(self.box)
            else 

            return next(self.)
            return self.boxed_text(text)

        else:
            return self.box() if self.style = "box" else self.line()

def function_status(name: Optional[str] = None,
                    width: Optional[int] = None,
                    catch_interruption: Optional[bool] = False,
                    catch_exceptions: Optional[bool] = False):

    """
    A decorator to enhance the visibility and presentation of function execution in the terminal.

    Parameters:
    - name (str, optional): The custom name to display in the terminal for the function.
                            If not provided, the actual name of the function will be used.

    - width (int, optional): Specifies the maximum width for the status line in the terminal.
                                 Helps in formatting the output for terminals of varying widths.

    - catch_interruption (bool, optional): If set to True, the decorator will catch KeyboardInterrupt,
                                           skip current function and proceed to a next one.
                                           Default is False, which means, the KeyboardInterrupt will be re-raised.

    - catch_exceptions (bool, optional): Determines if exceptions raised within the decorated function
                                         should be re-raised after being caught and processed by the decorator.
                                         Default is False, which means exceptions will be re-raised.
                                         (if False, an error message will be displayed)

    Behavior:
    - On function invocation, a status line is printed to the terminal indicating the start of the function.

    - Captures and displays any printed output from the function.

    - On successful completion of the function, updates the status to 'Success'.

    - If the function encounters a KeyboardInterrupt, updates the status to 'ABORTED'

    - If `catch_interruption` is True catch KeyboardInterrupt and skip the current function, else reraise

    - If the function encounters any other Exceptions, updates the status line to 'ERROR'

    - If `catch_exception` is True prints the error traceback, else reraise

    Note:
    The decorator captures the sys.stdout stream. Any modifications or changes to sys.stdout inside the
    decorated function might interfere with the decorator's logic and can result in unexpected behavior.
    Users are advised not to alter sys.stdout when using this decorator.

    Returns:
    The return value of the decorated function without any changes.
    """


    def first_layer(func):

        def second_layer(*args, **kwargs):

            # Catching text output stream
            old_stdout = sys.stdout
            new_stdout = io.StringIO()
            sys.stdout = new_stdout

            _catch_iterruption = catch_interruption
            _catch_exceptions = catch_exceptions

            _width = width if width else shutil.get_terminal_size().columns

            _name = name if name else func.__name__

            status = Styles(name = _name, _width, function_status = "PROCESSED")

            print(status.line, end = "\r", file = old_stdout)

            try:

                result = func(*args, **kwargs)
                endpoint = {"text" : "SUCCESS", "color" : "green"}
                line = status_line(ending = {"text" : "SUCCESS", "color" : "green"})
                print(line, file = old_stdout)

                if new_stdout.getvalue():
                    print(file = old_stdout)
                    print(new_stdout.getvalue(), end = "", file = old_stdout)
                    print(file = old_stdout)

                return result

            except SystemExit:
                line = status_line(ending = {"text" : "EXIT", "color" : "red"})
                print(line, file = old_stdout)
                if new_stdout.getvalue():
                    print(file = old_stdout)
                    print(new_stdout.getvalue(), end = "", file = old_stdout)
                    print(file = old_stdout)
                raise

            except KeyboardInterrupt:

                line = status_line(ending = {"text" : "ABORTED", "color" : "yellow"})
                print(line, file = old_stdout)

                if new_stdout.getvalue():
                    print(file = old_stdout)
                    print(new_stdout.getvalue(), end = "", file = old_stdout)
                    print(file = old_stdout)

                if not _catch_iterruption:
                    print(file = old_stdout)
                    raise

            except Exception as e:

                line = status_line(ending = {"text" : "ERROR", "color" : "red"})
                print(line, file = old_stdout)

                if new_stdout.getvalue():
                    print(file = old_stdout)
                    print(new_stdout.getvalue(), end = "", file = old_stdout)
                    print(file = old_stdout)

                if not _catch_exceptions:
                    print(file = old_stdout)
                    raise e

                else:
                    if not new_stdout.getvalue():
                        print(file = old_stdout)
                    traceback.print_exc()
                    print(file = old_stdout)

            finally:

                # restoring text output stream
                sys.stdout = old_stdout
                new_stdout.close()

        return second_layer

    return first_layer






if __name__ == "__main__":

    # 1. Basic test
    @function_status(name="Basic Test")
    def basic_function():
        print("Inside basic function.")
        return "Success!"

    print(basic_function(), end= "\n\n")

    # 2. Function that raises an exception, caught within a try-except block
    @function_status(name="Exception Test", catch_exceptions=False)
    def exception_function():
        print("Raising an exception...")
        raise ValueError("Sample error!")

    try:
        exception_function()
    except ValueError:
        print("Caught ValueError in exception_function!\n")

    # 3. Function simulating a KeyboardInterrupt, caught within a try-except block
    @function_status(name="Interrupt Test", catch_interruption=True, catch_exceptions=False)
    def interrupt_function():
        print("Simulating a keyboard interrupt...")
        raise KeyboardInterrupt

    try:
        interrupt_function()
    except KeyboardInterrupt:
        print("Caught KeyboardInterrupt in interrupt_function!")

    # 4. Function printing output and then raising an exception, caught within a try-except block
    @function_status(name="Print & Exception Test", catch_exceptions=False)
    def print_and_exception_function():
        print("This function will print this line and then raise an exception.")
        raise RuntimeError("An unexpected runtime error occurred!")

    try:
        print_and_exception_function()
    except RuntimeError:
        print("Caught RuntimeError in print_and_exception_function!\n")

    # 5.Calling the decorator without args
    @function_status()
    def function_with_no_aruments_in_decorator():
        time.sleep(0.5)

    function_with_no_aruments_in_decorator()

    # 6. Testing custom width of the status line
    @function_status(name = "With custom width", max_width = 70)
    def check_custom_width():
        time.sleep(1)

    check_custom_width()

