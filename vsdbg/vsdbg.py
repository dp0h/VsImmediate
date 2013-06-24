# coding: utf-8
'''
'''

import os
import socket
import tempfile
import re


class ReqType:
    VALUE = 1
    TYPE = 2
    MEMBERS = 3
    ALL = 4


class RespType:
    ERROR = 1
    VALUE = 2
    ARRAY = 3

BEL = '\x07'
PORT_FNAME = 'vsdbg.port'

_port = 0
_host = "localhost"


def _dbg_call(tp, expr):
    global _host, _port
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((_host, _port))
    s.sendall('%d%s%s' % (tp, BEL, expr))
    res = s.recv(4096)
    s.close()
    res = res.split(BEL)
    if len(res) < 2:
        raise Exception('Invalid respose')
    if int(res[0]) == RespType.ERROR:
        raise Exception(res[1])
    elif int(res[0]) == RespType.ARRAY:
        return res[1:]
    else:
        return res[1]


def detect():
    ''' Get port number from temp file '''
    port_fname = os.path.join(tempfile.gettempdir(), PORT_FNAME)
    if os.path.exists(port_fname):
        with open(port_fname) as f:
            global _port
            _port = int(f.readlines()[0])
    else:
        raise Exception('Could not find port number. Please load/realod VS add-in.')


def port(p):
    global _port
    _port = p


def host(h):
    global _host
    _host = h


def p(expr):
    ''' retrieves expression with all memebers '''
    return _dbg_call(ReqType.ALL, expr)


def v(expr):
    ''' retrieves expression's value '''
    return _dbg_call(ReqType.VALUE, expr)


def t(expr):
    ''' retrieves expression's type '''
    return _dbg_call(ReqType.TYPE, expr)


def m(expr):
    ''' retrieves list of expression's members '''
    return _dbg_call(ReqType.MEMBERS, expr)


def enum_array(expr):
    val = int(re.search('\d+', v(expr)).group(0))
    for x in range(0, val):
        yield '%s[%d]' % (expr, x)


def __rdump(expr, level, depth):
    if depth == 0:
        return '%s : Max depth reached.' % expr
    res = []
    try:
        res.append('%s%s: %s' % ('  ' * level, expr.split('.')[-1], v(expr)))
        for x in m(expr):
            if x.strip() != '' and x.strip() != 'Raw View':
                res.append(__rdump('%s%s%s' % (expr, '.' if x[0] != '[' else '', x), level + 1, depth - 1))
    except Exception as e:
        res.append(str(e))
    return '\n'.join(res)


def dump(expr, maxdepth=10):
    ''' retrieves expression and recursively dump all children '''
    return __rdump(expr, 0, maxdepth)

