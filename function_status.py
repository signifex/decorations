import inspect
import textwrap
import traceback
import time
import shutil
import sys

from concurrent.futures import ThreadPoolExecutor
from io import StringIO
from typing import Optional, Literal, List, NoReturn


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

class StatusGenarator:

    STATUS = Literal["EXIT", "SUCCESS", "ABORTED", "ERROR"]
    STYLE = Literal["line", "box"]

    def __init__(self, name: str, width: int, colorize: bool = True, style: STYLE = "line"):

        self.name = name
        self.width = width if width else shutil.get_terminal_size().columns
        self.generator = self.line() if style == "line" else self.box()
        self.colorize = colorize
        self.status = "PROCESSING"

    def __call__(self, text = None):

        '''
        comparing self.genarator.__name__ == "line_style" raises no error,
        but according python documantation and gpt, generators has no __name__ arrt.
        so I change it to gi_code.co_name, to make sure,
        that comparing is working on any device
        '''
        try:
            # simple line
            if not text and self.generator.gi_code.co_name == "line":
                return next(self.generator)

            # close the line generator and change style to box
            elif text and self.generator.gi_code.co_name == "line":
                self.generator.close()
                self.generator = self.box()
                box_top = next(self.generator)
                box_inner = self.generator.send(text)
                return box_top + box_inner

            # process box
            else:
                return self.generator.send(text)

        except Exception as e:
            message = "error call of the status geneator class"
            print(message, e, file = sys.stderr)

    @property
    def print(self):
        return self

    @property
    def function_status(self):
        return self.status

    @function_status.setter
    def function_status(self, new_status: STATUS):
        self.status = self.colorize_status(new_status) if self.colorize else new_status

    @staticmethod
    def colorize_status(colorizing_status):

        if colorizing_status == "EXIT":
            return Colorize(text = "EXIT", color = "red", bold = True)

        elif colorizing_status == "ERROR":
            return Colorize(text = "ERROR", color = "red")

        elif colorizing_status == "SUCCESS":
            return Colorize(text = "SUCCESS", color = "green")

        elif colorizing_status == "ABORTED":
            return Colorize(text = "ABORTED", color = "yellow")


    def line(self) -> str:

        def create_line():
            '''
            dots amaount:
            2 spaces around dots +
            2 spaces in brackets +
            2 spaces around whole line +
            brackets around status = 8
            '''
            error_line = "It's too tight, sempai"
            base_string = "\r {name} {dots} [ {status} ] "
            dots_amount = self.width - len(self.name) - len(self.status) - 8
            line = base_string.format(
                name = self.name,
                dots = "." * dots_amount,
                status = self.status)

            return line if dots_amount > 5 else error_line

        yield create_line() + "\r"

        yield create_line() + "\n"

    def box(self) -> str:

        '''
        returns opening line + closing line (with processing status and carriage return),
        then boxed text + closing box (same as before) while the generator getting text
        and at the end closing line, but now the status must be changed and the line it will be without carriage return
        '''
        def get_opening_line():
            base_string = "\r┌ {name} {dashes}┐\n"
            dashes_amount = self.width - len(self.name) - 4
            line = base_string.format(
                name = self.name,
                dashes = "─" * dashes_amount)
            return line

        def get_closing_line():
            base_string = "\r└{dashes} [ {status} ] ┘"
            dashes_amount = self.width - len(self.status) - 8
            line = base_string.format(
                status = self.status,
                dashes = '─' * dashes_amount)
            line = line + "\r" if self.status == "PROCESSING" else line + "\n"

            return line

        def get_boxed_text(text) -> List[str]:

            boxed_lines = []
            lines = text.splitlines()
            boxed_space = self.width - 4

            for line in lines:

                if not line.strip():
                    boxed_lines.append(f"│ {''.ljust(boxed_space)} │")

                else:
                    wrapped_text = textwrap.fill(line, boxed_space)

                    for wrapped_line in wrapped_text.splitlines():
                        boxed_lines.append(f"│ {wrapped_line.ljust(boxed_space)} │")

            boxed_lines.append(get_closing_line())

            return "\n".join(boxed_lines)

        text = yield get_opening_line() + get_closing_line()

        while text is not None:

            text = yield get_boxed_text(text)

        yield get_closing_line()


