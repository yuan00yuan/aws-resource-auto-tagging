#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/3 下午12:20
# @Author  : Dicey
# @File    : SQSAutotag.py
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

    client = boto3.client('sqs')
    queue_url = detail['responseElements']['queueUrl']

    if eventname == 'CreateQueue':
        tags = {'Owner': user, 'PrincipalId': principal}
        client.tag_queue(QueueUrl=queue_url, Tags=tags)
        logger.info("Success!")
        return True
    else:
        logger.warning('Not supported action')
        return False