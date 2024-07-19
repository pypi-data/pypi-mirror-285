from enum import Enum, auto


class ArtifactSourceType(Enum):
    """
    软件形态，包括：源代码、安装包、Dockerfile、DockerCompose、HelmChart
    """
    SOURCE_CODE = 'SourceCode'
    INSTALL_PACKAGE = 'InstallPackage'
    DOCKERFILE = 'Dockerfile'
    DOCKER_COMPOSE = 'DockerCompose'
    HELM_CHART = 'HelmChart'
