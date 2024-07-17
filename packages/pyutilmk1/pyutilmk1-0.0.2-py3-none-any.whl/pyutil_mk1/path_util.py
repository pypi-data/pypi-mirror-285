import glob
import os
from os.path import join, isdir, exists, isabs
from pathlib import PurePath
import pathlib
from typing import Any, Callable, TypeVar

from .dict_string_util import get_string_between


def get_after_copy_target_path(source_path: str, target_dir_path: str) -> str:
    source_path_obj = PurePath(source_path)
    return join(target_dir_path, source_path_obj.name)


def is_ancestor_of(ancestor_path: str, current_path: str):
    # return ancestor_path in current_path

    if (ancestor_path == current_path):
        return False

    if (not current_path or not ancestor_path):
        return False

    return str(current_path).startswith(ancestor_path)


def is_any_ancestor_of(ancestor_paths: list[str], current_path: str):

    ancestor_matches: list[bool] = list(map(lambda ancestor_path: is_ancestor_of(ancestor_path, current_path), ancestor_paths))

    return any(ancestor_matches)


def is_descendant_of(ancestor_path: str, path: str) -> bool:
    ancestor_path_obj = PurePath(os.path.abspath(ancestor_path))
    to_check_path_obj = PurePath(os.path.abspath(path))

    if (ancestor_path_obj == to_check_path_obj):
        return False

    return to_check_path_obj.is_relative_to(ancestor_path_obj)


def is_protected(fs_node_to_check: str, allowed_ancestor_whitelist: list[str], min_path_length: int = 6):

    if (len(fs_node_to_check) <= min_path_length):
        return True

    is_descendant_of_whitelist_results = [is_descendant_of(white_list_path, fs_node_to_check) for white_list_path in allowed_ancestor_whitelist]
    return not any(is_descendant_of_whitelist_results)


def is_ancestor_blacklisted(fs_node_to_check: str, blocked_ancestor_list: list[str], min_path_length: int = 6):

    if (len(fs_node_to_check) <= min_path_length):
        return True

    is_descendant_of_blocked = [is_descendant_of(white_list_path, fs_node_to_check) for white_list_path in blocked_ancestor_list]
    return any(is_descendant_of_blocked)


def get_dir_entry_sort_key(dir_entry: os.DirEntry | str, files_first: bool = True):

    if (isinstance(dir_entry, str)):
        dir_entry = pathlib.Path(dir_entry)

    is_dir_flag: bool = dir_entry.is_dir()

    if (files_first):
        return str(is_dir_flag) + dir_entry.name.lower()

    is_file_flag: bool = dir_entry.is_file()
    return str(is_file_flag) + dir_entry.name.lower()

# Sort directories by length and files by name


def get_sort_key_top_dirs_first(path: str) -> float:

    lower_name = os.path.basename(path).lower()
    if (exists(path) and isdir(path)):
        path_components = '/'.split(path)

        return (len(path_components), lower_name)

    return lower_name


def get_dir_entry_sort_key_files_first(dir_entry: os.DirEntry):
    return get_dir_entry_sort_key(dir_entry, True)


def get_dir_entry_sort_key_dirs_first(dir_entry: os.DirEntry):
    return get_dir_entry_sort_key(dir_entry, False)


# Fs agnostic way of sorting dirs before files and alphabetical withing those bins
# -> However not deterministic, as files rarely also have no suffix /bin/* or dirs rarely have a suffix
def get_path_sort_key_apparent_dirs_or_files_first(path: str, suffixed_first: bool = False):

    path_obj: PurePath = PurePath(path)

    current_node_name: str = path_obj.name.lower()

    if (path_obj.suffix):
        return str(int(not suffixed_first)) + current_node_name

    return str(int(suffixed_first)) + current_node_name


def get_sort_key_apparent_dirs_first(path: str):
    return get_path_sort_key_apparent_dirs_or_files_first(path, suffixed_first=False)


def get_dir_entry_sort_key_apparent_dirs_first(dir_entry: os.DirEntry):
    return get_path_sort_key_apparent_dirs_or_files_first(dir_entry, suffixed_first=False)


CallReturnType = TypeVar('CallReturnType')


def glob_apply_fn(path_to_expand: str, fn_to_call: Callable[[str, Any], CallReturnType], *args: list[Any]) -> list[CallReturnType]:

    collected_call_fn_results: list[Any] = []
    for source_path in glob.iglob(path_to_expand):
        collected_call_fn_result = fn_to_call(source_path, *args)
        collected_call_fn_results.append(collected_call_fn_result)
    return collected_call_fn_results


def clean_path_self_refs(path: str):

    if (not path):
        return path

    path_parts = path.split('/')

    resolved_path_parts: list[str] = []
    for path_part in path_parts:
        if (path_part != '.'):
            resolved_path_parts.append(path_part)

    return "/".join(resolved_path_parts)


def resolve_path(root_path: str, relative_path: str):
    root_path_parts: list[str] = root_path.split('/')
    relative_path_parts: list[str] = relative_path.split('/')

    for path_part in relative_path_parts:
        if path_part == '.':
            pass
        elif path_part == '..':
            if root_path_parts:
                root_path_parts.pop()
        else:
            root_path_parts.append(path_part)

    resolved_path = '/'.join(root_path_parts)
    return resolved_path


def split_path_filter_empty(path: str) -> list[str]:
    path_parts = path.split('/')
    return list(filter(bool, path_parts))


def get_path_between(path: str, ancestor_path: str, end_path_part: str):
    path_between: str = get_string_between(path, ancestor_path + '/', '/' + end_path_part)
    return path_between


def append_rooted_rel_to_target_dir(target_dir_path: str, src_path: str, src_root: str):

    if (not src_root or not target_dir_path or not src_root):
        return target_dir_path

    node_path_obj = PurePath(src_path)
    target_append_dir = get_string_between(src_path, src_root, node_path_obj.name)
    target_dir_path = join(target_dir_path, target_append_dir)
    return target_dir_path


"""before_and_after_src_root = node_path.split(backup_args.source_root)

# Take anything after the 'source_root' and before the last part (file/dir to be copied) and append it to the target dir
if (len(before_and_after_src_root) > 1):
    after_root_src = before_and_after_src_root[1]
    after_root_src_parts = after_root_src.split('/')

    if (len(after_root_src_parts) > 1):
        after_src_root_no_last = after_root_src_parts[0: len(after_root_src_parts) - 1]
        target_append_dir = '/'.join(after_src_root_no_last)
        target_dir_path = target_dir_path + target_append_dir
"""


def get_rel_path(path: str, ref_root_dir: str) -> str:

    if (isabs(path)):
        return os.path.relpath(path, ref_root_dir)
    return path


def get_rel_and_abs_path(path: str, reference_root_dir: str) -> tuple[str, str]:
    if (not reference_root_dir):
        raise Exception(f"Reference root dir '{reference_root_dir}' needs to be defined for getting a relative path from '{path}'")

    rel_path_to_ref = get_rel_path(path, reference_root_dir)

    if (rel_path_to_ref == '.'):
        rel_path_to_ref = ""

    abs_path = join(reference_root_dir, rel_path_to_ref)
    return rel_path_to_ref, abs_path


def add_name_suffix_path(path, suffix, new_extension=None):
    path_obj = PurePath(path)

    extension = path_obj.suffix
    if (new_extension):
        extension = new_extension

    return join(path_obj.parent, path_obj.stem + suffix + extension)
