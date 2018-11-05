# -*- coding: utf-8 -*-

"""
This module handles import compatibility issues between Python 2 and
Python 3.
"""

import sys
import random
import string

# -------
# Pythons
# -------

# Syntax sugar.
_ver = sys.version_info

#: Python 2.x?
is_py2 = (_ver[0] == 2)

#: Python 3.x?
is_py3 = (_ver[0] == 3)

try:
    import simplejson as json
except ImportError:
    import json

# ---------
# Specifics
# ---------

if is_py2:
    from urllib2 import Request, urlopen, HTTPError, URLError
    builtin_str = str
    bytes = str
    str = unicode
    basestring = basestring
    numeric_types = (int, long, float)
    integer_types = (int, long)

elif is_py3:
    from urllib.request import Request, urlopen
    from urllib.error import HTTPError, URLError
    builtin_str = str
    str = str
    bytes = bytes
    basestring = (str, bytes)
    numeric_types = (int, float)
    integer_types = (int,)


def enc(x):
    if isinstance(x, str):
        return x.encode('utf-8')
    elif isinstance(x, numeric_types):
        return str(x).encode('utf-8')
    return x


def choose_boundary():
    rand_letters = ''.join(random.sample(string.ascii_letters+string.digits, 15))
    return '{ch}{flag}{rand}'.format(ch='-'*6, flag='PylibFormBoundary', rand=rand_letters)
