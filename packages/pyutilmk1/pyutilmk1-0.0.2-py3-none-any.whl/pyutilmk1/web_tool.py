import requests


def is_url(path):
    if (path is None):
        return False

    if (path.startswith("https://") or path.startswith("http://")):
        return True
    return False


def page_exists(url):
    if (url is None):
        return False

    request = requests.get(url)
    if request.status_code == 200:
        return True
    return False


def get_url_contents_utf8(url):
    if (not is_url(url)):
        return None

    request = requests.get(url)
    return request.text
