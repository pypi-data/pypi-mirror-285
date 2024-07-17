import os
import sys
import json
from ruamel.yaml import YAML
from Tea.exceptions import TeaException
from computenestcli.service.supplier import SupplierService
from computenestcli.common import constant
from computenestcli.common.util import Util
from computenestcli.processor.artifact import ArtifactProcessor
from computenestcli.service.file import FileService
from computenestcli.service.credentials import CredentialsService

FILE = 'file'
DRAFT = 'draft'
SERVICE_NOT_FOUND = 'EntityNotExist.Service'
CUSTOM_OPERATIONS = 'CustomOperations'
ACTIONS = 'Actions'
TEMPLATE_URL = 'TemplateUrl'
SHARE_TYPE = 'ShareType'
APPROVAL_TYPE = 'ApprovalType'
ALWAYS_LATEST = 'AlwaysLatest'
SECURITY_GROUPS = 'SecurityGroups'
HIDDEN_PARAMETER_KEYS = 'HiddenParameterKeys'
PREDEFINED_PARAMETERS = 'PredefinedParameters'
NETWORK_METADATA = 'NetworkMetadata'
DEPLOY_TIME_OUT = 'DeployTimeout'
UPDATE_INFO = 'UpdateInfo'


class ServiceProcessor:

    def __init__(self, context):
        self.context = context

    def _get_service_logo_url(self, service_name):
        data_list_service = SupplierService.list_service(self.context, service_name)
        service_id = data_list_service.body.services[0].service_id
        service_version = data_list_service.body.services[0].version
        data_get_service = SupplierService.get_service(self.context, service_id, service_version)
        url = data_get_service.body.service_infos[0].image
        return url

    def _get_template_url_data(self, service_name):
        data_list_service = SupplierService.list_service(self.context, service_name)
        service_id = data_list_service.body.services[0].service_id
        service_version = data_list_service.body.services[0].version
        data_get_service = SupplierService.get_service(self.context, service_id, service_version)
        deploy_metadata = data_get_service.body.deploy_metadata
        return deploy_metadata

    def _replace_artifact_data(self, artifact_relations, data_artifact):
        for artifact_info in artifact_relations.values():
            id_file = artifact_info.get(constant.ARTIFACT_ID)
            version_file = artifact_info.get(constant.ARTIFACT_VERSION)
            id_match = Util.regular_expression(id_file)
            # 将占位符${Artifact.Artifact_x.ArtifactId}解析并输出dict
            version_match = Util.regular_expression(version_file)
            artifact_id_file = data_artifact.get(id_match[1]).get(id_match[2])
            # [0][1][2]为刚才解析出得占位符的分解，即Artifact，Artifact_x，ArtifactId
            artifact_version_file = data_artifact.get(version_match[1]).get(version_match[2])
            artifact_info[constant.ARTIFACT_ID] = artifact_id_file
            artifact_info[constant.ARTIFACT_VERSION] = artifact_version_file

    def _replace_file_path_with_url(self, file_path):
        file_name = os.path.basename(file_path)
        data_file = CredentialsService.get_upload_credentials(self.context, file_name)
        file_url = FileService.put_file(data_file, file_path, FILE)
        return file_url

    def _replace_parameters(self, content, parameters):
        new_content = content
        if isinstance(content, dict):
            new_content = {}
            for key, value in content.items():
                new_key = self._replace_parameters(key, parameters)
                new_value = self._replace_parameters(value, parameters)
                new_content[new_key] = new_value
        elif isinstance(content, list):
            new_content = []
            for value in content:
                new_value = self._replace_parameters(value, parameters)
                new_content.append(new_value)
        elif isinstance(content, str):
            parameter_match = Util.regular_expression(content)
            if parameter_match and len(parameter_match) == 1 and parameter_match[0] in parameters:
                new_content = parameters.get(parameter_match[0])
            else:
                new_content = content
        elif isinstance(content, bool):
            new_content = content
        return new_content

    def _delete_field(self, data, field):
        if isinstance(data, dict):
            for key in list(data.keys()):
                if key == field:
                    del data[key]
                else:
                    self._delete_field(data[key], field)
        elif isinstance(data, list):
            for item in data:
                self._delete_field(item, field)

    def _get_service_detail(self, region_id, service_name):
        response = SupplierService.list_service(self.context, service_name)
        if len(response.body.services) == 0:
            print("Service does not exist, please check the region_id and service_name")
            sys.exit(1)
        service_id = response.body.services[0].service_id
        version = response.body.services[0].version
        data = SupplierService.get_service(self.context, service_id, version)
        deploy_metadata = json.loads(data.body.deploy_metadata)
        approval_type = data.body.approval_type
        share_type = data.body.share_type
        service_type = data.body.service_type
        deploy_type = data.body.deploy_type
        # self._delete_field(deploy_metadata, NETWORK_METADATA)
        # self._delete_field(deploy_metadata, DEPLOY_TIME_OUT)
        self._delete_field(deploy_metadata, ALWAYS_LATEST)
        for config in deploy_metadata[constant.TEMPLATE_CONFIGS]:
            self._delete_field(config, SECURITY_GROUPS)
            # self._delete_field(config, HIDDEN_PARAMETER_KEYS)
            # self._delete_field(config, PREDEFINED_PARAMETERS)
            self._delete_field(config, UPDATE_INFO)
        service_info_pre = data.body.service_infos[0]
        image = service_info_pre.image
        name = service_info_pre.name
        locale = service_info_pre.locale
        short_description = service_info_pre.short_description
        service_info = {
            constant.LOCALE: locale,
            constant.SHORT_DESCRIPTION: short_description,
            constant.IMAGE: image,
            constant.NAME: name
        }
        parameters = {
            constant.REGION_ID: region_id,
            constant.DEPLOY_TYPE: deploy_type,
            constant.DEPLOY_METADATA: deploy_metadata,
            constant.SERVICE_TYPE: service_type,
            constant.SERVICE_INFO: service_info,
            constant.SHARE_TYPE: share_type,
            constant.APPROVAL_TYPE: approval_type
        }

        service = {
            constant.SERVICE: parameters
        }
        return service, deploy_metadata

    @Util.measure_time
    def import_command(self, data_config, file_path, update_artifact, service_name='', version_name='',
                       icon='', desc='', parameters={}):
        if parameters:
            data_config = self._replace_parameters(data_config, parameters)
        service_config = data_config[constant.SERVICE]
        deploy_metadata_config = service_config[constant.DEPLOY_METADATA]
        if data_config.get(constant.ARTIFACT):
            artifact_processor = ArtifactProcessor(self.context)
            data_artifact = artifact_processor.process(data_config, file_path, update_artifact, version_name)
            # 遍历部署物关联映射，进行部署物替换
            support_artifact_relation_types = [constant.ARTIFACT_RELATION, constant.FILE_ARTIFACT_RELATION,
                                               constant.ACR_IMAGE_ARTIFACT_RELATION,
                                               constant.HELM_CHART_ARTIFACT_RELATION]
            for relation_type, artifact_relations in \
                    deploy_metadata_config.get(constant.SUPPLIER_DEPLOY_METADATA, {}).items():
                if relation_type in support_artifact_relation_types:
                    self._replace_artifact_data(artifact_relations, data_artifact)
        if service_name:
            # 如果有service_name传入，那么覆盖yaml文件中的服务名称
            service_config[constant.SERVICE_INFO][constant.NAME] = service_name
        if version_name:
            service_config[constant.VERSION_NAME] = version_name
        if desc:
            service_config[constant.SERVICE_INFO][constant.SHORT_DESCRIPTION] = desc
        service_name = service_config.get(constant.SERVICE_INFO).get(constant.NAME)
        data_list = SupplierService.list_service(self.context, service_name)
        # 将相对路径替换成绝对路径
        image_path = os.path.join(os.path.dirname(file_path),
                                  service_config.get(constant.SERVICE_INFO).get(constant.IMAGE))
        if service_config.get(constant.OPERATION_METADATA):
            # 判断CUSTOM_OPERATIONS是否存在
            if CUSTOM_OPERATIONS in service_config[constant.OPERATION_METADATA]:
                for operation_template in service_config[constant.OPERATION_METADATA][CUSTOM_OPERATIONS][ACTIONS]:
                    # 将相对路径替换成绝对路径
                    operation_template_path = os.path.join(os.path.dirname(file_path),
                                                           operation_template.get(TEMPLATE_URL))
                    operation_template[TEMPLATE_URL] = self._replace_file_path_with_url(operation_template_path)
        # 将部署物的id和version替换成正确的值
        if len(data_list.body.services) == 0:
            if icon:
                service_config[constant.SERVICE_INFO][constant.IMAGE] = icon
            else:
                # 将服务logo的本地路径替换成Url
                service_config[constant.SERVICE_INFO][constant.IMAGE] = self._replace_file_path_with_url(image_path)
            # 将模版文件的本地路径替换成url
            if deploy_metadata_config.get(constant.TEMPLATE_CONFIGS):
                for template in deploy_metadata_config.get(constant.TEMPLATE_CONFIGS):
                    # 将相对路径替换成绝对路径
                    if template.get(constant.URL):
                        template_path = os.path.join(os.path.dirname(file_path), template.get(constant.URL))
                        template[constant.URL] = self._replace_file_path_with_url(template_path)
            # 将SupplierDeployMetadata的路径做替换
            if constant.SUPPLIER_DEPLOY_METADATA in deploy_metadata_config:
                supplier_deploy_metadata = deploy_metadata_config.get(constant.SUPPLIER_DEPLOY_METADATA)
                if constant.SUPPLIER_TEMPLATE_CONFIGS in supplier_deploy_metadata:
                    for supplier_template_config in supplier_deploy_metadata.get(constant.SUPPLIER_TEMPLATE_CONFIGS):
                        template_path = os.path.join(os.path.dirname(file_path),
                                                     supplier_template_config.get(constant.URL))
                        supplier_template_config[constant.URL] = self._replace_file_path_with_url(template_path)
            create_service_instance_result = SupplierService.create_service(self.context, service_config)
            service_id = create_service_instance_result.body.service_id
            current_time = Util.get_current_time()
            print("===========================")
            print("Successfully created a new service!")
            print("The service name:", service_name)
            print("The service id:", service_id)
            print("Completion time:", current_time)
            print("===========================")
        else:
            service_id = data_list.body.services[0].service_id
            if icon:
                service_config[constant.SERVICE_INFO][constant.IMAGE] = icon
            else:
                image_url_existed = self._get_service_logo_url(service_name)
                result_image = FileService.check_file_repeat(image_url_existed, image_path)
                # 检查服务logo是否重复，重复则不再上传，直接使用原有Url
                if result_image:
                    image_url = image_url_existed
                else:
                    image_url = self._replace_file_path_with_url(image_path)
                service_config[constant.SERVICE_INFO][constant.IMAGE] = image_url

            service_deploy_metadata = json.loads(self._get_template_url_data(service_name))
            if service_deploy_metadata and service_deploy_metadata.get(constant.TEMPLATE_CONFIGS) and \
                    service_config.get(constant.DEPLOY_METADATA).get(constant.TEMPLATE_CONFIGS):
                name_url_mapping = {template[constant.NAME]: template[constant.URL] for template in
                                    service_deploy_metadata.get(constant.TEMPLATE_CONFIGS)}
                # 检查模版文件是否重复，重复则不再上传，直接使用原有Url
                for template in service_config[constant.DEPLOY_METADATA][constant.TEMPLATE_CONFIGS]:
                    if template[constant.NAME] in name_url_mapping:
                        # 将相对路径替换成绝对路径
                        template_path = os.path.join(os.path.dirname(file_path), template.get(constant.URL))
                        result_template = FileService.check_file_repeat(name_url_mapping[template[constant.NAME]],
                                                                        template_path)
                        if result_template:
                            template[constant.URL] = name_url_mapping.get(template[constant.NAME])
                        else:
                            template[constant.URL] = self._replace_file_path_with_url(template_path)
                    else:
                        if template.get(constant.URL):
                            template_path = os.path.join(os.path.dirname(file_path), template.get(constant.URL))
                            template[constant.URL] = self._replace_file_path_with_url(template_path)
            elif deploy_metadata_config.get(constant.TEMPLATE_CONFIGS):
                for template in deploy_metadata_config.get(constant.TEMPLATE_CONFIGS):
                    # 将相对路径替换成绝对路径
                    if template.get(constant.URL):
                        template_path = os.path.join(os.path.dirname(file_path), template.get(constant.URL))
                        template[constant.URL] = self._replace_file_path_with_url(template_path)

            # 将SupplierDeployMetadata的路径做替换
            if constant.SUPPLIER_DEPLOY_METADATA in deploy_metadata_config:
                supplier_deploy_metadata = deploy_metadata_config.get(constant.SUPPLIER_DEPLOY_METADATA)
                # 已存在的服务的supplier_template_configs
                service_supplier_template_configs = service_deploy_metadata.get(constant.SUPPLIER_TEMPLATE_CONFIGS)
                if service_supplier_template_configs:
                    name_url_mapping = {template[constant.NAME]: template[constant.URL] for template in
                                        service_supplier_template_configs}
                    for supplier_template_config in supplier_deploy_metadata.get(constant.SUPPLIER_TEMPLATE_CONFIGS):
                        if supplier_template_config[constant.NAME] in name_url_mapping:
                            template_path = os.path.join(os.path.dirname(file_path),
                                                         supplier_template_config.get(constant.URL))
                            result_template = FileService.check_file_repeat(
                                name_url_mapping[supplier_template_config[constant.NAME]],
                                template_path)
                            if result_template:
                                supplier_template_config[constant.URL] = name_url_mapping.get(
                                    supplier_template_config[constant.NAME])
                            else:
                                supplier_template_config[constant.URL] = self._replace_file_path_with_url(
                                    template_path)
                        else:
                            supplier_template_config[constant.URL] = self._replace_file_path_with_url(
                                template_path)
                else:
                    # 已有服务中没有对应的SUPPLIER_TEMPLATE_CONFIGS
                    if supplier_deploy_metadata and constant.SUPPLIER_TEMPLATE_CONFIGS in supplier_deploy_metadata:
                        for supplier_template_config in supplier_deploy_metadata.get(
                                constant.SUPPLIER_TEMPLATE_CONFIGS):
                            template_path = os.path.join(os.path.dirname(file_path),
                                                         supplier_template_config.get(constant.URL))
                            supplier_template_config[constant.URL] = self._replace_file_path_with_url(template_path)

            # 状态为Draft或者Creating时，更新服务
            service_status = data_list.body.services[0].status
            if service_status == 'Draft' or service_status == 'Creating':
                SupplierService.update_service(self.context, service_config, service_id)
                service_name = service_config.get(constant.SERVICE_INFO).get(constant.NAME)
                current_time = Util.get_current_time()
                print("===========================")
                print("Successfully updated the service!")
                print("The service name: ", service_name)
                print("The service id: ", service_id)
                print("Completion time: ", current_time)
                print("===========================")
            else:
                service_id = data_list.body.services[0].service_id
                try:
                    SupplierService.get_service(self.context, service_id, DRAFT)
                except TeaException as e:
                    if e.code == SERVICE_NOT_FOUND:
                        SupplierService.create_service(self.context, service_config, service_id)
                    else:
                        raise
                else:
                    SupplierService.update_service(self.context, service_config, service_id)
                current_time = Util.get_current_time()
                print("===========================")
                print("Successfully updated the service!")
                print("The service name: ", service_name)
                print("The service id: ", service_id)
                print("Completion time: ", current_time)
                print("===========================")

    def export_command(self, service_name, file_path, parameters):
        artifact = ArtifactProcessor(self.context)
        data_yaml, deploy_metadata = self._get_service_detail(self.context.region_id, service_name)
        supplier_deploy_metadata = deploy_metadata[constant.SUPPLIER_DEPLOY_METADATA]
        if data_yaml[constant.SERVICE][constant.DEPLOY_METADATA][constant.SUPPLIER_DEPLOY_METADATA]:
            data_yaml.setdefault(constant.ARTIFACT, {})
            i = 1
            for artifact_metadata in supplier_deploy_metadata:
                if artifact_metadata == constant.ARTIFACT_RELATION:
                    relation = constant.ARTIFACT_RELATION
                elif artifact_metadata == constant.HELM_CHART_ARTIFACT_RELATION:
                    relation = constant.HELM_CHART_ARTIFACT_RELATION
                elif artifact_metadata == constant.FILE_ARTIFACT_RELATION:
                    relation = constant.FILE_ARTIFACT_RELATION
                elif artifact_metadata == constant.ACR_IMAGE_ARTIFACT_RELATION:
                    relation = constant.ACR_IMAGE_ARTIFACT_RELATION
                for image_key in \
                        data_yaml[constant.SERVICE][constant.DEPLOY_METADATA][constant.SUPPLIER_DEPLOY_METADATA][
                            relation]:
                    artifact_key = constant.ARTIFACT + '_' + str(i)
                    i += 1
                    artifact_id = \
                        data_yaml[constant.SERVICE][constant.DEPLOY_METADATA][constant.SUPPLIER_DEPLOY_METADATA][
                            relation][
                            image_key][constant.ARTIFACT_ID]
                    data_yaml = artifact.get_artifact_detail(artifact_id, data_yaml, artifact_key)
        yaml = YAML(typ='rt')
        yaml.indent(mapping=2, sequence=4, offset=2)
        yaml.width = 180
        with open(file_path, "w") as file:
            yaml.dump(data_yaml, file)
        print("===========================")
        print("Successfully export the config.yaml!")
        print("The file path: \n", file_path)
        print("===========================")