def function_status(name: Optional[str] = None,
                    width: Optional[int] = None,
                    catch_interruption: Optional[bool] = False,
                    catch_exceptions: Optional[bool] = False,
                    colorize: Optional[bool] = True):

    def first_layer(func):

        def second_layer(*args, **kwargs):

            nonlocal name, width, catch_interruption, catch_exceptions

            name = name if name else func.__name__

            def check_prints():
                text = buffer.getvalue()
                if text:
                    buffer.truncate(0)
                    buffer.seek(0)
                    wrapped_text = current_status(text)
                    original_stdout.write(wrapped_text)

            current_status = StatusGenarator(name, width)

            # Catching text output stream
            original_stdout = sys.stdout
            sys.stdout = buffer = StringIO()

            with ThreadPoolExecutor(max_workers = 1) as executor:

                original_stdout.write(current_status())

                future = executor.submit(func, *args, **kwargs)
                while not future.done():
                    time.sleep(0.1)
                    check_prints()

            try:
                result = future.result()
                check_prints()
                current_status.function_status = "SUCCESS"
                original_stdout.write(current_status())
                return result

            except SystemExit:

                check_prints()

                current_status.function_status = "EXIT"
                original_stdout.write(current_status())

                raise

            except KeyboardInterrupt:

                check_prints()

                current_status.function_status = "ABORTED"
                original_stdout.write(current_status())

                if not catch_interruption:
                    raise

            except Exception as e:

                check_prints()

                current_status.function_status = "ERROR"

                if not catch_exceptions:
                    original_stdout.write(current_status())
                    raise e from e

                else:
                    original_stdout.write(current_status(e))
                    original_stdout.write(current_status())

            finally:

                # restoring text current_status stream
                sys.stdout = original_stdout
                buffer.close()
                del(current_status)

        return second_layer

    return first_layer






if __name__ == "__main__":

    # 1. Basic test
    @function_status(name="Line Test")
    def line_text():
        return "returned from line test."

    print(line_text())

    # 2. Basic test with inside print
    @function_status(name="Basic Test")
    def basic_function():
        print("Inside basic function.")
        return "Good!"

    print(basic_function())

    # 3. Text formatting and multiple prints
    @function_status(name="Text Formatting Test")
    def formatting_function():
        print("Testing multiple lines of text\n" * 3)
        print("\tTesting tab character.")
        print("Testing \tsplit tab characters.")
        print("Testing carriage return: ABC\rXYZ")
        print("Mixing\ttabs and\nnewlines.")
        return "Done with formatting tests!"

    print(formatting_function())

    # 4. Long text test
    @function_status(name="Long Text Test")
    def long_text_function():
        for i in range(10):
            print(f"This is a long line of text number {i}. " * 3)
            time.sleep(0.2)
        return "Long text test completed!"

    print(long_text_function())

    # 5. Function simulating a KeyboardInterrupt
    @function_status(name="Interrupt Test", catch_interruption=True, catch_exceptions=False)
    def interrupt_function():
        print("Simulating a keyboard interrupt...")
        raise KeyboardInterrupt

    try:
        interrupt_function()
    except KeyboardInterrupt:
        print("Caught KeyboardInterrupt in interrupt_function!")

    # 6. Printing special characters
    @function_status(name="Special Characters Test")
    def special_characters_function():
        special_chars = '!@#$%^&*()_+-=[]{}|;:,.<>?/`~"\'\\'
        print(f"Testing special characters: {special_chars}")
        return "Special characters test completed!"

    print(special_characters_function())

    # 7. Function that waits and prints intermittently
    @function_status(name="Intermittent Print Test", width=79)
    def intermittent_print():
        for i in range(5):
            print(f"Intermittent print {i}")
            time.sleep(0.5)

    intermittent_print()

    # 8. Testing custom width of the status line
    @function_status(name="Custom Width Test", width=60)
    def custom_width_function():
        print("Testing a custom width for the status line.")
        time.sleep(1)

    custom_width_function()

    # 9. Function printing output and then raising an error
    @function_status(name="Print & Raise Error Test")
    def print_and_raise_error_function():
        print("This function will print this line and then raise an systemexit.")
        raise SystemExit

    print_and_raise_error_function()

