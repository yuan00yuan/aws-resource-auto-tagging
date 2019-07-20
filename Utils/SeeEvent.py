#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/7/16 上午11:30
# @Author  : Dicey
# @File    : SeeEvent.py
# @Software: PyCharm

from __future__ import print_function

import datetime
import boto3

def lambda_handler(event, context):
    import json
    tran(json.dumps(event, indent=2))


def tran(str_test):
    str2 = ""
    for s in str_test:
        if s == "'":
            str2 = str2 + "\""
        elif s == "," or s == "[" or s == "]" or s == "{" or s == "}":
            str2 = str2 + s + "\n" + "  "
        else:
            str2 = str2 + s
    print(str2)


if __name__ == '__main__':

    tran()