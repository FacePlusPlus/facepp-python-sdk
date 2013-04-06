#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# $File: cmdtool.py
# $Date: Sat Apr 06 15:42:43 2013 +0800
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

def init():
    import sys
    import os
    import os.path
    if sys.version_info.major != 2:
        sys.exit('Python 2 is required to run this program')

    fdir = None
    if hasattr(sys, "frozen") and \
            sys.frozen in ("windows_exe", "console_exe"):
        fdir = os.path.dirname(os.path.abspath(sys.executable))
        sys.path.append(fdir)
        fdir = os.path.join(fdir, '..')
    else:
        fdir = os.path.dirname(__file__)

    with open(os.path.join(fdir, 'apikey.cfg')) as f:
        exec(f.read())

    srv = locals().get('SERVER')
    from facepp import API
    return API(API_KEY, API_SECRET, srv = srv)

api = init()

from facepp import API, File

del init

def _run():
    global _run
    _run = lambda: None

    msg = """
===================================================
Welcome to Face++ Interactive Shell!
Here, you can explore and play with Face++ APIs :)
---------------------------------------------------
Getting Started:
    0. Register a user and API key on http://www.faceplusplus.com
    1. Write your API key/secret in apikey.cfg
    2. Start this interactive shell and try various APIs
        For example, to find all faces in a local image file, just type:
            api.detection.detect(img = File(r'<path to the image file>'))

Enjoy!
"""

    try:
        from IPython import embed
        embed(banner2 = msg)
    except ImportError:
        import code
        code.interact(msg, local = globals())


if __name__ == '__main__':
    _run()
