from __future__ import annotations

import ast
import copy
import io
import logging
import os
import sys
import traceback
from typing import Any, Callable, Tuple, cast

import line_profiler

from morph.task.utils.timer import TimeoutException

"""Tricks to restrict the usage of certain built-in functions"""


# Define the restricted version of the os module as before
class RestrictedOS:
    def __init__(self, os_module):
        self._os = os_module

    def __getattr__(self, name):
        if name in ["system", "popen"] or name.startswith("spawn"):
            raise AttributeError(f"Usage of os.{name} is restricted")
        return getattr(self._os, name)


restricted_os = RestrictedOS(os)

# Custom __import__ function that restricts certain modules
original_import = __builtins__["__import__"]  # type: ignore
# - 現状systemcall, ソースコード閲覧, ファイル操作を禁止している
# - その他検討したいモジュール
#   - pip, conda, パッケージ管理ツール
#   - ネットワーク通信
prohibited_modules = ["sys", "subprocess", "shutil", "importlib", "inspect"]


def custom_import(name, globals=None, locals=None, fromlist=(), level=0):
    if name == "os":
        return restricted_os

    if name in prohibited_modules:
        raise ImportError(f"The import of '{name}' is restricted")
    return original_import(name, globals, locals, fromlist, level)


def banned_function(function_name: str) -> Callable[..., Any]:
    """Raise an AttributeError when a banned function is called"""

    def banned_function_call(*args, **kwargs):
        raise AttributeError(f"Usage of {function_name} is restricted")

    return banned_function_call


""" Utility functions for code execution """


def _indent_code(code: str, indent: str = "    ") -> str:
    return indent + code.replace("\n", f"\n{indent}")


def package_user_code(
    user_code: str,
    setup_code: str | None = None,
    result_variable_name: str = "USER_CODE_RESULT",
    profile: bool = False,
) -> str:
    user_code_ast = ast.parse(user_code)
    main_function_defs = [
        node
        for node in user_code_ast.body
        if isinstance(node, ast.FunctionDef) and node.name == "main"
    ]
    if len(main_function_defs) == 0:
        raise ValueError("Code should declare a function named 'main'")
    elif len(main_function_defs) == 1:
        func = main_function_defs[0]
        # Extract the function name and arguments from the user code
        # Example. if function is like `def my_function(a, b, c):`
        # then `arguments` will be `a, b, c`

        # Also note that these variable should be defined before on setup code
        # with the same name as the function arguments
        arguments = ", ".join(arg.arg for arg in func.args.args)
        code = f"""def run_user_code():
{_indent_code(setup_code) if setup_code else "    # No setup code"}
{_indent_code(user_code)}
{_indent_code(f"return {func.name}({arguments})")}"""
        if not profile:
            code += f"\n{result_variable_name} = run_user_code()"

        return code
    else:
        raise ValueError(
            f"Code should declare only one function named 'main', but found {len(main_function_defs)}"
        )


def execute_user_code(
    user_code: str,
    setup_code: str | None = None,
    profile: bool = False,
    logger: logging.Logger = logging.getLogger(),
) -> Tuple[Any, dict | None, line_profiler.LineProfiler | None, str]:
    packaged_code = package_user_code(user_code, setup_code, profile=profile)
    # logger.info(f"[MORPH_INTERNAL_LOG] execute code: {packaged_code}")
    # Prepare an empty dictionary to capture local variables after exec
    local_vars: dict[str, Any] = {}
    profiler: line_profiler.LineProfiler | None = None
    # Compile the code to be executed
    compiled_code = compile(packaged_code, "<string>", "exec")
    # Prepare a namespace for the code execution
    original_environ = copy.deepcopy(os.environ)
    os.environ.clear()
    ns: dict[str, Any] = {
        "__builtins__": dict(__builtins__, __import__=custom_import),
        # Explicitly ban some built-in functions
        "exec": banned_function("exec"),
        "eval": banned_function("eval"),
        "open": banned_function("open"),
        "compile": banned_function("compile"),
        "builtins": banned_function("builtins"),
        "globals": banned_function("globals"),
        "locals": banned_function("locals"),
    }

    # Execute the code
    try:
        # replace stdout to capture user code output
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()

        if profile:
            exec(compiled_code, ns)  # Executing the packaged code

            # Get the 'run_user_code' function from the namespace
            user_func = ns["run_user_code"]

            profiler = line_profiler.LineProfiler()
            profiled_func = profiler(user_func)
            result = profiled_func()
        else:
            exec(packaged_code, ns, local_vars)
            result = local_vars.get("USER_CODE_RESULT", None)

        error = None
    except TimeoutException:
        raise
    except Exception:
        # 例外が発生した場合、スタックトレースを取得
        exc_type, exc_value, exc_traceback = sys.exc_info()
        tb = traceback.extract_tb(exc_traceback)
        stacks = [
            {
                "filename": frame.filename,
                "lineno": frame.lineno,
                "name": frame.name,
                "line": frame.line,
            }
            for frame in tb
        ]
        exc_type_str = "Exception" if exc_type is None else exc_type.__name__
        exc_value_str = str(exc_value)
        error = {
            "error": {
                "type": exc_type_str,
                "message": exc_value_str,
            },
            "code": user_code,
            "stacktrace": tb.format(),
            "structuredStacktrace": stacks,
        }
        result = None
    finally:
        # capture stdout output and log it
        captured_output = cast(io.StringIO, sys.stdout).getvalue()
        for line in captured_output.splitlines():
            logger.debug(line)

        # recover stdout
        sys.stdout = old_stdout

        # Restore the original environment variables after execution
        os.environ.clear()
        os.environ.update(original_environ)

    return result, error, profiler, packaged_code


def format_profiling_stats(
    profiler: line_profiler.LineProfiler, source_code: str
) -> str:
    source_lines = source_code.split("\n")
    output = io.StringIO()

    output.write("Line #\tHits\t\tTime\t\tLine Content\n")
    output.write("-" * 80 + "\n")

    # Access the profiler's stats
    for (fn, lineno, name), timings in profiler.get_stats().timings.items():
        # Iterate over the timings for this function
        for timing in timings:
            line, hits, time_spent = timing

            # Ensure the line number is within bounds
            if 0 <= line - 1 < len(source_lines):
                line_content = source_lines[line - 1].rstrip()  # Get the line content
            else:
                line_content = "<line out of range>"

            # Format the time spent for better readability
            formatted_time = f"{time_spent / 1000000:.6f} ms"  # Assuming time_spent is in microseconds

            output.write(f"{line}\t{hits}\t\t{formatted_time}\t{line_content}\n")

    return output.getvalue()
