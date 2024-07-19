import urllib.parse
from typing import Optional, Dict


def quote_url(url: str) -> str:
    """
    >>> quote_url('abc def')
    'abc%20def'

    :param url:
    :return:
    """
    return urllib.parse.quote(url)


def unquote_url(url: str) -> str:
    """
    >>> unquote_url('abc%20def')
    'abc def'

    :param url:
    :return:
    """
    return urllib.parse.unquote(url)


def urlencode(params: Dict) -> str:  # noqa
    """
    >>> urlencode({'a': 1, 'b': 2, 'c': 3})
    'a=1&b=2&c=3'

    :param params:
    :return:
    """
    return urllib.parse.urlencode(params)


def urldecode(url: str) -> Dict:
    """
    >>> urldecode('a=1&b=2&c=3')
    {'a': '1', 'b': '2', 'c': '3'}

    :param url:
    :return:
    """
    params = dict()

    kvs = url.split('?')[-1].split('&')
    for kv in kvs:
        k, v = kv.split('=', 1)
        params[k] = unquote_url(v)

    return params


def join_params(url: str, params: Optional[Dict]) -> str:
    """
    >>> join_params("https://www.baidu.com/s", {"ie": "UTF-8", "wd": "abc"})
    'https://www.baidu.com/s?ie=UTF-8&wd=abc'

    :param url: 
    :param params: 
    :return: 
    """
    if not params:
        return url

    params = urlencode(params)
    separator = '?' if '?' not in url else '&'
    return url + separator + params
