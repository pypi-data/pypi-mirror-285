# # # # 生成的项目相对路径 # # # #
# icon资源目录
OUTPUT_ICON_DIR = "resources/icons/"
# 软件包目录
OUTPUT_PACKAGE_DIR = "resources/artifact_resources/file/"
# Dockerfile文件目录
OUTPUT_DOCKERFILE_DIR = "resources/artifact_resources/acr_image/"
# Docker compose文件目录
OUTPUT_DOCKER_COMPOSE_DIR = "resources/artifact_resources/docker_compose/"
# Helm Chart包目录
OUTPUT_HELM_CHART_DIR = "resources/artifact_resources/helm_chart/"
# ROS模板目录相对路径，暂时先不考虑多模板
OUTPUT_ROS_TEMPLATE_DIR = "ros_templates/"
# docs目录相对路径
OUTPUT_DOCS_DIR = "docs/"

# 默认服务icon
OUTPUT_SERVICE_ICON_NAME = "service_logo.png"
# Dockerfile文件名称
OUTPUT_DOCKERFILE_NAME = "Dockerfile"
# ROS模板文件名称
OUTPUT_ROS_TEMPLATE_NAME = "template.yaml"
# config.yaml文件名称
OUTPUT_CONFIG_NAME = "config.yaml"
# 托管版预设参数文件名称
OUTPUT_PRESET_PARAMETERS_NAME = "preset_parameters.yaml"
# README.md文件名称
OUTPUT_README_NAME = "README.md"
# index.md
OUTPUT_INDEX_NAME = "index.md"


# # # # 生成项目所需模板与资源的路径信息 # # # #
# 包内资源目录，需要用.这种方式来指定路径
INPUT_ROOT_PATH = "computenestcli.resources.project_generation"
INPUT_ROS_TEMPLATE_ECS_SINGLE_PATH = "computenestcli.resources.project_generation.ros_templates.ecs_single"
INPUT_ROS_TEMPLATE_ECS_CLUSTER_PATH = "computenestcli.resources.project_generation.ros_templates.ecs_cluster"
INPUT_CONFIG_PATH = "computenestcli.resources.project_generation.configs"
INPUT_DOCS_ECS_SINGLE_PATH = "computenestcli.resources.project_generation.docs.ecs_single"
INPUT_DOCS_ECS_CLUSTER_PATH = "computenestcli.resources.project_generation.docs.ecs_cluster"
# icon资源目录名称
INPUT_ICON_DIR = "icons"

# 代码源config.yaml模板名称
INPUT_SOURCE_CODE_CONFIG_NAME = "source_code_config.yaml.j2"
# 安装包config.yaml模板名称
INPUT_INSTALL_PACKAGE_CONFIG_NAME = "install_package_config.yaml.j2"
# dockerfile_config.yaml模板名称
INPUT_DOCKERFILE_CONFIG_NAME = "dockerfile_config.yaml.j2"
# docker_compose_config.yaml模板名称
INPUT_DOCKER_COMPOSE_CONFIG_NAME = "docker_compose_config.yaml.j2"
# Helm Chart config.yaml模板名称
INPUT_HELM_CHART_CONFIG_NAME = "helm_chart_config.yaml.j2"

# ros_template资源名称
INPUT_SOURCE_CODE_ROS_TEMPLATE_NAME = "source_code.yaml.j2"
INPUT_INSTALL_PACKAGE_ROS_TEMPLATE_NAME = "install_package.yaml.j2"
INPUT_DOCKERFILE_ROS_TEMPLATE_NAME = "dockerfile.yaml.j2"
INPUT_DOCKER_COMPOSE_ROS_TEMPLATE_NAME = "docker_compose.yaml.j2"
INPUT_HELM_CHART_ROS_TEMPLATE_NAME = "helm_chart.yaml.j2"

# 托管版预设参数模板名称
INPUT_PRESET_PARAMETERS_NAME = "preset_parameters.yaml"
# README.md资源名称
INPUT_README_NAME = "README.md"
APP_NAME = "myapp"


# # # # 参数Key # # # #
# 软件形态
ARTIFACT_SOURCE_TYPE_KEY = "ArtifactSourceType"
# 架构
ARCHITECTURE_KEY = "Arch"
# 源代码路径
SOURCE_CODE_PATH_KEY = "SourceCodePath"
# 安装包路径
PACKAGE_PATH_KEY = "PackagePath"
# 安装包名称
PACKAGE_NAME_KEY = "PackageName"
# Dockerfile路径
DOCKERFILE_PATH_KEY = "DockerfilePath"
# Docker Compose路径
DOCKER_COMPOSE_PATH_KEY = "DockerComposeYamlPath"
# Docker Compose YAML
DOCKER_COMPOSE_YAML = "DockerComposeYaml"
# 软件安装运行命令
RUN_COMMAND_KEY = "RunCommand"
# 服务端口号
SERVICE_PORT_KEY = "ServicePort"
# 安全组端口号
SECURITY_GROUP_PORT_KEY = "SecurityGroupPort"
# 服务类型
SERVICE_TYPE_KEY = "ServiceType"
# 服务地域
SERVICE_REGION_KEY = "ServiceRegion"
# 可部署地域
DEPLOY_REGION_KEY = "AllowedRegion"
# 架构
ARCH_KEY = "Architecture"
# 镜像名称
IMAGE_NAME_KEY = "ImageName"
# 镜像版本
IMAGE_TAG_KEY = "ImageTag"
# 端口号，需要映射的容器与宿主机的端口号，例如：8080:8080
PORT_KEY = "Port"
# 仓库名称
REPO_NAME_KEY = "RepoName"
# PreStartCommand
PRE_START_COMMAND_KEY = "PreStartCommand"
# PostStartCommand
POST_START_COMMAND_KEY = "PostStartCommand"
