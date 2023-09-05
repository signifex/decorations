import textwrap
import time
import shutil
import sys

from threading import Thread

from concurrent.futures import ThreadPoolExecutor
from io import StringIO
from typing import Optional, Literal, List, NoReturn

from decorations import Colorize

class StatusGenarator:

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
            base_string = "\r└{dashes} [ {status} ] ┘\r"
            dashes_amount = self.width - len(self.status) - 8
            line = base_string.format(
                status = self.status,
                dashes = '─' * dashes_amount)
            return line

        def get_boxed_text(text) -> List[str]:

            boxed_lines = []
            lines = text.splitlines()
            boxed_space = self.width - 4

            for line in lines:

                if not line.strip():
                    boxed_lines.append(f"\r│ {''.ljust(boxed_space)} │")

                else:
                    wrapped_text = textwrap.fill(line, boxed_space)

                    for wrapped_line in wrapped_text.splitlines():
                        boxed_lines.append(f"\r│ {wrapped_line.ljust(boxed_space)} │")

            boxed_lines.append(get_closing_line())

            return "\n".join(boxed_lines)

        text = yield get_opening_line() + get_closing_line()

        while text is not None:

            text = yield get_boxed_text(text)

        yield get_closing_line() + "\n"


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
                    wrapped_text = current_status(text)
                    original_stdout.write(wrapped_text)

            current_status = StatusGenarator(name, width)

            # Catching text output stream
            original_stdout = sys.stdout
            sys.stdout = buffer = StringIO()

            original_stdout.write(current_status())

            thread = Thread(target = checking_thread)
            thread.start()

            try:

                func_result = func(*args, **kwargs)
                current_status.status = Colorize(text = "SUCCESS", color = "green") if colorize else "SUCCESS"

            except SystemExit as e:

                current_status.status = Colorize(text = "EXIT", color = "red", bold = True) if colorize else "EXIT"
                if str(e):
                    error_message = e
                raise

            except KeyboardInterrupt as e:

                current_status.status = Colorize(text = "ABORTED", color = "yellow") if colorize else "ABORTED"

                if str(e) != "KeyboardInterrupt":
                    error_message = str(e)

                if not catch_interruption:
                    raise

            except Exception as e:

                current_status.status = Colorize(text = "ERROR", color = "red") if colorize else "ERROR"

                if not catch_exceptions:
                    raise e from e

                else:
                    error_message = str(e)

            finally:

                main_function_processing = False
                thread.join()
                check_prints()

                if error_message:
                    error_message = current_status(error_message)
                    original_stdout.write(error_message)

                original_stdout.write(current_status())
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

    @function_status(name = "line error test")
    def error_in_line():
        1/0

    try:
        error_in_line()
    except ZeroDivisionError as e:
        print(e)

    @function_status(name = "catching error test", catch_exceptions = True)
    def error_in_box():
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

