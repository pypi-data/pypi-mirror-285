# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.
"""
Standard functions provided to the BLISS shell.
"""

from __future__ import annotations

import gevent
import contextlib
import prompt_toolkit
import tabulate
import shutil
import time
import typing
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import TerminalFormatter

from bliss import current_session
from bliss.common import timedisplay
from bliss.config import static
from bliss.common.utils import chunk_list

# Expose this functions from this module
from bliss.common.standard import info  # noqa: E402,F401
from bliss.shell.pt import utils as pt_utils
from bliss.shell.pt.default_style import get_style

if typing.TYPE_CHECKING:
    from bliss.shell.pt.text_block_app import TextBlock
    from prompt_toolkit import HTML, ANSI
    from prompt_toolkit.formatted_text import FormattedText


def lsconfig():
    """
    Print all objects found in config.
    Not only objects declared in current session's config.
    """
    obj_dict = dict()

    config = static.get_config()

    # Maximal length of objects names (min 5).
    display_width = shutil.get_terminal_size().columns

    print()

    for name in config.names_list:
        c = config.get_config(name).get("class")
        # print(f"{name}: {c}")
        if c is None and config.get_config(name).plugin == "emotion":
            c = "Motor"
        try:
            obj_dict[c].append(name)
        except KeyError:
            obj_dict[c] = list()
            obj_dict[c].append(name)

    # For each class
    for cc in obj_dict.keys():
        print(f"{cc}: ")
        if cc is None:
            print("----")
        else:
            print("-" * len(cc))
        obj_list = list()

        # put all objects of this class in a list
        while obj_dict[cc]:
            obj_list.append(obj_dict[cc].pop())
        # print(obj_list)

        max_length = max([len(x) for x in obj_list])

        # Number of items displayable on one line.
        item_count = int(display_width / max_length) + 1

        print(tabulate.tabulate(chunk_list(obj_list, item_count), tablefmt="plain"))
        print()


def _pyhighlight(code, bg="dark", outfile=None):
    formatter = TerminalFormatter(bg=bg)
    return highlight(code, PythonLexer(), formatter, outfile=outfile)


def _get_source_code(obj_or_name):
    """
    Return source code for an object, either by passing the object or its name in the current session env dict
    """
    import inspect

    is_arg_str = isinstance(obj_or_name, str)
    if is_arg_str:
        obj, name = current_session.env_dict[obj_or_name], obj_or_name
    else:
        obj = obj_or_name
        name = None
    try:
        real_name = obj.__name__
    except AttributeError:
        real_name = str(obj)
    if name is None:
        name = real_name

    if (
        inspect.ismodule(obj)
        or inspect.isclass(obj)
        or inspect.istraceback(obj)
        or inspect.isframe(obj)
        or inspect.iscode(obj)
    ):
        pass
    elif callable(obj):
        obj = inspect.unwrap(obj)
    else:
        try:
            obj = type(obj)
        except Exception:
            pass

    try:
        fname = inspect.getfile(obj)
    except TypeError:
        return f"Source code for {repr(obj)} is not available.", []
    lines, line_nb = inspect.getsourcelines(obj)

    if name == real_name or is_arg_str:
        header = f"'{name}' is defined in:\n{fname}:{line_nb}\n"
    else:
        header = f"'{name}' is an alias for '{real_name}' which is defined in:\n{fname}:{line_nb}\n"

    return header, lines


def prdef(obj_or_name):
    """
    Show the text of the source code for an object or the name of an object.
    """
    header, lines = _get_source_code(obj_or_name)
    print(header)
    print_ansi(_pyhighlight("".join(lines)))


def clear():
    """
    Clear terminal screen
    """
    import sys
    import os

    if sys.platform == "win32":
        os.system("cls")
    else:
        os.system("clear")


def print_html(text: str, **kwargs):
    """
    Print formatted text as HTML.

    See prompt-toolkit `print_formatted_text`.

    .. code-block:: python

        print_html("<em><red>Hi!</red></em>")
    """
    output = current_session.output
    return prompt_toolkit.print_formatted_text(
        prompt_toolkit.HTML(text), output=output, style=get_style(), **kwargs
    )


def print_ansi(text: str, **kwargs):
    """
    Print formatted text with ANSI escape sequences.

    See prompt-toolkit `print_formatted_text`.

    .. code-block:: python

        print_ansi("\033[94mHi!\033[0m")
    """
    output = current_session.output
    return prompt_toolkit.print_formatted_text(
        prompt_toolkit.ANSI(text), output=output, **kwargs
    )


def countdown(duration_s: float, message="Waiting...", end_message=None):
    """
    Wait <duration_s> seconds while printing a countdown message.
    If provided, print <end_message> once the countdown is finished.
    Ex: countdown(2, 'waiting for refill', 'Gooooo !')
    """
    if not pt_utils.can_use_text_block():
        # Make sure a sleep is anyway displayed
        gevent.sleep(duration_s)
        return

    starting_time = time.time()

    def render():
        remaining_s = int(duration_s - (time.time() - starting_time) + 1)
        return 1, f"{message} {remaining_s:4d} s"

    with text_block(render=render) as tb:
        gevent.sleep(duration_s)
        tb.set_text(f"{message} {0:4d} s")

    if end_message:
        print(end_message)


@contextlib.contextmanager
def bench():
    """
    Context manager for basic timing of procedure, this has to be use like this:
        with bench():
            <command>
    example:
        with bench():
             mot1._hw_position
    gives:
        Execution time: 2ms 119μs

    """
    start_time = time.perf_counter()
    yield
    duration = time.perf_counter() - start_time

    print(f"Execution time: {timedisplay.duration_format(duration)}")


@contextlib.contextmanager
def text_block(
    render: (
        typing.Callable[[], tuple[int, str | FormattedText | ANSI | HTML]] | None
    ) = None
) -> typing.Context[TextBlock]:
    """Provides a block of text than can be updated during a context.

    Arguments:
        render: A callback function while format the content. It is called
                times in a second.
    """
    from bliss.shell.pt.text_block_app import TextBlockApplication
    from prompt_toolkit.application import get_app_or_none

    if not pt_utils.can_use_text_block():
        from bliss.shell.pt.text_block_app import TextBlock

        # Dummy text block
        yield TextBlock(None)
        return

    g = gevent.getcurrent()
    if isinstance(g, gevent.Greenlet):
        app = g.spawn_tree_locals.get("text_block")
    else:
        g = None
        app = get_app_or_none()
        if not isinstance(app, TextBlockApplication):
            app = None

    if app is None:
        app = TextBlockApplication(render)
        app.interrupt_exception = KeyboardInterrupt
        try:
            if g is not None:
                g.spawn_tree_locals["text_block"] = app
            with app.exec_context():
                yield app.first_text_block()
        finally:
            if g is not None:
                g.spawn_tree_locals["text_block"] = None
    else:
        with app.new_text_block(render) as tb:
            yield tb
