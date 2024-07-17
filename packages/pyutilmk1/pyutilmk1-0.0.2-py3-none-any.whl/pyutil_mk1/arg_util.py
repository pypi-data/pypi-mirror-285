import argparse
import logging
import os
from .extract_urls import ExtractTarget, detect_extract_clipboard


def get_arg_or_env_item(args_key: str, args: argparse.Namespace, env_key: str):

    args_dict = args.__dict__
    if (args_key in args_dict and args_dict[args_key] and len(args_dict[args_key]) > 0):
        return args_dict[args_key]

    if (str(env_key) in os.environ):
        return os.environ[env_key]

    return None


def get_arg_or_env_list(args_key: str, args: argparse.Namespace, env_key: str):

    item = get_arg_or_env_item(args_key, args, env_key)

    if (isinstance(item, list)):
        return item

    if (item):
        return [item]

    return None


def get_arg_or_env_or_clipboard_list(args_key: str, args: argparse.Namespace, env_key: str, clipboard_extract_target: ExtractTarget, prefer_clipboard=False):

    if (prefer_clipboard):
        clipboard_extracted_items_list = detect_extract_clipboard(clipboard_extract_target)
        if (clipboard_extracted_items_list and len(clipboard_extracted_items_list) >= 0):
            return clipboard_extracted_items_list

    arg_or_env_list = get_arg_or_env_list(args_key, args, env_key)
    if (arg_or_env_list and len(arg_or_env_list) > 0):
        return arg_or_env_list

    if (not prefer_clipboard):
        clipboard_extracted_items_list = detect_extract_clipboard(clipboard_extract_target)
        if (clipboard_extracted_items_list and len(clipboard_extracted_items_list) >= 0):
            return clipboard_extracted_items_list

    raise Exception("Failed getting parameter from 'arguments', 'environment' or from the clipboard -- get_arg_or_env_or_clipboard_list")


# def get_urls_arg_env_or_clipboard(args, prefer_clipboard=False):
#    return get_arg_or_env_or_clipboard_list('urls', args, QuteEnvVars.URL, extract_tool.ExtractTarget.URL, prefer_clipboard=prefer_clipboard)


def add_logging_options(parser: argparse.ArgumentParser):
    parser.add_argument('-v', '--verbose', action="store_true", help="Verbose logging")
    parser.add_argument('-d', '--debug', action="store_true", help="Debug logging")


def init_logging(args: argparse.Namespace):
    if args.verbose or args.debug:
        logging.basicConfig(level=logging.DEBUG)


def get_logger():
    return logging.getLogger()
