import yaml
import os
from computenestcli.common import constant
from computenestcli.common.util import Util


class CheckProcesser:
    def __init__(self, config, file_path):
        self.config = config
        self.file_path = file_path
        self.checks = [self.validate_allowed_regions, self.validate_image_key]
        self.errors = []

    def validate_allowed_regions(self):
        support_regions = []
        if constant.ARTIFACT not in self.config:
            return True
        deploy_metadata = self.config[constant.SERVICE][constant.DEPLOY_METADATA]
        if self.config[constant.SERVICE][constant.SERVICE_TYPE] == constant.MANAGED:
            template_configs = deploy_metadata[constant.SUPPLIER_DEPLOY_METADATA][constant.SUPPLIER_TEMPLATE_CONFIGS]
        else:
            template_configs = deploy_metadata[constant.TEMPLATE_CONFIGS]

        for artifact in self.config[constant.ARTIFACT]:
            if self.config[constant.ARTIFACT][artifact][constant.ARTIFACT_TYPE] == constant.ECS_IMAGE:
                support_regions.extend(self.config[constant.ARTIFACT][artifact][constant.SUPPORT_REGION_IDS])
                for config in template_configs:
                    allowed_regions = config[constant.ALLOWED_REGIONS]
                    if set(allowed_regions).issubset(set(support_regions)):
                        continue
                    else:
                        self.errors.append("The AllowedRegions in TemplateConfigs are beyond the scope of SupportRegionIds in Artifact.")
                        return False
        return True

    def validate_image_key(self):
        deploy_metadata = self.config[constant.SERVICE][constant.DEPLOY_METADATA]

        if self.config[constant.SERVICE][constant.SERVICE_TYPE] == constant.MANAGED:
            template_configs = deploy_metadata[constant.SUPPLIER_DEPLOY_METADATA][constant.SUPPLIER_TEMPLATE_CONFIGS]
        else:
            template_configs = deploy_metadata[constant.TEMPLATE_CONFIGS]

        for template in template_configs:
            # 将相对路径替换成绝对路径
            template_path = os.path.join(os.path.dirname(self.file_path), template.get(constant.URL))
            template = self.read_yaml_file(template_path)
            template_image_ids = self.get_image_ids(template)
            supplier_deploy_metadata = deploy_metadata.get(constant.SUPPLIER_DEPLOY_METADATA, None)
            if supplier_deploy_metadata is None:
                return True
            if constant.ARTIFACT_RELATION not in supplier_deploy_metadata:
                return True
            config_image_ids = set(self.config[constant.SERVICE][constant.DEPLOY_METADATA][
                                       constant.SUPPLIER_DEPLOY_METADATA][constant.ARTIFACT_RELATION].keys())
            if not config_image_ids.issubset(template_image_ids):
                self.errors.append("The ImageId in template.yaml does not match the image identifier in config.yaml.")
                return False
        return True

    @staticmethod
    def read_yaml_file(file):
        with open(file, 'r') as f:
            return yaml.safe_load(f)

    @staticmethod
    def get_image_ids(template):
        image_ids = set()
        CheckProcesser.search_image_ids(template, image_ids)
        return image_ids

    @staticmethod
    def search_image_ids(obj, image_ids):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key == constant.IMAGE_ID:
                    image_ids.add(value)
                else:
                    CheckProcesser.search_image_ids(value, image_ids)
        elif isinstance(obj, list):
            for item in obj:
                CheckProcesser.search_image_ids(item, image_ids)
        return image_ids

    def run_checks(self):
        for check_func in self.checks:
            if not check_func():
                return False
        return True

    def print_errors(self):
        if self.errors:
            for error in self.errors:
                print(error)
                raise ValueError(f"YAML file parameters are incorrect. Please modify and try again.\nThe error message: {error}")
        else:
            print("Config is valid.")

    def processor(self):
        if self.run_checks():
            current_time = Util.get_current_time()
            print("===========================")
            print("Validation check: The config.yaml is correct!")
            print("Completion time: ", current_time)
            print("===========================")
        else:
            self.print_errors()


