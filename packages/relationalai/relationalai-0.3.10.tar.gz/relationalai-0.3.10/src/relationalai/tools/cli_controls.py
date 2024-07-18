#pyright: reportPrivateImportUsage=false
from __future__ import annotations
import io
import os
from re import Pattern
from typing import Sequence, cast, Any, List
from pathlib import Path
from InquirerPy.base.complex import FakeDocument
from prompt_toolkit.key_binding import KeyPressEvent
from prompt_toolkit.validation import ValidationError
import rich
from rich.console import Console
import sys
from InquirerPy import inquirer, utils as inquirer_utils
from InquirerPy.base.control import Choice
import time
import threading
import itertools
from ..debugging import jupyter

#--------------------------------------------------
# Constants
#--------------------------------------------------

REFETCH = "[REFETCH LIST]"
MANUAL_ENTRY = "[MANUAL ENTRY]"

#--------------------------------------------------
# Style
#--------------------------------------------------

STYLE = inquirer_utils.get_style({
    "fuzzy_prompt": "#e5c07b"
}, False)

#--------------------------------------------------
# Helpers
#--------------------------------------------------

def rich_str(string:str, style:str|None = None) -> str:
    output = io.StringIO()
    console = Console(file=output, force_terminal=True)
    console.print(string, style=style)
    return output.getvalue()

def nat_path(path: Path, base: Path):
    resolved_path = path.resolve()
    resolved_base = base.resolve()
    if resolved_base in resolved_path.parents or resolved_path == resolved_base:
        return resolved_path.relative_to(resolved_base)
    else:
        return resolved_path.absolute()

def get_default(value:str|None, list_of_values:Sequence[str]):
    if value is None:
        return None
    list_of_values_lower = [v.lower() for v in list_of_values]
    value_lower = value.lower()
    if value_lower in list_of_values_lower:
        return value

#--------------------------------------------------
# Dividers
#--------------------------------------------------

def divider(console=None, flush=False):
    div = "\n[dim]---------------------------------------------------\n "
    if console is None:
        rich.print(div)
    else:
        console.print(div)
    if flush:
        sys.stdout.flush()

def abort():
    rich.print()
    rich.print("[yellow]Aborted")
    divider()
    sys.exit(1)

#--------------------------------------------------
# Prompts
#--------------------------------------------------

default_bindings = cast(Any, {
    "interrupt": [
        {"key": "escape"},
        {"key": "c-c"},
        {"key": "c-d"}
    ],
    "skip": [
        {"key": "c-s"}
    ]
})

def prompt(message:str, value:str|None, newline=False, validator:callable = None, invalid_message:str|None = None) -> str:
    if value:
        return value
    try:
        result:str = inquirer.text(
            message,
            validate=validator,
            invalid_message=invalid_message,
            keybindings=default_bindings,
        ).execute()
    except KeyboardInterrupt:
        abort()
        raise Exception("Unreachable")
    if newline:
        rich.print("")
    return result

def select(message:str, choices:List[str|Choice], value:str|None, newline=False, **kwargs) -> str|Any:
    if value:
        return value
    try:
        result:str = inquirer.select(message, choices, keybindings=default_bindings, **kwargs).execute()
    except KeyboardInterrupt:
        abort()
        raise Exception("Unreachable")
    if newline:
        rich.print("")
    return result

def fuzzy(message:str, choices:List[str], default:str|None = None, multiselect=False, show_index=False, **kwargs) -> str:
    for i, choice in enumerate(choices):
        if isinstance(choice, str):
            choices[i] = {"name": f"{i+1} {choice}" if show_index else choice, "value": choice}

    values = [choice["value"] for choice in choices]

    try:
        kwargs["keybindings"] = default_bindings
        if multiselect:
            kwargs["keybindings"] = {
                "toggle": [
                    {"key": "tab"},   # toggle choices
                ],
                "toggle-down": [
                    {"key": "tab", "filter":False},
                ],
            }.update(default_bindings)
            kwargs["multiselect"] = True

        scroll_to_ix = None
        # @FIXME: Future improvement to make it optionally case insensitive
        if default and default in values:
            scroll_to_ix = values.index(default)
            default = None

        prompt = inquirer.fuzzy(message, choices=choices, default=default or "", max_height=8, border=True, style=STYLE, **kwargs)
        if scroll_to_ix is not None:
            prompt.content_control.selected_choice_index = scroll_to_ix
        return prompt.execute()
    except KeyboardInterrupt:
        return abort()

