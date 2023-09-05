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

    @function_status(name = "interrupt me", catch_interruption = True)
    def long_function():
        time.sleep(10)
        print("text")

    long_function()

    @function_status(name = "Print & SystemExit")
    def print_and_raise_error_function():
        print("This function is printing this text and then raise the systemexit error")
        raise SystemExit

    print_and_raise_error_function()

