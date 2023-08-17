import io
import inspect
import time
import traceback
import shutil
import sys

from typing import Optional

# another module of this library
from .colorize import Colorize


def function_status(name: Optional[str] = None, max_width: Optional[int] = None, catch_interruption: Optional[bool] = False, catch_exceptions: Optional[bool] = False):

    """
    A decorator to enhance the visibility and presentation of function execution in the terminal.

    Parameters:
    - name (str, optional): The custom name to display in the terminal for the function.
                            If not provided, the actual name of the function will be used.

    - max_width (int, optional): Specifies the maximum width for the status line in the terminal.
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

            def status_line(ending: dict):

                stage_name = name
                terminal_width = max_width

                if stage_name is None:
                    stage_name = func.__name__

                if terminal_width is None:
                    terminal_width = shutil.get_terminal_size().columns

                variable_len = len(stage_name) + len(ending["text"])

                # space before dots + space after dots + 2 spaces in brackets + 2 brackets = 6
                dot_count_processing = terminal_width - variable_len - 8

                if dot_count_processing >= 10:
                    status_string = ("\r " + stage_name + " " +
                                     (dot_count_processing * ".") +" [ " +
                                     str(Colorize(text = ending["text"], color = ending["color"])) + " ]")

                else:
                    status_string = str(Colorize(text = "It's too tight, sempai", color = "red"))

                return status_string


            _catch_iterruption = catch_interruption
            _catch_exceptions = catch_exceptions

            # Catching text output stream
            old_stdout = sys.stdout
            new_stdout = io.StringIO()
            sys.stdout = new_stdout

            line = status_line(ending = {"text" : "PROCESSING", "color" : "white"})

            print(line, end = "\r", file = old_stdout)

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

