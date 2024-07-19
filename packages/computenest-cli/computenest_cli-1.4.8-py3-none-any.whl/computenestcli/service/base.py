from computenestcli.client.computenest import ComputeNestClient
from computenestcli.client.oos import OosClient
from computenestcli.client.ecs import EcsClient


class Service:

    @classmethod
    def _get_computenest_client(cls, context):
        client = ComputeNestClient(context)
        return client.create_client_compute_nest()

    @classmethod
    def _get_ecs_client(cls, context):
        client = EcsClient(context)
        return client.create_client_ecs()

    @classmethod
    def _get_oos_client(cls, context):
        client = OosClient(context)
        return client.create_client_oos()