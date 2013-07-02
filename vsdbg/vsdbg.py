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


def __cast_expr(expr, type):
    return "((%s)%s)" % (type, expr)

__RE_CLASS_NAME = '[A-Za-z_][\w\.<>,]+'


def __get_types(expr):
    def get_types_rec(expr, tp):
        for x in m(__cast_expr(expr, tp)):
            v = re.search('base {(%s)}' % __RE_CLASS_NAME, x)
            if v:
                yield v.group(1)
                for x in get_types_rec(expr, v.group(1)): yield x
                break
    tp = t(expr)
    v = re.search('{(%s)}' % __RE_CLASS_NAME, tp)
    if v: tp = v.group(1)
    yield tp
    for x in get_types_rec(expr, tp): yield x


def __get_generic_subtypes(expr):
    for x in m('%s, raw' % expr):
        v = re.search('base {(%s)}' % __RE_CLASS_NAME, x)
        if v:
            v = re.search('<(%s)>' % __RE_CLASS_NAME, v.group(1))
            return (v.group(1) if v else '')
    return ''


def __is_type(expr, tp):
    for x in m('%s, raw' % expr):
        v = re.search('base {(%s)}' % __RE_CLASS_NAME, x)
        if v and tp in v.group(0):
            return True
    return False


def __split_indexer(expr):
    ''' splits string as 'xxx[000]' to 'xxx', '[000]' '''
    s = expr.split('[')
    return '['.join(s[:-1]), '[' + s[-1]


def __dump(expr, level, depth):
    def loop_members(e):
        for x in [i.strip() for i in m(e)]:
            if x == '' or x == 'Raw View' or 'base ' in x:  # skip "Raw View", "base {class_name}"
                continue
            elif x[0] == '[':  # [???]
                if x[1] == '0':  # handle index [0x0???] (and skip [class_name] memebers)
                    yield __dump('%s%s' % (e, x), level + 1, depth - 1)
            else:
                yield __dump('%s.%s' % (e, x), level + 1, depth - 1)

    def handle_dictionary(expr):
        e, i = __split_indexer(expr)
        if __is_type(e, 'System.Collections.Generic.Dictionary'):
            expr = "(new System.Collections.Generic.Mscorlib_DictionaryDebugView<%s>(%s)).Items%s" % (__get_generic_subtypes(e), e, i)
            val = v(expr)
            return expr, val
        return expr, None

    if depth == 0: return '%s : Max depth reached.' % expr
    res = []
    try:
        val = None
        if expr[-1] == ']':  # if we have index access
            expr, val = handle_dictionary(expr)
        val = (v(expr) if not val else val)

        res.append('%s%s: %s' % ('  ' * level, expr.split('.')[-1].split('>')[-1].replace(')', ''), val))

        exps = [__cast_expr(expr, x) for x in __get_types(expr)]  # cast expr to every possible type to access all hidden members
        for e in (exps if len(exps) > 0 else [expr]):
            res += loop_members(e)
    except Exception as e:
        res.append(str(e))
    return '\n'.join(res)


def dump(expr, maxdepth=10):
    ''' retrieves expression and recursively dump all children '''
    return __dump(expr, 0, maxdepth)  # idealy this functionality should be moved to VSDebugConnector

