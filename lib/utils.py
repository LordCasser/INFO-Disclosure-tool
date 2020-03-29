# -*- coding: utf-8 -*-
#####
#Author: LordCasser
# Date: 2020-03-27 15:51:23
#LastEditTime: 2020-03-27 18:21:37
#LastEditors: LordCasser
# Description:
#####

__author__ = 'gakki429'

import os
import sys
import struct
from urllib import request
try:
    from ctypes import windll, create_string_buffer
except ImportError:
    pass
import ssl

def win_default_color():
    stdout_handle = windll.kernel32.GetStdHandle(-11)
    csbi = create_string_buffer(22)
    windll.kernel32.GetConsoleScreenBufferInfo(stdout_handle, csbi)
    wattr = struct.unpack("hhhhHhhhhhh", csbi.raw)[4]
    return wattr


if sys.platform.startswith('win'):
    default = win_default_color()
    default_bg = default & 0xf0


def win_set_color(color='cyan'):
    win_color = {
        'green': 0xa,
        'cyan': 0xb,
        'red': 0xc,
        'default': default,
    }
    stdout_handle = windll.kernel32.GetStdHandle(-11)
    windll.kernel32.SetConsoleTextAttribute(
        stdout_handle, win_color[color] | default_bg)


def _print(stdout, color='cyan'):
    if sys.platform.startswith('win'):
        win_set_color(color)
        print('{}\r\n'.format(stdout), end=' ')
        win_set_color('default')
    else:
        unix_color = {
            'red': 31,
            'green': 32,
            'cyan': 36,
        }
        print('\033[1;{}m{}\033[0m\n'.format(
            unix_color[color], stdout), end=' ')


def _mkdir(path):
    path = os.path.dirname(path)
    if path and not os.path.exists(path):
        os.makedirs(path)


def getFile(path,local=True):
    if local and os.path.exists(path):
        return open(path, 'rb').read()
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        resp = request.urlopen(path, context=ctx)
        if resp.getcode() == 200:
            data = resp.read()
            _mkdir(path)
            open(path, 'wb').write(data)
            return data
    except Exception as e:
        _print('[-] File not exist {} '.format(path), 'red')
        return
