# -*- coding: utf-8 -*-
from computenestcli.client.base import BaseClient
from alibabacloud_ecs20140526.client import Client as Ecs20140526Client


class EcsClient(BaseClient):
    def __init__(self, context):
        super().__init__(context.region_id,
                         context.credentials.access_key_id,
                         context.credentials.access_key_secret)

    def create_client_ecs(self):
        self.config.endpoint = f'ecs.{self.region_id}.aliyuncs.com'
        return Ecs20140526Client(self.config)