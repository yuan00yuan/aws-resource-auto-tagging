#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/4 上午10:49
# @Author  : Dicey
# @File    : AWSAutoTagTotal3.0.py
# @Software: PyCharm

from __future__ import print_function
import json
import boto3
import logging
from AWSAutotagTotal import awstaglib

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    detail = event['detail']
    eventname = detail['eventName']

    tagger = awstaglib.Tagger(event)

    if eventname == 'RunInstances':
        # 启动 EC2
        tagger.tag_ec2()

    elif eventname == 'CreateTable':
        # Dynamodb
        tagger.tag_dynamodb()

    elif eventname == 'CreateFunction20150331':
        # Lambda
        tagger.tag_lambda()

    elif eventname == 'CreateDBInstance':
        # RDS
        tagger.tag_rds()

    elif eventname == 'CreateCluster':
        # RedShift
        tagger.tag_redshift()

    elif eventname == 'CreateBucket':
        # 给 S3 桶打标签
        tagger.tag_s3_bucket()

    elif eventname == 'PutObject':
        # 给 S3 中 Object 打标签
        tagger.tag_s3_object()

    elif eventname == 'CreateQueue':
        # SQS
        tagger.tag_sqs()

    elif eventname == 'CreateVpc':
        # VPC
        tagger.tag_vpc()
    else:
        logger.warning('Not supported action')
        return False

    logger.info("Success!")
    return True