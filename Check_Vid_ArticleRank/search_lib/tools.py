import os.path
from urllib.parse import urlparse, parse_qsl, unquote_plus

import pandas as pd


class Url(object):
    """
    A url object that can be compared with other url objects
    without regard to the vagaries of encoding, escaping, and ordering
    of parameters in query strings.
    """

    def __init__(self, url):
        parts = urlparse(url)
        _query = frozenset(parse_qsl(parts.query))
        _path = unquote_plus(parts.path)
        parts = parts._replace(query=_query, path=_path)
        self.parts = parts

    def __eq__(self, other):
        return self.parts == other.parts

    def __hash__(self):
        return hash(self.parts)


def check_contains_columns(file):
    extension = os.path.splitext(file)[-1]
    if extension == ".xlsx":
        pass
    elif extension == ".csv":
        df = pd.read_csv(file)
        if "Title" in df.columns:
            return True
    return False
