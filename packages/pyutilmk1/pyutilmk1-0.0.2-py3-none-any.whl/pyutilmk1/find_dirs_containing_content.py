import os
from os.path import join
import re
import sys
from .find_children_dirs_containing_files import find_children_dirs_containing_files


excluded_path_parts = [
    'site-packages',
    'lib',
    'module',
    'vscode-settings',
    'public-github',
    'External',
]


def find_content_in_dir(content_search_pattern, dir, file_match_pattern):

    file_match = re.compile(file_match_pattern)

    matches_in_dir = []
    if os.path.isdir(dir):
        for (root, dirs, decendant_files) in os.walk(dir):

            for decendant_file in decendant_files:

                if (file_match.match(decendant_file)):

                    file_path = join(root, decendant_file)

                    exclude_conditions_list = [exclude_path in file_path for exclude_path in excluded_path_parts]
                    if (not any(exclude_conditions_list)):

                        # print(file_path)
                        with open(file_path) as file_stream_reader:

                            file_content = str(file_stream_reader.read())

                            for index, line in enumerate(file_content.split("\n")):

                                if (content_search_pattern in line):
                                    result = (dir, file_path, line, index)
                                    matches_in_dir.append(result)

    return matches_in_dir


def search_line_pattern_in_dirs(content_search_pattern, dir, file_match_pattern):

    matched_dirs = find_children_dirs_containing_files(dir, file_match_pattern)

    # found_results = []

    found_results_per_dir = []

    for dir_index, matched_dir in enumerate(matched_dirs):
        found_dir_lines = find_content_in_dir(content_search_pattern, matched_dir, file_match_pattern)

        if (found_dir_lines):
            print(f"\n{dir_index}) {matched_dir}: ----------------------------------------------------- ")

        for found_entry_index, (dir_match, file_of_dir, line_content, line_index) in enumerate(found_dir_lines):
            # print(f"\n{dir_index}) {dir_match} -> {file_of_dir}: ")
            print(f"\n{found_entry_index}) {file_of_dir}: ")
            print(f"{str(line_index)}: {line_content.strip()}")

        found_results_per_dir.append(found_dir_lines)

    print('\n--------------------------------------')
    dir_number_input = input("\nIf you want to open a project with code enter its number, otherwise hit enter?\n")

    if (dir_number_input and len(dir_number_input) > 0):

        dir_numbers = [dir_number_input]
        if (',' in dir_number_input):
            dir_numbers = dir_number_input.split(',')

        for dir_number in dir_numbers:

            if ('+' in dir_number):
                number_parts = dir_number.split('+')
                dir_number = int(number_parts[0])
                file_number = int(number_parts[1])

                dir_results = found_results_per_dir[dir_number]
                (dir_match, file_of_dir, line_content, line_index) = dir_results[file_number]
                os.system(f'code {matched_dirs[int(number_parts[0])]} --goto {file_of_dir}:{line_index + 1}')

            os.system(f'code {matched_dirs[int(dir_number)]}')

    # found_results


if __name__ == '__main__':

    cwd = os.getcwd()
    file_match_pattern = sys.argv[1]
    content_search_pattern = sys.argv[2]
    search_line_pattern_in_dirs(content_search_pattern, cwd, file_match_pattern)
    sys.exit()
