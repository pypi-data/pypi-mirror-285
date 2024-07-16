#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/6/12 下午7:34
@Author  : Gie
@File    : inner_ip.py
@Desc    :
"""
import platform
import socket


def get_linux_inner_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('www.baidu.com', 0))
        ip = s.getsockname()[0]
    except:
        return

    return ip


def get_inner_ip():
    sys_platform = platform.system()

    if sys_platform == "Windows":
        inner_ip = socket.gethostbyname(socket.gethostname())
        print(f'get inner ip for windows: {inner_ip}')
        return inner_ip

    if sys_platform == "Linux":
        inner_ip = get_linux_inner_ip()
        print(f"get inner ip for linux: {inner_ip}")
        return inner_ip
    elif sys_platform == "Darwin":
        inner_ip = socket.gethostbyname(socket.gethostname())
        print(f"get inner ip for MacOs: {inner_ip}")
        return inner_ip
    else:
        print("Other System @ some ip")
        return
