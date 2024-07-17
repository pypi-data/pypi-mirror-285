import os
import re
import shutil
import tempfile

from pathlib import Path
from importlib import resources
from computenestcli.processor.jinja2 import Jinja2Processor
from computenestcli.common import project_setup_constant
from computenestcli.common.artifact_source_type import ArtifactSourceType
from computenestcli.common.arch import Arch
from computenestcli.common.service_type import ServiceType


class ProjectSetup:
    def __init__(self, output_base_path, parameters):
        self.output_base_path = Path(output_base_path).absolute()
        # 检查将Parameters中的RepoName，并修改为符合正则表达式的RepoName
        repo_name = parameters.get(project_setup_constant.REPO_NAME_KEY)
        if not repo_name:
            repo_name = project_setup_constant.APP_NAME
        else:
            repo_name = self._sanitize_name(repo_name)
        parameters[project_setup_constant.REPO_NAME_KEY] = repo_name
        self.parameters = parameters
        self.processor = Jinja2Processor()

    def setup_project(self):
        print("Setting up the project...")
        self._validate_parameters()
        self._handle_source_code_packaging()
        self._render_templates()
        self._copy_resources()
        print("Project setup complete.")

    def _validate_parameters(self):
        print("Validating parameters...")
        artifact_source_type = self.parameters.get(project_setup_constant.ARTIFACT_SOURCE_TYPE_KEY)
        if artifact_source_type not in [ArtifactSourceType.SOURCE_CODE.value, ArtifactSourceType.INSTALL_PACKAGE.value,
                                        ArtifactSourceType.DOCKERFILE.value, ArtifactSourceType.HELM_CHART.value,
                                        ArtifactSourceType.DOCKER_COMPOSE.value]:
            raise Exception("Invalid artifact source type.")
        if artifact_source_type == ArtifactSourceType.SOURCE_CODE.value:
            source_code_path = self.parameters.get(project_setup_constant.SOURCE_CODE_PATH_KEY)
            if not source_code_path:
                raise Exception("Source code path is empty.")
            if not os.path.exists(source_code_path):
                raise Exception(f"Source code path:{source_code_path} does not exist.")
        if artifact_source_type == ArtifactSourceType.INSTALL_PACKAGE.value:
            package_path = self.parameters.get(project_setup_constant.PACKAGE_PATH_KEY)
            if not package_path:
                raise Exception("Package path is empty.")
            if not os.path.exists(package_path):
                raise Exception(f"Package path:{package_path} does not exist.")
            if not os.path.isfile(package_path):
                raise Exception(f"Package path:{package_path} is not a file.")
        if artifact_source_type == ArtifactSourceType.DOCKERFILE.value:
            dockerfile_path = self.parameters.get(project_setup_constant.DOCKERFILE_PATH_KEY)
            if not dockerfile_path:
                raise Exception("Dockerfile path is empty.")
            if not os.path.exists(dockerfile_path):
                raise Exception(f"Dockerfile path:{dockerfile_path} does not exist.")
        if artifact_source_type == ArtifactSourceType.DOCKER_COMPOSE.value:
            docker_compose_path = self.parameters.get(project_setup_constant.DOCKER_COMPOSE_PATH_KEY)
            if not docker_compose_path:
                raise Exception("Docker compose path is empty.")
            if not os.path.exists(docker_compose_path):
                raise Exception(f"Docker compose path:{docker_compose_path} does not exist.")

    def _create_directories(self):
        print("Creating necessary directories...")
        necessary_dirs = [project_setup_constant.OUTPUT_DOCS_DIR,
                          project_setup_constant.OUTPUT_ROS_TEMPLATE_DIR,
                          project_setup_constant.OUTPUT_ICON_DIR]

        for directory in necessary_dirs:
            Path(self.output_base_path, directory).mkdir(parents=True, exist_ok=True)

        artifact_source_type = self.parameters.get(project_setup_constant.ARTIFACT_SOURCE_TYPE_KEY)

        # 创建特定于软件形态的目录
        map_artifact_to_dir = {
            ArtifactSourceType.INSTALL_PACKAGE.value: project_setup_constant.OUTPUT_PACKAGE_DIR,
            ArtifactSourceType.SOURCE_CODE.value: project_setup_constant.OUTPUT_PACKAGE_DIR,
            ArtifactSourceType.DOCKERFILE.value: project_setup_constant.OUTPUT_DOCKERFILE_DIR,
            ArtifactSourceType.DOCKER_COMPOSE.value: project_setup_constant.OUTPUT_DOCKER_COMPOSE_DIR,
            ArtifactSourceType.HELM_CHART.value: project_setup_constant.OUTPUT_HELM_CHART_DIR
        }

        if artifact_source_type in map_artifact_to_dir:
            Path(self.output_base_path, map_artifact_to_dir[artifact_source_type]).mkdir(parents=True, exist_ok=True)
            print(f"Created {map_artifact_to_dir[artifact_source_type]} directory at {self.output_base_path}.")

    def _render_templates(self):
        print("Rendering templates...")
        self._create_directories()
        artifact_source_type = self.parameters.get(project_setup_constant.ARTIFACT_SOURCE_TYPE_KEY)
        architecture = self.parameters.get(project_setup_constant.ARCHITECTURE_KEY)
        print(f"Artifact source type: {artifact_source_type}")

        template_paths = {
            ArtifactSourceType.SOURCE_CODE.value: (
                project_setup_constant.INPUT_SOURCE_CODE_ROS_TEMPLATE_NAME,
                project_setup_constant.INPUT_SOURCE_CODE_CONFIG_NAME
            ),
            ArtifactSourceType.INSTALL_PACKAGE.value: (
                project_setup_constant.INPUT_INSTALL_PACKAGE_ROS_TEMPLATE_NAME,
                project_setup_constant.INPUT_INSTALL_PACKAGE_CONFIG_NAME
            ),
            ArtifactSourceType.DOCKERFILE.value: (
                project_setup_constant.INPUT_DOCKERFILE_ROS_TEMPLATE_NAME,
                project_setup_constant.INPUT_DOCKERFILE_CONFIG_NAME
            ),
            ArtifactSourceType.DOCKER_COMPOSE.value: (
                project_setup_constant.INPUT_DOCKER_COMPOSE_ROS_TEMPLATE_NAME,
                project_setup_constant.INPUT_DOCKER_COMPOSE_CONFIG_NAME
            ),
            ArtifactSourceType.HELM_CHART.value: (
                project_setup_constant.INPUT_HELM_CHART_ROS_TEMPLATE_NAME,
                project_setup_constant.INPUT_HELM_CHART_CONFIG_NAME
            ),
        }

        if artifact_source_type in template_paths:
            input_ros_template_name, input_config_name = template_paths[artifact_source_type]
            print(f"Rendering templates for {artifact_source_type}...")
        else:
            raise Exception("Invalid artifact source type.")

        # 根据架构选择不同的模板所在的包
        if Arch.ECS_SINGLE.value == architecture:
            package_name = project_setup_constant.INPUT_ROS_TEMPLATE_ECS_SINGLE_PATH
        elif Arch.ECS_CLUSTER.value == architecture:
            package_name = project_setup_constant.INPUT_ROS_TEMPLATE_ECS_CLUSTER_PATH
        else:
            # 目前仅支持单节点和集群版（可弹性伸缩）架构
            raise Exception("Invalid architecture.")

        # 处理 docker-compose 的情况
        if artifact_source_type == ArtifactSourceType.DOCKER_COMPOSE.value:
            docker_compose_path = self.parameters.get(project_setup_constant.DOCKER_COMPOSE_PATH_KEY)
            if not os.path.isabs(docker_compose_path):
                docker_compose_path = os.path.abspath(docker_compose_path)
            with open(docker_compose_path, "r") as f:
                compose_content = f.read()
                # 使用正则表达式替换 ${xxx} 为 ${!xxx}
                updated_compose_content = re.sub(r'\$\{([^}]+)}', r'${!\1}', compose_content)
                self.parameters[project_setup_constant.DOCKER_COMPOSE_YAML] = updated_compose_content

        output_ros_template_path = os.path.join(self.output_base_path, project_setup_constant.OUTPUT_ROS_TEMPLATE_DIR,
                                                project_setup_constant.OUTPUT_ROS_TEMPLATE_NAME)
        self.processor.process(input_ros_template_name, self.parameters, output_ros_template_path, package_name)
        print(f"Template rendered to {output_ros_template_path}")

        output_config_path = os.path.join(self.output_base_path, project_setup_constant.OUTPUT_CONFIG_NAME)
        if artifact_source_type == ArtifactSourceType.INSTALL_PACKAGE.value:
            self.parameters[project_setup_constant.PACKAGE_NAME_KEY] = self.parameters.get(
                project_setup_constant.PACKAGE_PATH_KEY).split("/")[-1]
        self.processor.process(input_config_name, self.parameters, output_config_path,
                               project_setup_constant.INPUT_CONFIG_PATH)
        print(f"Config rendered to {output_config_path}")

        print("Template rendering complete.")

    def _copy_resources(self):
        output_base = Path(self.output_base_path)

        # 复制静态资源文件，包括icon、README.md、软件包、Docs
        self._copy_icons(output_base)
        self._copy_readme(output_base)
        self._copy_docs(output_base)

        artifact_source_type = self.parameters.get(project_setup_constant.ARTIFACT_SOURCE_TYPE_KEY)
        # 源代码
        if artifact_source_type == ArtifactSourceType.SOURCE_CODE.value:
            print("Handling source code copying.")
        # 软件包
        elif artifact_source_type == ArtifactSourceType.INSTALL_PACKAGE.value:
            self._copy_software_package()
        elif artifact_source_type == ArtifactSourceType.DOCKER_COMPOSE.value:
            self._copy_docker_compose()
        # Dockerfile
        elif artifact_source_type == ArtifactSourceType.DOCKERFILE.value:
            self._copy_dockerfile()
        else:
            raise Exception("Invalid artifact source type.")

        service_type = self.parameters.get(project_setup_constant.SERVICE_TYPE_KEY)
        if service_type == ServiceType.MANAGED.value:
            self._copy_preset_parameters(output_base)

        print("Resource copying complete.")

    @staticmethod
    def _copy_from_package(src_package, src_name, dst_directory):
        with resources.path(src_package, src_name) as src_path:
            if src_path.is_dir():
                shutil.copytree(src_path, dst_directory, dirs_exist_ok=True)
            else:
                shutil.copy2(src_path, dst_directory / src_name)

    def _copy_icons(self, output_base):
        icon_dir = project_setup_constant.INPUT_ICON_DIR
        output_icon_dir = output_base / project_setup_constant.OUTPUT_ICON_DIR
        self._copy_from_package(project_setup_constant.INPUT_ROOT_PATH, icon_dir, output_icon_dir)
        print(f"Copied icons to {output_icon_dir}")

    def _copy_docs(self, output_base):
        arch = self.parameters.get(project_setup_constant.ARCHITECTURE_KEY)
        if Arch.ECS_SINGLE.value == arch:
            docs_dir = project_setup_constant.INPUT_DOCS_ECS_SINGLE_PATH
        elif Arch.ECS_CLUSTER.value == arch:
            docs_dir = project_setup_constant.INPUT_DOCS_ECS_CLUSTER_PATH
        else:
            raise Exception("Invalid architecture.")
        output_docs_dir = output_base / project_setup_constant.OUTPUT_DOCS_DIR
        self._copy_from_package(docs_dir, ".", output_docs_dir)

    def _copy_readme(self, output_base):
        readme_name = project_setup_constant.INPUT_README_NAME
        self._copy_from_package(project_setup_constant.INPUT_ROOT_PATH, readme_name, output_base)
        print(f"Copied README to {output_base}")

    def _copy_preset_parameters(self, output_base):
        self._copy_from_package(project_setup_constant.INPUT_ROOT_PATH,
                                project_setup_constant.INPUT_PRESET_PARAMETERS_NAME, output_base)
        print(f"Copied preset parameters to {output_base}")

    # 处理软件包文件的复制，如 tar.gz
    def _copy_software_package(self):
        print("Handling install package copying...")
        install_package_path = self.parameters.get(project_setup_constant.PACKAGE_PATH_KEY)
        # abspath
        if not os.path.isabs(install_package_path):
            install_package_path = os.path.abspath(install_package_path)
        shutil.copy(install_package_path,
                    os.path.join(self.output_base_path, project_setup_constant.OUTPUT_PACKAGE_DIR))
        print(
            f"Copied install package to {os.path.join(self.output_base_path, project_setup_constant.OUTPUT_PACKAGE_DIR)}")

    # 复制 Dockerfile
    def _copy_dockerfile(self):
        print("Handling Dockerfile copying...")
        dockerfile_path = self.parameters.get(project_setup_constant.DOCKERFILE_PATH_KEY)
        if not os.path.isabs(dockerfile_path):
            dockerfile_path = os.path.abspath(dockerfile_path)
        shutil.copy(dockerfile_path,
                    os.path.join(self.output_base_path, project_setup_constant.OUTPUT_DOCKERFILE_DIR))
        print(
            f"Copied Dockerfile to {os.path.join(self.output_base_path, project_setup_constant.OUTPUT_DOCKERFILE_DIR)}")

    def _copy_docker_compose(self):
        print("Handling Docker compose copying...")
        docker_compose_path = self.parameters.get(project_setup_constant.DOCKER_COMPOSE_PATH_KEY)
        if not os.path.isabs(docker_compose_path):
            docker_compose_path = os.path.abspath(docker_compose_path)
        shutil.copy(docker_compose_path,
                    os.path.join(self.output_base_path, project_setup_constant.OUTPUT_DOCKER_COMPOSE_DIR))
        print(f"Copied Docker compose to "
              f"{os.path.join(self.output_base_path, project_setup_constant.OUTPUT_DOCKER_COMPOSE_DIR)}")

    def _handle_source_code_packaging(self):
        print("Handling source code packaging...")
        artifact_source_type = self.parameters.get(project_setup_constant.ARTIFACT_SOURCE_TYPE_KEY)
        if artifact_source_type != ArtifactSourceType.SOURCE_CODE.value:
            return

        source_code_path = self.parameters.get(project_setup_constant.SOURCE_CODE_PATH_KEY)
        # 确保源文件目录存在且转换为 Path 对象
        source_code_path = Path(source_code_path).resolve()

        if not source_code_path.exists():
            raise FileNotFoundError(f"Source code path '{source_code_path}' does not exist.")

        # 创建临时目录用于存放需要打包的文件和目录
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            repo_name = self.parameters.get(project_setup_constant.REPO_NAME_KEY)
            package_dir = temp_dir_path / repo_name
            package_dir.mkdir(parents=True, exist_ok=True)
            # 定义需要排除的目录
            exclude_dirs = {'.computenest', '.git'}

            # 遍历原始目录，复制非排除的文件和目录到临时目录
            for item in source_code_path.iterdir():
                if item.name not in exclude_dirs:
                    if item.is_dir():
                        shutil.copytree(item, package_dir / item.name)
                    else:
                        shutil.copy2(item, package_dir / item.name)

            destination_dir = self.output_base_path / project_setup_constant.OUTPUT_PACKAGE_DIR
            # 如果存在则先删除
            if destination_dir.exists():
                shutil.rmtree(destination_dir)

            destination_dir.mkdir(parents=True, exist_ok=True)

            # 使用临时目录作为源进行打包
            try:
                archive_path = shutil.make_archive(
                    base_name=str(destination_dir / repo_name), format='gztar',
                    root_dir=temp_dir_path, base_dir=repo_name)
                print(f"Directory '{source_code_path}' has been packed into '{archive_path}'")
            except Exception as e:
                print(f"Packing failed: {e}")
                return

            # 确保目标base路径存在
            if not self.output_base_path.exists():
                self.output_base_path.mkdir(parents=True, exist_ok=True)

            # 移动.tar.gz文件到指定目录
            tar_gz_path = destination_dir / (repo_name + '.tar.gz')
            shutil.move(archive_path, tar_gz_path)
            print(f"'{archive_path}' has been moved to '{tar_gz_path}'")

    # 将输入参数改为计算巢部署物允许的格式
    @staticmethod
    def _sanitize_name(name):
        # 只允许字母、数字、下划线、和中划线
        pattern = r'[^\w-]+'
        # 替换不符合的字符为下划线
        sanitized_name = re.sub(pattern, '_', name)
        return sanitized_name
