#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/3 上午11:17
# @Author  : Dicey
# @File    : VPCAutotag.py
# @Software: PyCharm

from __future__ import print_function
import json
import boto3
import logging

'''
VPC 的 API 位与 EC2下
在设置 CloudWatch 时请将事件源设置为 EC2
'''

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    print("=========================")

    region = event['region']
    detail = event['detail']
    eventname = detail['eventName']
    arn = detail['userIdentity']['arn']
    principal = detail['userIdentity']['principalId']
    userType = detail['userIdentity']['type']
    vpc_id = detail['responseElements']['vpc']['vpcId']

    # 判断事件是来自 User 实体还是来自 Rule
    if userType == 'IAMUser':
        user = detail['userIdentity']['userName']
    else:
        user = principal.split(':')[1]

    logger.info('principalId: ' + str(principal))
    logger.info('region: ' + str(region))
    logger.info('eventName: ' + str(eventname))
    logger.info('detail: ' + str(detail))

    ec2 = boto3.resource('ec2')
    vpc = ec2.Vpc(vpc_id)

    if eventname == 'CreateVpc':
        tags = [{'Key': 'Owner', 'Value': user}, {'Key': 'PrincipalId', 'Value': principal}]
        vpc.create_tags(DryRun=False, Tags=tags)
        logger.info("Success!")
        return True
    else:
        logger.warning('Not supported action')
        return False