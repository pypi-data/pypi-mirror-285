from enum import Enum


class ServiceType(Enum):
    """
    服务类别
    """
    # 托管版
    MANAGED = "managed"
    # 私有化部署
    PRIVATE = "private"
