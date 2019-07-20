#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/1 下午5:30
# @Author  : Dicey
# @File    : RunInstanceTest.py
# @Software: PyCharm

import boto3

client = boto3.client("ec2")
client.run_instances(MaxCount=1, MinCount=1, ImageId='ami-ffd00992')