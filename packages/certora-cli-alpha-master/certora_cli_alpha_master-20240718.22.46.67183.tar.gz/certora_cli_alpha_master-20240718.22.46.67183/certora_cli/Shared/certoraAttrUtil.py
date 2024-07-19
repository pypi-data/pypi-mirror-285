import sys
import argparse
from typing import Any, NoReturn, Dict, Optional, Callable
from Shared import certoraUtils as Util
from enum import auto
from dataclasses import dataclass, field
from rich.console import Console
from rich.table import Table
from rich.text import Text

APPEND = 'append'
STORE_TRUE = 'store_true'
VERSION = 'version'
SINGLE_OR_NONE_OCCURRENCES = '?'
MULTIPLE_OCCURRENCES = '*'
ONE_OR_MORE_OCCURRENCES = '+'


def default_validation(x: Any) -> Any:
    return x


class UniqueStore(argparse.Action):
    """
    This class makes the argparser throw an error for a given flag if it was inserted more than once
    """

    def __call__(self, parser: argparse.ArgumentParser, namespace: argparse.Namespace, values: Any,  # type: ignore
                 option_string: str) -> None:
        if getattr(namespace, self.dest, self.default) is not self.default:
            parser.error(f"{option_string} appears several times.")
        setattr(namespace, self.dest, values)


class NotAllowed(argparse.Action):
    """
    This class makes the argparser throw an error for a given flag if it was set in CLI (can be set using conf file)
    """

    def __call__(self, parser: argparse.ArgumentParser, namespace: argparse.Namespace, values: Any,  # type: ignore
                 option_string: str) -> None:

        parser.error(f"{option_string} cannot be set in command line only in a conf file.")


class CertoraArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def error(self, message: str) -> NoReturn:
        prefix = 'unrecognized arguments: '
        is_single_dash_flag = False

        if message.startswith(prefix):
            flag = message[len(prefix):].split()[0]
            if len(flag) > 1 and flag[0] == '-' and flag[1] != '-':
                is_single_dash_flag = True
        self.print_help(sys.stderr)
        if is_single_dash_flag:
            Console().print(f"{Util.NEW_LINE}[bold red]Please remember, CLI flags should be preceded with "
                            f"double dashes!{Util.NEW_LINE}")
        raise Util.CertoraUserInputError(message)


class AttrArgType(Util.NoValEnum):
    STRING = auto()
    BOOLEAN = auto()
    LIST = auto()
    INT = auto()
    MAP = auto()


class BaseAttribute(Util.NoValEnum):
    def get_flag(self) -> str:
        return self.value.flag if self.value.flag is not None else '--' + str(self)

    @classmethod
    def print_attr_help(cls) -> None:

        type_col_header = "Type"
        type_col_width = len(type_col_header)
        desc_col_width = 37
        """
        At the time of writing this, the default_desc column width is 25 and is the minimum because the default value
        of --orig_run_dir in certoraMutate is `.certora_mutate_sources`
        """
        default_col_width = Util.HELP_TABLE_WIDTH - Util.MAX_FLAG_LENGTH - type_col_width - desc_col_width

        table = Table(padding=(0, 0), show_lines=True, header_style="bold")
        table.add_column(Text("Flag"), no_wrap=True, width=Util.MAX_FLAG_LENGTH)
        table.add_column(Text(type_col_header), width=type_col_width)
        table.add_column(Text("Description"), width=desc_col_width)
        table.add_column(Text("Default"), width=default_col_width)

        for attr in cls:
            if attr.value.help_msg != Util.SUPPRESS_HELP_MSG and attr.get_flag().startswith('--') \
               and not attr.value.deprecation_msg:
                default = attr.value.default_desc if attr.value.default_desc else ""
                type_str = str(attr.value.arg_type).upper()[0]  # We show boolean as B etc
                flag_name = Text(attr.get_flag(), style="bold")
                table.add_row(flag_name, type_str, attr.value.help_msg, default)
        console = Console()
        console.print(table)


@dataclass
class BaseArgument:
    affects_build_cache_key: bool  # a context argument that should be hashed as part of cache key computation
    disables_build_cache: bool  # if set to true, setting this option means cache will be disabled no matter what

    flag: Optional[str] = None  # override the 'default': option name
    attr_validation_func: Callable = default_validation
    help_msg: str = argparse.SUPPRESS
    # args for argparse's add_attribute passed as is
    argparse_args: Dict[str, Any] = field(default_factory=dict)
    arg_type: AttrArgType = AttrArgType.STRING
    deprecation_msg: Optional[str] = None
    default_desc: Optional[str] = None  # A description of the default behavior
