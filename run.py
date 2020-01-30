#!/usr/bin/env python
# from gevent import monkey
from gevent import pywsgi
from medicine.wsgi import application

# monkey.patch_all()
HOST = '127.0.0.1'
PORT = 8000
# set spawn=None for memcache
if __name__ == '__main__':
    print('---------------------Server Start-----------------------')
    pywsgi.WSGIServer(('', PORT), application).serve_forever()
