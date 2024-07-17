#!/usr/bin/env python3

import re
from typing import Callable
from tldextract import extract
from enum import Enum
import pyperclip


class ExtractTarget(Enum):
    URL = 1
    PATH = 2
    YT_URLS = 3


url_start_token_patterns = [
    '(http|https)\:\/\/',
    'www\.'
]

# Use of negative lookahead -> bad performance for "large" texts (-> modify if required)
# Alternative (match until whitespace, .etc "\S+" then remove the substring after the termination tokens after matching )
url_termination_patterns = [
    '\)',
    '\ ',
    '\]',
    '\\n',
    '\\Z'
]
stop_match_pattern = '|'.join(url_termination_patterns)
greedy_match_until = f"\S+?(?={stop_match_pattern})"

url_match_pattern_groups = list(
    map(lambda url_start_pattern: f"({url_start_pattern}{greedy_match_until})", url_start_token_patterns))

full_url_match_regex_string = '(' + "|".join(url_match_pattern_groups) + ')'

# print(full_url_match_regex_string)
url_match_regex = re.compile(full_url_match_regex_string)

# Does work for ./path/part/part/file.txt /abspatg/something/something , but not for paths in the form of somepath/test/test/ (as having slashes and characters is not unique in this case)
path_match_regex = re.compile(
    '((^[ ]*\.\/[\w+\/]+[\.\w]+)|(^[ ]*\/[\w+\/]+[\.\w]+))')


def extract_regex_results(regEx, text):
    extracted_entries = []
    for match in re.findall(regEx, text):
        print(match)
        if (match != None):
            extracted_entries.append(match[0])

    return extracted_entries


def detect_extract_urls(text):
    return extract_regex_results(url_match_regex, text)


def detect_extract_paths(text):
    return extract_regex_results(path_match_regex, text)


def parse_urls(urls):
    return list(map(lambda url: extract(url), urls))


def get_host_name(url):
    parsed_host_parts = extract(url)
    if (parsed_host_parts != None):
        return parsed_host_parts.domain
    return None


def has_url_hostname(url, host_name):
    extracted_host_name = get_host_name(url)

    return (extracted_host_name.strip() == host_name.strip())


def has_host_names(url, host_names):
    url_host_name = get_host_name(url)

    host_name_matches = list(
        map(lambda host_name: url_host_name is host_name, host_names))

    return any(host_name_matches)


def filter_urls_by_host_name(urls, host_names):
    urls_with_host_name = list(
        filter(lambda url: has_host_names(url, host_names), urls))

    return urls_with_host_name


def extract_urls_with_host_names(text, host_names):
    extracted_urls = detect_extract_urls(text)
    return filter_urls_by_host_name(extracted_urls, host_names)


def extract_urls_by_host_name(text, host_name):
    return extract_urls_with_host_names([host_name])


def extract_youtube_urls(text):
    return extract_urls_with_host_names(['youtube', 'youtu'])


text_extraction_functions_dict: dict[ExtractTarget, Callable[[str], list[str]]] = {
    ExtractTarget.URL: detect_extract_urls,
    ExtractTarget.PATH: detect_extract_paths,
    ExtractTarget.YT_URLS: extract_youtube_urls,
}


def detect_extract(text, to_extract: ExtractTarget):
    if to_extract in text_extraction_functions_dict:
        return text_extraction_functions_dict[to_extract](text)

    raise Exception(f"Extraction mode {str(to_extract)} is not registered on 'text_extraction_functions_dict'")


def detect_extract_clipboard(to_extract: ExtractTarget):
    clipboard_text = pyperclip.paste()
    if (not clipboard_text or len(clipboard_text) <= 0):
        return None

    return detect_extract(clipboard_text, to_extract)


def detect_extract_urls_clipboard():
    return detect_extract_clipboard(ExtractTarget.URL)


def test_extraction():

    expected = [
        'https://stackoverflow.com/questions/1181271/regex-space-termination',
        'www.google.com',
        'https://stackoverflow.com/questions/1181271/regex-newline-termination',
        'https://stackoverflow.com/questions/1181271/regex-bracket-termination1',
        'https://stackoverflow.com/questions/1181271/regex-left',
        'https://stackoverflow.com/questions/1181271/regex-right',
        'http://some.com/hello#anther?test&safff',
        'www.some.com/hello#anther?test&safff'
    ]

    test_text = f"""
        Something irrelevant
    sagopsndg   sogposdgopm
        {expected[0] + " "}
        {expected[1]}
    sdighisge
        {expected[2]}
        {expected[3]})-something clipped
        {expected[4]}
        Loprem Ipsum something otherthing

        [As Markdown]({expected[5]}) (As Markdown)({expected[6]}){expected[7]}
    """

    urls = detect_extract_urls(test_text)

    print('expected:')
    print(str(expected))
    print('got:')
    print(str(urls))

    if (str(expected) == str(urls)):
        print("Extraction test was a SUCCESS")
        return

    print("\nExtraction test failed")


# test_extraction()
