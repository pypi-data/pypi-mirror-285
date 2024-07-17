import json
import pathlib
import os
import zlib
# pip3 install zstd
import zstd
from typing import Literal


def write_as_json(py_var, target_path, format=False, compress=False, algorithm: Literal["zlib", "zstd"] = "zlib", level=3):
    indent = 0
    if (format):
        indent = 4

    json_string = json.dumps(py_var, indent=indent)

    string_to_write = json_string
    if (compress):

        if (algorithm == "zlib"):
            string_to_write = zlib.compress(json_string.encode(), level)
            target_path += '.zlib'
        elif (algorithm == "zstd"):
            bytes_to_write: bytes = zstd.compress(json_string.encode(), level)
            target_path += '.zstd'
            with open(target_path, 'wb+') as file:
                file.write(bytes_to_write)

            return

    # json_buffer = bytes(json_string, 'utf-8')
    with open(target_path, 'w+') as file:
        file.write(string_to_write)

    return target_path


def read_json(target_path):
    # if (not os.path.exists(target_path)):
    #    return None

    if (os.path.exists(target_path + '.zlib')):
        target_path = target_path + '.zlib'
    elif (os.path.exists(target_path + '.zstd')):
        target_path = target_path + '.zstd'
    elif (not os.path.exists(target_path)):
        return None

    with open(target_path, 'rb') as file:
        file_contents = file.read()

    path_suffix = pathlib.Path(target_path).suffix
    if (path_suffix == '.zlib'):
        file_contents = zlib.decompress(file_contents)
    elif (path_suffix == '.zstd'):
        file_contents = zstd.decompress(file_contents)

    file_string = file_contents.decode('utf-8')
    if not file_string:
        return ""
    return json.loads(file_string)
