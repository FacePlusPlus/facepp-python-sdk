# -*- coding: utf-8 -*-
# $File: facepp.py
# $Date: Mon Dec 17 14:47:27 2012 +0800
# $Author: jiakai@megvii.com
#
# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What The Fuck You Want
# To Public License, Version 2, as published by Sam Hocevar. See
# http://sam.zoy.org/wtfpl/COPYING (copied as below) for more details.
#
#                DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE 
#                        Version 2, December 2004 
#
#     Copyright (C) 2004 Sam Hocevar <sam@hocevar.net> 
#
#     Everyone is permitted to copy and distribute verbatim or modified 
#     copies of this license document, and changing it is allowed as long 
#     as the name is changed. 
#
#                DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE 
#       TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION 
#
#      0. You just DO WHAT THE FUCK YOU WANT TO. 

"""a simple facepp sdk
example:
api = API(key, secret)
api.detection.detect(img = File('/tmp/test.jpg'))"""

__all__ = ['File', 'APIError', 'API']


DEBUG_LEVEL = 0

import sys
import socket
import urllib
import urllib2
import json
import os
import itertools
import mimetools
import mimetypes
import time
from collections import Iterable
from cStringIO import StringIO

class File(object):
    """an object representing a local file"""
    path = None
    def __init__(self, path):
        self.path = path

class APIError(Exception):
    code = None
    """HTTP status code"""

    url = None
    """request URL"""

    body = None
    """server response body; or detailed error information"""

    def __init__(self, code, url, body):
        self.code = code
        self.url = url
        self.body = body

    def __str__(self):
        return 'code={s.code}\nurl={s.url}\n{s.body}'.format(s = self)

    __repr__ = __str__


class API(object):
    key = None
    secret = None
    server = 'http://api.faceplusplus.com/'

    decode_result = True
    timeout = None
    max_retries = None
    retry_delay = None

    def __init__(self, key, secret, srv = None,
            decode_result = True, timeout = 30, max_retries = 10,
            retry_delay = 5):
        """:param srv: The API server address
        :param decode_result: whether to json_decode the result
        :param timeout: HTTP request timeout in seconds
        :param max_retries: maximal number of retries after catching URL error
            or socket error
        :param retry_delay: time to sleep before retrying"""
        self.key = key
        self.secret = secret
        if srv:
            self.server = srv
        self.decode_result = decode_result
        assert timeout >= 0 or timeout is None
        assert max_retries >= 0
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        _setup_apiobj(self, self, [])

    def wait_async(self, session_id, referesh_interval = 2):
        """wait for asynchronous operations to complete"""
        while True:
            rst = self.info.get_session(session_id = session_id)
            if rst['status'] != u'INQUEUE':
                return rst
            time.sleep(referesh_interval)

    def update_request(self, request):
        """overwrite this function to update the request before sending it to
        server"""
        pass


def _setup_apiobj(self, api, path):
    if self is not api:
        self._api = api
        self._urlbase = api.server + '/'.join(path)

    lvl = len(path)
    done = set()
    for i in _APIS:
        if len(i) <= lvl:
            continue
        cur = i[lvl]
        if i[:lvl] == path and cur not in done:
            done.add(cur)
            setattr(self, cur, _APIProxy(api, i[:lvl + 1]))

