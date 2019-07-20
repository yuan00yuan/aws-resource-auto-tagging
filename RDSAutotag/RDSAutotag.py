#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/2 下午8:03
# @Author  : Dicey
# @File    : RDSAutotag.py
# @Software: PyCharm


from __future__ import print_function
import json
import boto3
import logging


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

    # 判断事件是来自 User 实体还是来自 Rule
    if userType == 'IAMUser':
        user = detail['userIdentity']['userName']
    else:
        user = principal.split(':')[1]

    logger.info('principalId: ' + str(principal))
    logger.info('region: ' + str(region))
    logger.info('eventName: ' + str(eventname))
    logger.info('detail: ' + str(detail))

    client = boto3.client('rds')
    resource_arn = detail['responseElements']['dBInstanceArn']

    if eventname == 'CreateDBInstance':
        tags = [{'Key': 'Owner', 'Value': user}, {'Key': 'PrincipalId', 'Value': principal}]
        client.add_tags_to_resource(ResourceName=resource_arn, Tags=tags)
    else:
        logger.warning('Not supported action')
