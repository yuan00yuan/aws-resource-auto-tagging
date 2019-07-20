#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/3 上午9:39
# @Author  : Dicey
# @File    : RedShiftAutotag.py
# @Software: PyCharm

from __future__ import print_function
import json
import boto3
import logging

'''
在 API 中并没有提供获取 RedShift ARN 的方法, 需要自己手动拼接
以下为更多 RedShift ARN 的格式:

arn:aws:redshift:region:account-id:cluster:cluster-name
arn:aws:redshift:region:account-id:dbname:cluster-name/database-name
arn:aws:redshift:region:account-id:dbuser:cluster-name/database-user-name
arn:aws:redshift:region:account-id:dbgroup:cluster-name/database-group-name
arn:aws:redshift:region:account-id:parametergroup:parameter-group-name
arn:aws:redshift:region:account-id:securitygroup:security-group-name
arn:aws:redshift:region:account-id:snapshot:cluster-name/snapshot-name
arn:aws:redshift:region:account-id:subnetgroup:subnet-group-name

特别的, 中国区的 ARN 形如
arn:aws-cn:redshift:region:account-id:cluster:cluster-name
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
        account_id = event['account']

        # 判断事件是来自 User 实体还是来自 Rule
        if userType == 'IAMUser':
            user = detail['userIdentity']['userName']
        else:
            user = principal.split(':')[1]

        logger.info('principalId: ' + str(principal))
        logger.info('region: ' + str(region))
        logger.info('eventName: ' + str(eventname))
        logger.info('detail: ' + str(detail))

        client = boto3.client('redshift')
        cluster_name = detail['requestParameters']['clusterIdentifier']

        # 拼接 arn
        resource_arn = "arn:aws-cn:redshift:" + str(region) + ":" + str(account_id) + ":cluster:" + cluster_name
        logger.info("arn: " + resource_arn)

        if eventname == 'CreateCluster':
            tags = [{'Key': 'Owner', 'Value': user}, {'Key': 'PrincipalId', 'Value': principal}]
            client.create_tags(ResourceName=resource_arn, Tags=tags)
            logger.info("Success!")
            return True
        else:
            logger.warning('Not supported action')
            return False

    except Exception as e:
        logger.error('Something went wrong: ' + str(e))
        return False