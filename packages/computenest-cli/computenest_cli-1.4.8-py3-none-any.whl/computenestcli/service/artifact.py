# -*- coding: utf-8 -*-
from Tea.exceptions import TeaException
from alibabacloud_computenestsupplier20210521 import models as compute_nest_supplier_20210521_models
from computenestcli.service.base import Service
from computenestcli.common.util import Util
from computenestcli.common import constant
from computenestcli.common.decorator import retry_on_exception


class ArtifactService(Service):

    @classmethod
    def create_artifact(cls, context, artifact_data, artifact_id=''):
        artifact_type = artifact_data.get(constant.ARTIFACT_TYPE)
        version_name = Util.add_timestamp_to_version_name(artifact_data.get(constant.VERSION_NAME))
        supported_regions = artifact_data.get(constant.SUPPORT_REGION_IDS)
        if artifact_type == constant.ECS_IMAGE:
            artifact_property = compute_nest_supplier_20210521_models.CreateArtifactRequestArtifactProperty(
                region_id=artifact_data.get(constant.ARTIFACT_PROPERTY).get(constant.REGION_ID),
                image_id=artifact_data.get(constant.ARTIFACT_PROPERTY).get(constant.IMAGE_ID)
            )
        elif artifact_type == constant.FILE:
            artifact_property = compute_nest_supplier_20210521_models.CreateArtifactRequestArtifactProperty(
                url=artifact_data.get(constant.ARTIFACT_PROPERTY).get(constant.URL)
            )
        elif artifact_type == constant.ACR_IMAGE or artifact_type == constant.HELM_CHART:
            repo_name = artifact_data[constant.ARTIFACT_NAME]
            repo_id = artifact_data[constant.ARTIFACT_PROPERTY][constant.REPO_ID]
            tag = artifact_data[constant.ARTIFACT_PROPERTY][constant.TAG]
            artifact_property = compute_nest_supplier_20210521_models.CreateArtifactRequestArtifactProperty(
                repo_name=repo_name,
                repo_id=repo_id,
                tag=tag
            )
        if artifact_id:
            create_artifact_request = compute_nest_supplier_20210521_models.CreateArtifactRequest(
                artifact_id=artifact_id,
                artifact_type=artifact_data.get(constant.ARTIFACT_TYPE),
                name=artifact_data.get(constant.ARTIFACT_NAME),
                version_name=version_name,
                description=artifact_data.get(constant.DESCRIPTION),
                artifact_property=artifact_property,
                support_region_ids=supported_regions
            )
        else:
            create_artifact_request = compute_nest_supplier_20210521_models.CreateArtifactRequest(
                artifact_type=artifact_data.get(constant.ARTIFACT_TYPE),
                name=artifact_data.get(constant.ARTIFACT_NAME),
                version_name=version_name,
                description=artifact_data.get(constant.DESCRIPTION),
                artifact_property=artifact_property,
                support_region_ids=supported_regions
            )
        client = cls._get_computenest_client(context)
        response = client.create_artifact(create_artifact_request)
        return response

    @classmethod
    @retry_on_exception(max_retries=10, delay=2, backoff=2, exceptions=(TeaException,))
    def release_artifact(cls, context, artifact_id):
        release_service_request = compute_nest_supplier_20210521_models.ReleaseArtifactRequest(artifact_id)
        client = cls._get_computenest_client(context)
        response = client.release_artifact(release_service_request)
        return response

    @classmethod
    def update_artifact(cls, context, artifact_data, artifact_id):
        artifact_type = artifact_data.get(constant.ARTIFACT_TYPE)
        version_name = Util.add_timestamp_to_version_name(artifact_data.get(constant.VERSION_NAME))
        supported_regions = artifact_data.get(constant.SUPPORT_REGION_IDS)
        if artifact_type == constant.ECS_IMAGE:
            artifact_property = compute_nest_supplier_20210521_models.UpdateArtifactRequestArtifactProperty(
                region_id=artifact_data.get(constant.ARTIFACT_PROPERTY).get(constant.REGION_ID),
                image_id=artifact_data.get(constant.ARTIFACT_PROPERTY).get(constant.IMAGE_ID)
            )
        elif artifact_type == constant.FILE:
            artifact_property = compute_nest_supplier_20210521_models.UpdateArtifactRequestArtifactProperty(
                url=artifact_data.get(constant.ARTIFACT_PROPERTY).get(constant.URL)
            )
        elif artifact_type == constant.ACR_IMAGE or artifact_type == constant.HELM_CHART:
            repo_name = artifact_data[constant.ARTIFACT_NAME]
            repo_id = artifact_data[constant.ARTIFACT_PROPERTY][constant.REPO_ID]
            tag = artifact_data[constant.ARTIFACT_PROPERTY][constant.TAG]
            artifact_property = compute_nest_supplier_20210521_models.CreateArtifactRequestArtifactProperty(
                repo_name=repo_name,
                repo_id=repo_id,
                tag=tag
            )
        update_artifact_request = compute_nest_supplier_20210521_models.UpdateArtifactRequest(
            artifact_id=artifact_id,
            version_name=version_name,
            description=artifact_data.get(constant.DESCRIPTION),
            artifact_property=artifact_property,
            support_region_ids=supported_regions
        )
        client = cls._get_computenest_client(context)
        response = client.update_artifact(update_artifact_request)
        return response

    @classmethod
    def delete_artifact(cls, context, artifact_id, artifact_version):
        delete_artifact_request = compute_nest_supplier_20210521_models.DeleteArtifactRequest(artifact_id,
                                                                                              artifact_version)
        client = cls._get_computenest_client(context)
        response = client.delete_artifact(delete_artifact_request)
        return response

    @classmethod
    def list_artifact(cls, context, artifact_name):
        filter_first = compute_nest_supplier_20210521_models.ListArtifactsRequestFilter(
            name=constant.NAME,
            values=[artifact_name]
        )
        list_artifact_request = compute_nest_supplier_20210521_models.ListArtifactsRequest(
            filter=[
                filter_first
            ]
        )
        client = cls._get_computenest_client(context)
        response = client.list_artifacts(list_artifact_request)
        return response

    @classmethod
    @retry_on_exception()
    def list_acr_image_repositories(cls, context, artifact_type, repo_name):
        print("list_acr_image_repositories artifact_type: %s repo_name: %s" % (artifact_type, repo_name))
        list_acr_image_repositories_request = compute_nest_supplier_20210521_models.ListAcrImageRepositoriesRequest(
            artifact_type=artifact_type,
            repo_name=repo_name
        )
        client = cls._get_computenest_client(context)
        response = client.list_acr_image_repositories(list_acr_image_repositories_request)
        print("list_acr_image_repositories response: %s" % response)
        # 如果body不为空，且repositories数组为空的话就抛出异常
        if response.body and not response.body.repositories:
            raise Exception("No repositories found")
        return response

    @classmethod
    @retry_on_exception()
    def list_acr_image_tags(cls, context, repo_id, artifact_type):
        list_acr_image_tags_request = compute_nest_supplier_20210521_models.ListAcrImageTagsRequest(
            repo_id=repo_id,
            artifact_type=artifact_type
        )
        client = cls._get_computenest_client(context)
        response = client.list_acr_image_tags(list_acr_image_tags_request)
        print("list_acr_image_tags response: %s" % response)
        if response.body and not response.body.images:
            raise Exception("No tags found")
        return response

    @classmethod
    def get_artifact(cls, context, artifact_name, artifact_version='', artifact_id=''):
        get_artifact_request = compute_nest_supplier_20210521_models.GetArtifactRequest(
            artifact_version=artifact_version,
            artifact_name=artifact_name,
            artifact_id=artifact_id,
        )
        client = cls._get_computenest_client(context)
        response = client.get_artifact(get_artifact_request)
        return response

    @classmethod
    def list_versions(cls, context, artifact_id):
        list_artifact_versions_request = compute_nest_supplier_20210521_models.ListArtifactVersionsRequest(artifact_id)
        client = cls._get_computenest_client(context)
        response = client.list_artifact_versions(list_artifact_versions_request)
        return response
