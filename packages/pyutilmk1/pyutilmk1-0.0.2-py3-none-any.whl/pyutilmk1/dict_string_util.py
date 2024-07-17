import re
import argparse
from typing import Any, Callable, TypeVar

quoted_pattern = re.compile(r'^[\'"](.+)[\'"]$')


def unquote_if_quoted(string: str) -> str:

    string = string.strip()

    match_between_quotes: re.Match[str] | None = quoted_pattern.match(string)

    if (match_between_quotes and match_between_quotes.group(1)):
        return match_between_quotes.group(1)

    return string


def clean_parse_string(to_parse: str):
    if (not to_parse):
        return ""

    to_parse = to_parse.strip()
    to_parse = unquote_if_quoted(to_parse)
    # rule_args: list[str] = shlex.split(rule_string)
    return to_parse


def get_dictval_or_default(dict_key: str, check_dict: dict, default_val: Any):
    if (dict_key in check_dict and check_dict[dict_key]):
        return check_dict[dict_key]

    return default_val


def add_fs_path_filter_args(parser: argparse.ArgumentParser, prefix="", prefix_full=""):

    full_option_prefix_string = ""
    if (prefix_full):
        full_option_prefix_string = prefix_full + "_"

    parser.add_argument(f'-{prefix}n', f'-{prefix}name', f'--{full_option_prefix_string}name', help="Same as path_filter but only applies to the name of the file/directory")
    parser.add_argument(f'-{prefix}rn', f'-{prefix}rname', f'--{full_option_prefix_string}regex_name', help="Same as path_filter but only applies to the name of the file/directory")
    parser.add_argument(f'-{prefix}p', f'-{prefix}path', f'--{full_option_prefix_string}path', help="")
    parser.add_argument(f'-{prefix}rp', f'-{prefix}rpath', f'--{full_option_prefix_string}regex_path', help="")


ListItem: TypeVar = TypeVar('ListItem')


def get_list_item_at(pos: int, list: list[ListItem], default: ListItem | None = None) -> ListItem | None:
    if (len(list) > pos):
        return list[pos]
    return default


def unpack_nested_dict_val(keys: list[str], dict: dict) -> Any | None:

    current_cursor_val = None
    for key in keys:
        current_cursor_val = dict.get(key)
        if (not current_cursor_val):
            return None

    return current_cursor_val


def pack_nested_dict_val(keys: list[str], dict: dict, new_value: Any) -> Any | None:

    current_cursor_val = None
    keys_before_last = keys[0:-1]
    last_key = keys[-1:]
    for key in keys_before_last:
        current_cursor_val = dict.get(key)
        if (not current_cursor_val):
            return None

    current_cursor_val[last_key] = new_value


def get_string_between(string: str, start_token: str, end_token: str) -> str:

    start = 0
    end = len(string)
    if (start_token in string):
        start = string.index(start_token) + len(start_token)
    if (end_token in string):
        end = string.index(end_token)

    return string[start: end]
