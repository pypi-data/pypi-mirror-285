import os
from os.path import join
import re
import sys


def is_decendant_matched_dir(dir_path: str, regex_matcher: re.Pattern):

    if os.path.isdir(dir_path):
        for (root, dirs, files) in os.walk(dir_path):

            for file in files:

                if (regex_matcher.match(file)):
                    return True

    return False


def find_children_dirs_containing_files(target_dir, file_name_match_pattern):

    child_files = os.listdir(target_dir)

    regex_matcher = re.compile(file_name_match_pattern)

    list_of_dirs = []

    for child_file in child_files:
        child_path = join(target_dir, child_file)

        if is_decendant_matched_dir(child_path, regex_matcher):
            list_of_dirs.append(child_file)

    return list_of_dirs


if __name__ == '__main__':
    cwd = os.getcwd()
    regex_pattern = sys.argv[1]
    print(sys.argv)

    list_of_dirs = find_children_dirs_containing_files(cwd, regex_pattern)
    print('\n'.join(list_of_dirs))

    sys.exit()
