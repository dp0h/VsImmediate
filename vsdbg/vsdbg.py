# coding: utf-8
''' 
Functions which call VSDebugConnector Add-In API for expression evaluation in VS debugger.
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


try:
    detect()  # call detect during module loading
except Exception as e:
    print(e)


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



def cast_expr(expr, type):
    return "((%s)%s)" % (type, expr)

RE_CLASS_NAME = '[A-Za-z_][\w\.<>]+'


def get_types(expr):
    def get_types_rec(expr, tp):
        for x in m(cast_expr(expr, tp)):
            v = re.search('base {(%s)}' % RE_CLASS_NAME, x)
            if v:
                yield v.group(1)
                for x in get_types_rec(expr, v.group(1)): yield x
                break
    tp = t(expr)
    v = re.search('{(%s)}' % RE_CLASS_NAME, tp)
    if v: tp = v.group(1)
    yield tp
    for x in get_types_rec(expr, tp): yield x


def __dump(expr, level, depth):
    if depth == 0:
        return '%s : Max depth reached.' % expr
    res = []
    try:
        # dictionaries and list requires specic formatters
        res.append('%s%s: %s' % ('  ' * level, expr.split('.')[-1].split('>')[-1].replace(')', ''), v(expr)))

        exps = [cast_expr(expr, x) for x in get_types(expr)]
        if len(exps) == 0: exps.append(expr)
        for e in exps:
            for x in [i.strip() for i in m(e)]:
                if x == '' or x == 'Raw View' or 'base ' in x:  # skip "Raw View", "base {class_name}"
                    continue
                elif x[0] == '[':  # [???]
                    if x[1] != '0':  # [class_name]
                        pass
                    else:  # we have index [0x0???]
                        res.append(__dump('%s%s' % (e, x), level + 1, depth - 1))
                else:
                    res.append(__dump('%s.%s' % (e, x), level + 1, depth - 1))
    except Exception as e:
        res.append(str(e))
    return '\n'.join(res)


def dump(expr, maxdepth=10):
    ''' retrieves expression and recursively dump all children '''
    return __dump(expr, 0, maxdepth)  # idealy this functionality should be moved to VSDebugConnector

