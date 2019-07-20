#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/4 上午1:29
# @Author  : Dicey
# @File    : awstaglib.py
# @Software: PyCharm


import logging
import boto3


class Tagger:
    detail = {}
    user = ""
    principal = ""
    logger = logging.getLogger()
    event = {}
    region = ""

    def __init__(self, event):
        # 构造方法
        self.event = event
        self.region = str(event['region'])
        self.detail = event['detail']
        self.principal = self.detail['userIdentity']['principalId']
        userType = self.detail['userIdentity']['type']

        # 判断事件是来自 User 实体还是来自 Rule
        if userType == 'IAMUser':
            self.user = self.detail['userIdentity']['userName']
        else:
            # 若非实体用户则从 principal 中截取 Rule 的信息
            self.user = self.principal.split(':')[1]

        self.logger.info('principalId: ' + str(self.principal))
        self.logger.info('region: ' + str(self.region))
        self.logger.info('detail: ' + str(self.detail))
        self.logger.setLevel(logging.INFO)

    def tag_ec2(self):
        '''
        给 EC2 打 tag
        :return:
        '''
        ids = []
        ec2 = boto3.resource('ec2')

        items = self.detail['responseElements']['instancesSet']['items']
        for item in items:
            ids.append(item['instanceId'])
        self.logger.info(ids)
        self.logger.info('number of instances: ' + str(len(ids)))

        base = ec2.instances.filter(InstanceIds=ids)

        # loop through the instances
        for instance in base:
            for vol in instance.volumes.all():
                ids.append(vol.id)
            for eni in instance.network_interfaces:
                ids.append(eni.id)
        if ids:
            for resourceid in ids:
                print('Tagging resource ' + resourceid)
            ec2.create_tags(Resources=ids,
                            Tags=[{'Key': 'Owner', 'Value': self.user}, {'Key': 'PrincipalId', 'Value': self.principal}])

    def tag_dynamodb(self):
        client = boto3.client('dynamodb')
        resource_arn = self.detail['responseElements']['tableDescription']['tableArn']
        tags = [{'Key': 'Owner', 'Value': self.user}, {'Key': 'PrincipalId', 'Value': self.principal}]
        client.tag_resource(ResourceArn=resource_arn, Tags=tags)

    def tag_lambda(self):
        # Lambda 的实际 API 与文档中并不一致, 其组成为 AIP 名字+版本
        client = boto3.client('lambda')

        # Lambda 函数的 arn
        function_arn = self.detail['responseElements']['functionArn']
        self.logger.info('function_arn: ' + function_arn)

        tag = {'Owner': self.user, 'PrincipalId': self.principal}
        client.tag_resource(Resource=function_arn, Tags=tag)

    def tag_rds(self):
        client = boto3.client('rds')
        resource_arn = self.detail['responseElements']['dBInstanceArn']

        tags = [{'Key': 'Owner', 'Value': self.user}, {'Key': 'PrincipalId', 'Value': self.principal}]
        client.add_tags_to_resource(ResourceName=resource_arn, Tags=tags)

    def tag_redshift(self):
        cluster_name = self.detail['requestParameters']['clusterIdentifier']
        client = boto3.client('redshift')

        # 在 API 中并没有提供获取 RedShift ARN 的方法, 需要自己手动拼接
        # 特别的, 中国区的 ARN 形如
        # arn:aws-cn:redshift:region:account-id:cluster:cluster-name
        # 拼接 arn
        account_id = self.event['account']
        region = self.event['region']
        resource_arn = "arn:aws-cn:redshift:" + str(region) + ":" + str(account_id) + ":cluster:" + cluster_name
        self.logger.info("RedShift arn: " + resource_arn)

        tags = [{'Key': 'Owner', 'Value': self.user}, {'Key': 'PrincipalId', 'Value': self.principal}]
        client.create_tags(ResourceName=resource_arn, Tags=tags)

    def tag_s3_object(self):
        s3 = boto3.client("s3")
        bucket_name = self.detail['requestParameters']['bucketName']
        object_name = self.detail['requestParameters']['key']

        tags = [{'Key': 'Owner', 'Value': self.user}, {'Key': 'PrincipalId', 'Value': self.principal}]
        s3.put_object_tagging(Bucket=bucket_name, Key=object_name, Tagging={'TagSet': tags})

    def tag_s3_bucket(self):
        s3 = boto3.client("s3")
        bucket_name = self.detail['requestParameters']['bucketName']

        tags = [{'Key': 'Owner', 'Value': self.user}, {'Key': 'PrincipalId', 'Value': self.principal}]
        s3.put_bucket_tagging(Bucket=bucket_name, Tagging={'TagSet': tags})

    def tag_sqs(self):
        client = boto3.client('sqs')
        queue_url = self.detail['responseElements']['queueUrl']

        tags = {'Owner': self.user, 'PrincipalId': self.principal}
        client.tag_queue(QueueUrl=queue_url, Tags=tags)

    def tag_vpc(self):
        vpc_id = self.detail['responseElements']['vpc']['vpcId']

        ec2 = boto3.resource('ec2')
        vpc = ec2.Vpc(vpc_id)

        tags = [{'Key': 'Owner', 'Value': self.user}, {'Key': 'PrincipalId', 'Value': self.principal}]
        vpc.create_tags(DryRun=False, Tags=tags)

