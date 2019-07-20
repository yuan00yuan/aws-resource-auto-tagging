#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/2 下午3:03
# @Author  : Dicey
# @File    : S3AutotagVObject.py
# @Software: PyCharm


from __future__ import print_function
import json
import boto3
import logging


'''
为 S3 自动打 tag 的 对象级别版本
S3 的 API 都已经在 CloudWatch 中给出
可以直接添加

特别的, 对象级别(Object Level Operations)的 Cloud Trail 记录需要手动开启
请参考: https://docs.aws.amazon.com/zh_cn/AmazonS3/latest/user-guide/enable-cloudtrail-events.html
'''


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    print("=========================")

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

        s3 = boto3.client("s3")

        bucket_name = detail['requestParameters']['bucketName']
        object_name = detail['requestParameters']['key']

        if eventname == 'PutObject':
            tags = [{'Key': 'Owner', 'Value': user}, {'Key': 'PrincipalId', 'Value': principal}]
            s3.put_object_tagging(Bucket=bucket_name, Key=object_name, Tagging={'TagSet': tags})
        else:
            logger.warning('Not supported action')

        logger.info(' Remaining time (ms): ' + str(context.get_remaining_time_in_millis()) + '\n')
        print("+++++++++++++++++++++++++")

    except Exception as e:
        logger.error('Something went wrong: ' + str(e))
        return False