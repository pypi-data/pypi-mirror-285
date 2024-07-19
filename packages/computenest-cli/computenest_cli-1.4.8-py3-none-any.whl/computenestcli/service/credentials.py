# -*- coding: utf-8 -*-
from alibabacloud_computenestsupplier20210521 import models as compute_nest_supplier_20210521_models

from computenestcli.common import constant
from computenestcli.service.base import Service


class CredentialsService(Service):

    @classmethod
    def get_upload_credentials(cls, context, file_name):
        get_upload_credentials_request = compute_nest_supplier_20210521_models. \
            GetUploadCredentialsRequest(file_name, constant.GET_UPDATE_OSS_PUBLIC_CREDENTIALS)
        client = cls._get_computenest_client(context)
        response = client.get_upload_credentials(get_upload_credentials_request)
        return response

    @classmethod
    def get_artifact_repository_credentials(cls, context, artifact_type):
        client = cls._get_computenest_client(context)
        get_artifact_repository_credentials = compute_nest_supplier_20210521_models.GetArtifactRepositoryCredentialsRequest(
            artifact_type, context.region_id)
        response = client.get_artifact_repository_credentials(get_artifact_repository_credentials)
        return response