def fuzzy_with_refetch(prompt: str, type: str, fn: callable = None, *args, **kwargs):
    exception = None
    auto_select = kwargs.get("auto_select", None)
    not_found_message = kwargs.get("not_found_message", None)
    manual_entry = kwargs.get("manual_entry", None)
    with Spinner(f"Fetching {type}", f"Fetched {type}"):
        try:
            items = fn(*args)
        except Exception as e:
            exception = e
    if exception is not None:
        rich.print(f"\n[red]Error fetching {type}: {exception}\n")
        return exception
    if len(items) == 0:
        if not_found_message:
            rich.print(f"\n[yellow]{not_found_message}\n")
        else:
            rich.print(f"\n[yellow]No valid {type} found\n")
        return None

    if auto_select and len(items) == 1 and items[0].lower() == auto_select.lower():
        return auto_select

    if manual_entry:
        items.insert(0, MANUAL_ENTRY)
    items.insert(0, REFETCH)

    passed_default = kwargs.get("default", None)
    passed_mandatory = kwargs.get("mandatory", False)

    rich.print("")
    result = fuzzy(
        prompt,
        items,
        default=get_default(passed_default, items),
        mandatory=passed_mandatory
    )
    rich.print("")

    while result == REFETCH:
        result = fuzzy_with_refetch(prompt, type, fn, *args, **kwargs)
    return result

def confirm(message:str, default:bool = False) -> bool:
    try:
        return inquirer.confirm(message, default=default, keybindings=default_bindings).execute()
    except KeyboardInterrupt:
        return abort()

def text(message:str, default:str|None = None, validator:callable = None, invalid_message:str|None = None, **kwargs) -> str:
    if validator and not invalid_message:
        invalid_message = "Invalid input"
    try:
        return inquirer.text(
            message,
            default=default or "",
            keybindings=default_bindings,
            validate=validator,
            invalid_message=invalid_message,
            **kwargs
        ).execute()
    except KeyboardInterrupt:
        return abort()

def password(message:str, default:str|None = None, validator:callable = None, invalid_message:str|None = None) -> str:
    try:
        return inquirer.secret(
            message,
            default=default or "",
            keybindings=default_bindings,
            validate=validator,
            invalid_message=invalid_message
        ).execute()
    except KeyboardInterrupt:
        return abort()

def file(message: str, start_path:Path|None = None, pattern:str|Pattern|None = None, default:str|None = None, allow_freeform=False, **kwargs) -> str|None:
    try:
        return FuzzyFile(message, start_path, allow_freeform=allow_freeform, max_height=8, border=True, style=STYLE, **kwargs).execute()
    except KeyboardInterrupt:
        return abort()

