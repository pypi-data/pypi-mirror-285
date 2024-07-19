import os
import sys
from typing import Any, Callable, Iterable, List, TypeVar
from simple_chalk import chalk  # type: ignore
from .undefined import undefined


"""
Generic undefined data type.
"""
T = TypeVar("T")
SPECIAL_KEYS = [
    "SHELL",
    "SESSION_MANAGER",
    "QT_ACCESSIBILITY",
    "COLORTERM",
    "XDG_CONFIG_DIRS",
    "NVM_INC",
    "XDG_MENU_PREFIX",
    "TERM_PROGRAM_VERSION",
    "GNOME_DESKTOP_SESSION_ID",
    "LANGUAGE",
    "GNOME_SHELL_SESSION_MODE",
    "SSH_AUTH_SOCK",
    "WARP_USE_SSH_WRAPPER",
    "XMODIFIERS",
    "DESKTOP_SESSION",
    "SSH_AGENT_PID",
    "GTK_MODULES",
    "PWD",
    "LOGNAME",
    "XDG_SESSION_DESKTOP",
    "XDG_SESSION_TYPE",
    "GPG_AGENT_INFO",
    "XAUTHORITY",
    "GJS_DEBUG_TOPICS",
    "WINDOWPATH",
    "HOME",
    "USERNAME",
    "IM_CONFIG_PHASE",
    "LANG",
    "LS_COLORS",
    "XDG_CURRENT_DESKTOP",
    "VIRTUAL_ENV",
    "WARP_HONOR_PS1",
    "WARP_COMBINED_PROMPT_COMMAND_GRID",
    "SSH_SOCKET_DIR",
    "INVOCATION_ID",
    "MANAGERPID",
    "GJS_DEBUG_OUTPUT",
    "NVM_DIR",
    "LESSCLOSE",
    "XDG_SESSION_CLASS",
    "TERM",
    "LESSOPEN",
    "USER",
    "DISPLAY",
    "SHLVL",
    "NVM_CD_FLAGS",
    "SPARK_HOME",
    "QT_IM_MODULE",
    "XDG_RUNTIME_DIR",
    "WARP_IS_LOCAL_SHELL_SESSION",
    "JOURNAL_STREAM",
    "XDG_DATA_DIRS",
    "PATH",
    "GDMSESSION",
    "HISTFILESIZE",
    "DBUS_SESSION_BUS_ADDRESS",
    "NVM_BIN",
    "GIO_LAUNCHED_DESKTOP_FILE_PID",
    "GIO_LAUNCHED_DESKTOP_FILE",
    "OLDPWD",
    "TERM_PROGRAM",
    "_",
]

CONFIDENTIAL_KEYWORDS = [
    "password",
    "uri",
    "secret",
    "passphrase",
    "key",
    "connection_string",
]


def __caller_path():
    frame = sys._getframe()

    while frame.f_back != None:
        frame = frame.f_back

    return os.path.dirname(frame.f_code.co_filename)


def __contains(key: str, keywords: List[str]):
    key = key.lower()

    for keyword in keywords:
        if keyword in key:
            return True

    return False


def __get_value_text(
    key: str,
    value: str,
    confidential_keywords: List[str],
    value_len: int,
):
    if __contains(key, confidential_keywords):
        return chalk.dim.gray("*" * value_len), False

    do_ellipses = len(value) > value_len
    text = value[0 : value_len - 3] if do_ellipses else value

    return text, do_ellipses


def pretty_print(
    ignore_keys: Iterable[str] = SPECIAL_KEYS,
    confidential_keywords: Iterable[str] = CONFIDENTIAL_KEYWORDS,
    max_fields: int = 64,
    min_hidden_fields: int = 3,
    min_key_length: int = 16,
    min_value_length: int = 16,
    max_value_length: int = 64,
    max_field_length: int = 80,
):
    """
    Requires `simple-chalk`.
    """
    confidential_keywords = [
        *map(
            lambda keyword: keyword.lower(),
            confidential_keywords,
        )
    ]
    ignore_keys = [
        *map(
            lambda key: key.lower(),
            ignore_keys,
        )
    ]

    fields = [
        *filter(
            lambda field: field[0].lower() not in ignore_keys,
            os.environ.items(),
        )
    ]

    if not any(fields):
        return

    extra_fields_count = len(fields) - max_fields
    too_many_fields = extra_fields_count > min_hidden_fields

    if too_many_fields:
        fields = fields[0:max_fields]

    key_len = max(
        max(
            map(
                lambda field: len(field[0]),
                fields,
            )
        ),
        min_key_length,
    )
    value_len = filter(
        lambda field: not __contains(
            field[0],
            confidential_keywords,
        ),
        fields,
    )
    value_len = max(
        map(
            lambda field: len(field[1]),
            value_len,
        )
    )
    value_len = max(value_len, min_value_length)
    value_len = min(value_len, max_value_length)
    value_len = min(value_len, max_field_length - key_len)

    print(
        chalk.black.bgYellow.bold("KEY".ljust(key_len + 1)),
        chalk.black.bgWhite.bold("VALUE".ljust(value_len)),
    )

    for key, value in fields:
        dots = key_len - len(key)
        dots = "." * dots
        text, do_ellipses = __get_value_text(
            key,
            value,
            confidential_keywords,
            value_len,
        )

        print(
            chalk.yellow(key),
            " ",
            chalk.dim.gray(dots),
            " ",
            text,
            chalk.dim.gray("...") if do_ellipses else "",
            sep="",
        )

    if too_many_fields:
        print(
            chalk.dim.gray(f"and {extra_fields_count} more..."),
        )

    print()


def env(
    *keys,
    cast: Callable[[Any], T] = str,
    default: Any = undefined,
    write_to_env=False,
) -> T:
    """
    keys: The keys that will be searched.\
    Starts from the first index,\
    until it finds an existing pair.
    cast: Casts the values with the given callable.\
    By default, uses 'str'.
    default: The default value.\
    If not provided, will raise an error if not found.
    write_to_env: If `True`,\
    the default value is written in `os.environ`.\
    Does not affect any files.
    """
    for key in keys:
        if key in os.environ:
            return cast(os.environ[key])

    if default == undefined:
        text = "', '".join(keys)
        raise Exception(f"'{text}' is not in the environment!")

    if write_to_env and default != None:
        for key in keys:
            os.environ[key] = str(default)

    return default
