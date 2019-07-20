#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/2 上午10:48
# @Author  : Dicey
# @File    : Lambda2Autotag.py
# @Software: PyCharm

from __future__ import print_function
import json
import boto3
import logging


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    # print('Received event: ' + json.dumps(event, indent=2))
    print("+++++++++++++++++++")

    try:
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

        # 是否收到正确响应
        # 当删除 Lambda 时是响应是空的
        if not detail['responseElements']:
            logger.warning('Not responseElements found')
            if detail['errorCode']:
                logger.error('errorCode: ' + detail['errorCode'])
            if detail['errorMessage']:
                logger.error('errorMessage: ' + detail['errorMessage'])
            return False

        # Lambda 函数的 arn
        function_arn = detail['responseElements']['functionArn']
        logger.info('function_arn: ' + function_arn)

        client = boto3.client('lambda')

        # 根据事件构造 tag list, 以后可根据需要扩展功能
        if eventname == 'CreateFunction20150331':
            tag = {'Owner': user, 'PrincipalId': principal}
            client.tag_resource(Resource=function_arn, Tags=tag)
        else:
            logger.warning('Not supported action')

        logger.info(' Remaining time (ms): ' + str(context.get_remaining_time_in_millis()) + '\n')

        print("------------------")
        return True
    except Exception as e:
        logger.error('Something went wrong: ' + str(e))
        return False