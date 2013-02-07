# coding: utf-8

import socket


class ReqType:
    VALUE = 1
    TYPE = 2
    MEMBERS = 3
    ALL = 4

BEL = '\x07'

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
    if int(res[0]) == 1:
        raise Exception(res[1])
    return res[1]


def port(p):
    global _port
    _port = p


def host(h):
    global _host
    _host = h


def p(expr):
    ''' retrieves expression '''
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
