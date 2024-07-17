# -*- coding: utf-8 -*-
from alibabacloud_oos20190601.client import Client as oos20190601Client
from computenestcli.client.base import BaseClient


class OosClient(BaseClient):
    def __init__(self, context):
        super().__init__(context.region_id,
                         context.credentials.access_key_id,
                         context.credentials.access_key_secret)

    def create_client_oos(self):
        self.config.endpoint = f'oos.{self.region_id}.aliyuncs.com'
        return oos20190601Client(self.config)