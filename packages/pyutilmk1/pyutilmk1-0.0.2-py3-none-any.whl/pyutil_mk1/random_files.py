import os
from os.path import join
import random
import string

__letters = string.ascii_lowercase


def generate_random_ascii_char():
    random_char = random.choice(__letters)
    # print(random_char)
    return random_char


def random_ascii_string(length_chars: int):
    random_letters_list: list[str] = [generate_random_ascii_char() for i in range(0, length_chars)]
    return ''.join(random_letters_list)


def generate_random_file(file_path: str, letters_cnt: int):
    content = random_ascii_string(letters_cnt)

    with open(file_path, 'w+') as file:
        file.write(content)

    return file_path


def generate_dir_with_random_files(dir_to_create_path: str, files_cnt: int, file_prefix='file', letters_cnt_min_rand: tuple[int, int] = (300, 4000), file_suffix: str = '.txt'):
    os.makedirs(dir_to_create_path, exist_ok=True)

    letters_cnt_min, letters_cnt_length = letters_cnt_min_rand

    random_file_paths = []
    for i in range(0, files_cnt):

        letters_cnt = int(letters_cnt_min + random.random() * letters_cnt_length)
        file_path = join(dir_to_create_path, f'{file_prefix}_{i}{file_suffix}')

        random_file_paths.append(generate_random_file(file_path, letters_cnt))

    return random_file_paths


def generate_dir_with_random_files_in_dir(target_name, target_dir, subfiles_cnt: int, file_prefix='file'):
    to_create_dir_path = join(target_dir, target_name)
    random_file_paths = generate_dir_with_random_files(to_create_dir_path, subfiles_cnt, file_prefix)
    return to_create_dir_path, random_file_paths
