from enum import Enum

REGION = 'us-east-1'
NAMESPACE = 'kube-system'
DEFAULT_NAMESPACE = 'default'
SERVICE_ACCOUNT_NAME = 's3-csi-driver-sa'
ADDON_NAME = "aws-mountpoint-s3-csi-driver"
KNATIVE_SERVING_NAMESPACE = 'knative-serving'
CONFIG_FEATURES = 'config-features'
BUILD_TOOL = 'buildkit'


def get_cluster_name():
    return "tensorkube"


def get_mount_policy_name(cluster_name):
    return f'{cluster_name}-mountpoint-policy'


def get_mount_driver_role_name(cluster_name):
    return f'{cluster_name}-mountpoint-driver-role'


class Events(Enum):
    CONFIGURE_START = 'configure-start'
    CONFIGURE_END = 'configure-end'
    CONFIGURE_ERROR = 'configure-error'

    DEPLOY_START = 'deploy-start'
    DEPLOY_END = 'deploy-end'
    DEPLOY_ERROR = 'deploy-error'

    TEST_START = 'test-start'
    TEST_END = 'test-end'


class PodStatus(Enum):
    PENDING = 'Pending'
    RUNNING = 'Running'
    SUCCEEDED = 'Succeeded'
    FAILED = 'Failed'
    UNKNOWN = 'Unknown'


def get_efs_service_account_name() -> str:
    return f'{get_cluster_name()}-efs-csi-controller-sa'


def get_efs_role_name() -> str:
    return f'AmazonEKS_EFS_CSI_DriverRole_{get_cluster_name()}'


def get_logging_service_account_name() -> str:
    return f'cloudwatch-agent'


def get_cloudwatch_role_name() -> str:
    return f'cloudwatch-agent-role_{get_cluster_name()}'

def get_cloudwatch_namespace() -> str:
    return 'amazon-cloudwatch'


def get_efs_security_group_name() -> str:
    return f'eks-efs-sg-{get_cluster_name()}'
