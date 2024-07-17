# -*- coding: utf-8 -*-
import json

from alibabacloud_oos20190601 import models as oos_20190601_models
from computenestcli.common import constant
from alibabacloud_ecs20140526 import models as ecs_20140526_models
from computenestcli.common.decorator import retry_on_exception
from computenestcli.service.base import Service

ACS_ECS_UPDATE_IMAGE = 'ACS-ECS-UpdateImage'
ZONE = 'Zone'
INSTANCE_TYPE = 'instanceType'


class ImageService(Service):

    @classmethod
    def describe_available_resource(cls, context, instance_type):
        client = cls._get_ecs_client(context)
        describe_available_resource_request = ecs_20140526_models.DescribeAvailableResourceRequest(
            region_id=context.region_id,
            destination_resource=ZONE,
            instance_type=instance_type
        )
        response = client.describe_available_resource(describe_available_resource_request)
        return response

    @classmethod
    def get_available_zone_id(cls, context, instance_type):
        response = cls.describe_available_resource(context, instance_type)
        zone_id = response.body.available_zones.available_zone[0].zone_id
        return zone_id

    @classmethod
    def start_update_Image_execution(cls, context, image_data):

        instance_type = image_data.get(INSTANCE_TYPE)
        # 根据用户提供的实例类型和地域选择合适的可用区
        zone_id = cls.get_available_zone_id(context, instance_type)
        image_data[constant.ZONE_ID] = zone_id
        # 默认用户选择新建vpc，无需用户指定vpc/vswitch
        image_data[constant.WHETHER_CREATE_VPC] = True
        image_data[constant.OOS_ASSUME_ROLE] = ""
        json_data = json.dumps(image_data)
        start_execution_request = oos_20190601_models.StartExecutionRequest(
            region_id=context.region_id,
            template_name=ACS_ECS_UPDATE_IMAGE,
            parameters=json_data
        )
        response = cls._get_oos_client(context).start_execution(start_execution_request)
        execution_id = response.body.execution.execution_id

        return execution_id

    @classmethod
    @retry_on_exception()
    def list_execution(cls, context, execution_id):
        list_execution_request = oos_20190601_models.ListExecutionsRequest(execution_id=execution_id)
        response = cls._get_oos_client(context).list_executions(list_execution_request)
        print("list_oos_execution execution_id: %s, response: %s" % (execution_id, response))
        return response

    @classmethod
    def list_task_executions(cls, context, execution_id):
        list_task_executions_request = oos_20190601_models.ListTaskExecutionsRequest(
            region_id=context.region_id,
            execution_id=execution_id
        )
        response = cls._get_oos_client(context).list_task_executions(list_task_executions_request)
        return response

    @classmethod
    def list_execution_logs(cls, context, execution_id):
        list_execution_logs_request = oos_20190601_models.ListExecutionLogsRequest(
            region_id=context.region_id,
            execution_id=execution_id
        )
        response = cls._get_oos_client(context).list_execution_logs(list_execution_logs_request)
        return response