class _APIProxy(object):
    _api = None
    """underlying :class:`API` object"""

    _urlbase = None

    def __init__(self, api, path):
        _setup_apiobj(self, api, path)

    def __call__(self, *args, **kargs):
        if len(args):
            raise TypeError('Only keyword arguments are allowed')
        url = self.geturl(**kargs)
        request = urllib2.Request(url)
        form = _MultiPartForm()
        add_form = False
        for (k, v) in kargs.iteritems():
            if isinstance(v, File):
                add_form = True
                with open(v.path, 'rb') as f:
                    form.add_file(k, v.path, f)
        if add_form:
            body = str(form)
            request.add_header('Content-type', form.get_content_type())
            request.add_header('Content-length', str(len(body)))
            request.add_data(body)

        self._api.update_request(request)

        retry = self._api.max_retries
        while True:
            retry -= 1
            try:
                ret = urllib2.urlopen(request, timeout = self._api.timeout).read()
                break
            except urllib2.HTTPError as e:
                raise APIError(e.code, url, e.read())
            except (socket.error, urllib2.URLError) as e:
                if retry < 0:
                    raise e
                _print_debug('caught error: {}; retrying'.format(e))
                time.sleep(self._api.retry_delay)

        if self._api.decode_result:
            try:
                ret = json.loads(ret)
            except:
                raise APIError(-1, url, 'json decode error, value={0!r}'.format(ret))
        return ret

    def geturl(self, **kargs):
        """return the request url"""
        def enc(x):
            if isinstance(x, unicode):
                return x.encode('utf-8')
            return str(x)
        kargs = kargs.copy()
        kargs['api_key'] = self._api.key
        kargs['api_secret'] = self._api.secret
        for (k, v) in kargs.items():
            if isinstance(v, Iterable) and not isinstance(v, basestring):
                kargs[k] = ','.join([enc(i) for i in v])
            elif isinstance(v, File) or v is None:
                del kargs[k]
            else:
                kargs[k] = enc(v)
        return self._urlbase + '?' + urllib.urlencode(kargs) 

    def visit(self, browser = 'chromium', **kargs):
        """visit the url in browser"""
        os.system('{0} "{1}"'.format(browser, self.geturl(**kargs)))



# ref: http://www.doughellmann.com/PyMOTW/urllib2/
class _MultiPartForm(object):
    """Accumulate the data to be used when posting a form."""

    def __init__(self):
        self.form_fields = []
        self.files = []
        self.boundary = mimetools.choose_boundary()
        return
    
    def get_content_type(self):
        return 'multipart/form-data; boundary=%s' % self.boundary

    def add_field(self, name, value):
        """Add a simple field to the form data."""
        self.form_fields.append((name, value))
        return

    def add_file(self, fieldname, filename, fileHandle, mimetype=None):
        """Add a file to be uploaded."""
        body = fileHandle.read()
        if mimetype is None:
            mimetype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        self.files.append((fieldname, filename, mimetype, body))
        return
    
    def __str__(self):
        """Return a string representing the form data, including attached files."""
        # Build a list of lists, each containing "lines" of the
        # request.  Each part is separated by a boundary string.
        # Once the list is built, return a string where each
        # line is separated by '\r\n'.  
        parts = []
        part_boundary = '--' + self.boundary
        
        # Add the form fields
        parts.extend(
            [ part_boundary,
              'Content-Disposition: form-data; name="%s"' % name,
              '',
              value,
            ]
            for name, value in self.form_fields
            )
        
        # Add the files to upload
        parts.extend(
            [ part_boundary,
              'Content-Disposition: file; name="%s"; filename="%s"' % \
                 (field_name, filename),
              'Content-Type: %s' % content_type,
              '',
              body,
            ]
            for field_name, filename, content_type, body in self.files
            )
        
        # Flatten the list and add closing boundary marker,
        # then return CR+LF separated data
        flattened = list(itertools.chain(*parts))
        flattened.append('--' + self.boundary + '--')
        flattened.append('')
        return '\r\n'.join(flattened)


def _print_debug(msg):
    if DEBUG_LEVEL:
        sys.stderr.write(msg + '\n')

_APIS = [
    '/detection/detect',

    '/info/get_image',
    '/info/get_face',
    '/info/get_session',
    '/info/get_quota',
    '/info/get_person_list',
    '/info/get_group_list',
    '/info/get_app',

    '/person/create',
    '/person/delete',
    '/person/add_face',
    '/person/remove_face',
    '/person/get_info',
    '/person/set_info',

    '/group/create',
    '/group/delete',
    '/group/add_person',
    '/group/remove_person',
    '/group/get_info',
    '/group/set_info',

    '/recognition/compare',
    '/recognition/train',
    '/recognition/verify',
    '/recognition/recognize',
    '/recognition/search',
]

_APIS = [i.split('/')[1:] for i in _APIS]
