# coding: utf-8

import socket


DEFAULT_HOST = "localhost"

class ReqType:
    VALUE = 1
    TYPE = 2
    MEMBERS = 3
    ALL = 4


class VSDbgConnector(object):
    def __init__(self, host, port):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.connect((host, port))

    def __del__(self):
        self._sock.close()

    def call(self, type, expr):
        self._sock.sendall('%d|%s' % (type, expr))
        return self._sock.recv(4096)


_dbgConn = None


def conn(port, host=DEFAULT_HOST):
    ''' Connect to VS add-in '''
    global _dbgConn
    _dbgConn = VSDbgConnector(host, port)


def p(expr):
    ''' retrieves expression '''
    global _dbgConn
    if _dbgConn is None:
        return "Connection isn't initialized."
    return _dbgConn.call(ReqType.ALL, expr)


def v(expr):
    ''' retrieves expression's value '''
    global _dbgConn
    if _dbgConn is None:
        return "Connection isn't initialized."
    return _dbgConn.call(ReqType.VALUE, expr)


def t(expr):
    ''' retrieves expression's type '''
    global _dbgConn
    if _dbgConn is None:
        return "Connection isn't initialized."
    return _dbgConn.call(ReqType.TYPE, expr)


def m(expr):
    ''' retrieves list of expression's members '''
    global _dbgConn
    if _dbgConn is None:
        return "Connection isn't initialized."
    return _dbgConn.call(ReqType.MEMBERS, expr)
