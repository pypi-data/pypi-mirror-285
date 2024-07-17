import datetime
import os
import pathlib
import shutil
from typing import Any, Callable


def time_transient(to_wrap_fn: Callable) -> Callable:
    def wrapper_fn(path: str, *args):
        current_times = snap_times(path)
        res = to_wrap_fn(path, *args)
        restore_times(path, current_times)
        return res

    return wrapper_fn


def call_time_transient(to_wrap_fn: Callable, path: str, *args) -> Any:
    return time_transient(to_wrap_fn)(path, *args)


# Prevents double calling os.stat
def time_transient_stat(path: str) -> os.stat_result:
    original_stat = os.stat(path)
    restore_times(path, [original_stat.st_atime, original_stat.st_mtime])
    return original_stat


def timestamp_to_human_readable(fs_node_time: float) -> str:
    fs_node_datetime: datetime = datetime.datetime.fromtimestamp(fs_node_time)
    return fs_node_datetime.strftime('D_%d-%m-%Y__T_%H-%M')


def get_stat_attr(fs_node_path: str, attr_name: str) -> Any:
    fs_stat: os.stat_result = time_transient_stat(fs_node_path)
    return getattr(fs_stat, attr_name)


def get_formated_fs_time(path: str, attr_name: str) -> str:
    return timestamp_to_human_readable(get_stat_attr(path, attr_name))


"""def call_time_transient(to_wrap_fn: Callable, path: str, *args) -> Any:
    current_times = snap_times(path)
    res = to_wrap_fn(path, *args)
    restore_times(path, current_times)
    return res
"""


def snap_times(path: str) -> list[float]:
    original_stat = os.stat(path)
    original_atime = original_stat.st_atime
    original_mtime = original_stat.st_mtime

    return [original_atime, original_mtime]


def restore_times(path: str, times: list[float]):
    os.utime(path, (times[0], times[1]))


def time_transient_copy2(src: str, dst: str, *, follow_symlinks: bool = True):

    current_times = snap_times(src)

    copy_res = shutil.copy2(src, dst, follow_symlinks=follow_symlinks)

    restore_times(src, current_times)
    restore_times(dst, current_times)

    return copy_res


def is_excluded_glob(path: str, exclude_globs: list[str]):

    for glob in exclude_globs:
        if (pathlib.PurePath(path).match(glob)):
            return True

    return False
