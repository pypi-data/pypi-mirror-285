# -*- coding: utf-8 -*-
from alibabacloud_computenestsupplier20210521.client import Client as ComputeNestSupplier20210521Client
from computenestcli.client.base import BaseClient
from computenestcli.common.constant import AP_SOUTHEAST_1


class ComputeNestClient(BaseClient):

    def __init__(self, context):
        super().__init__(context.region_id,
                         context.credentials.access_key_id,
                         context.credentials.access_key_secret,
                         context.credentials.security_token)

    def create_client_compute_nest(self):
        if self.region_id == AP_SOUTHEAST_1:
            self.config.endpoint = f'computenestsupplier.ap-southeast-1.aliyuncs.com'
        else:
            self.config.endpoint = f'computenestsupplier.cn-hangzhou.aliyuncs.com'

        return ComputeNestSupplier20210521Client(self.config)