class FuzzyFile(inquirer.fuzzy):
    def __init__(self, message: str, initial_path: Path|None = None, allow_freeform = False,  *args, **kwargs):
        self.initial_path = initial_path or Path()
        self.current_path = Path(self.initial_path)
        self.allow_freeform = allow_freeform

        kwargs["keybindings"] = {
            **default_bindings,
            "answer": [
                {"key": os.sep},
                {"key": "enter"},
                {"key": "tab"},
                {"key": "right"}
            ],
            **kwargs.get("keybindings", {})
        }

        super().__init__(message, *args, **kwargs, choices=self._get_choices)

    def _get_prompt_message(self) -> List[tuple[str, str]]:
        pre_answer = ("class:instruction", f" {self.instruction} " if self.instruction else " ")
        result = str(nat_path(self.current_path, self.initial_path))

        if result:
            sep = " " if self._amark else ""
            return [
                ("class:answermark", self._amark),
                ("class:answered_question", f"{sep}{self._message} "),
                ("class:answer", f"{result}{os.sep if not self.status['answered'] else ''}"),
            ]
        else:
            sep = " " if self._qmark else ""
            return [
                ("class:answermark", self._amark),
                ("class:questionmark", self._qmark),
                ("class:question", f"{sep}{self._message}"),
                pre_answer
            ]

    def _handle_enter(self, event: KeyPressEvent) -> None:
        try:
            fake_document = FakeDocument(self.result_value)
            self._validator.validate(fake_document)  # type: ignore
            cc = self.content_control
            if self._multiselect:
                self.status["answered"] = True
                if not self.selected_choices:
                    self.status["result"] = [cc.selection["name"]]
                    event.app.exit(result=[cc.selection["value"]])
                else:
                    self.status["result"] = self.result_name
                    event.app.exit(result=self.result_value)
            else:
                res_value = cc.selection["value"]
                self.current_path /= res_value
                if self.current_path.is_dir():
                    self._update_choices()
                else:
                    self.status["answered"] = True
                    self.status["result"] = cc.selection["name"]
                    event.app.exit(result=str(nat_path(self.current_path, self.initial_path)))
        except ValidationError as e:
            self._set_error(str(e))
        except IndexError:
            self.status["answered"] = True
            res = self._get_current_text() if self.allow_freeform else None
            if self._multiselect:
                res = [res] if res is not None else []
            self.status["result"] = res
            event.app.exit(result=res)

    def _get_choices(self, _ = None):
        choices = os.listdir(self.current_path)
        choices.append("..")
        return choices

    def _update_choices(self):
        raw_choices = self._get_choices()
        cc = self.content_control
        cc.selected_choice_index = 0
        cc._raw_choices = raw_choices
        cc.choices = cc._get_choices(raw_choices, None)
        cc._safety_check()
        cc._format_choices()
        self._buffer.reset()

#--------------------------------------------------
# Spinner
#--------------------------------------------------

class Spinner:
    """Shows a spinner control while a task is running.\n
    The finished_message will not be printed if there was an exception and the failed_message is provided.
    """
    busy = False
    delay = 0.1

    def __init__(self, message="", finished_message="", failed_message=None, delay=None):
        self.message = message
        self.finished_message = finished_message
        self.failed_message = failed_message
        self.spinner_generator = itertools.cycle([ "▰▱▱▱", "▰▰▱▱", "▰▰▰▱", "▰▰▰▰", "▱▰▰▰", "▱▱▰▰", "▱▱▱▰", "▱▱▱▱" ])
        if delay and float(delay):
            self.delay = delay

    def get_message(self):
        return rich_str(f"[magenta]{next(self.spinner_generator)} {self.message}").strip()

    def get_clear(self, message:str):
        return '\b'* len(message.encode('utf-8'))

    def spinner_task(self):
        while self.busy:
            message = self.get_message()
            sys.stdout.write(message)
            sys.stdout.flush()
            time.sleep(self.delay)
            sys.stdout.write(self.get_clear(message))
            # Only flush if stdout is a terminal
            if sys.stdout.isatty():
                sys.stdout.flush()

    def __enter__(self):
        self.busy = True
        if jupyter.ipython:
            message = self.get_message()
            sys.stdout.write(message)
            if sys.stdout.isatty():
                sys.stdout.flush()
        else:
            threading.Thread(target=self.spinner_task).start()

    def __exit__(self, exception, value, tb):
        self.busy = False
        if exception is not None:
            if self.failed_message is not None:
                rich.print(f"\n\n[yellow]{self.failed_message} {value}", file=sys.stderr)
                return True
            return False
        time.sleep(self.delay)
        message = self.get_message()
        sys.stdout.write(self.get_clear(message))
        if self.finished_message != "":
            final_message = f"[green]▰▰▰▰ {self.finished_message}"
            final_message += " " * (len(message) - len(final_message))
            rich.print(final_message)
        elif self.finished_message == "":
            sys.stdout.write(self.get_clear(message))
            sys.stdout.write(" "*len(message.encode('utf-8')))
            sys.stdout.write(self.get_clear(message))
            if sys.stdout.isatty():
                sys.stdout.flush()
