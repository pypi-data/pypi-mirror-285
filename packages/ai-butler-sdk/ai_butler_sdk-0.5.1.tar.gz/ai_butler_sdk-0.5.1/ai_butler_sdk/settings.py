from functools import lru_cache

from pydantic_settings import BaseSettings


# 可以通过环境变量的方式修改此配置项
class Settings(BaseSettings):
    AI_BUTLER_SDK_BASE_URL: str
    AI_BUTLER_SDK_TOKEN: str
    CELERY_BROKER_URL: str
    CELERY_WORKER_NAME: str
    CELERY_WORKER_LISTEN_QUEUE: str
    CELERY_WORKER_CONCURRENCY: int = 1
    CELERY_WORKER_LOGGER_LEVEL: str = "INFO"

    DEPLOY_ONNX_WEIGHT_DIR: str = "onnx_weight"
    DEPLOY_ONNX_DOCKER_IMAGE_CPU: str = "ai-butler-onnx-infer-service-cpu"
    DEPLOY_ONNX_DOCKER_IMAGE_GPU: str = "ai-butler-onnx-infer-service-gpu"
    DEPLOY_TARGET_CONTAINER_WORKDIR: str = "/srv/app"

    DEPLOY_ONNX_IP_ADDRESS: str = ""
    DEPLOY_ONNX_AVAILABLE_PORT: str = ""  # 逗号分割多个端口
    # 宿主机的项目目录, 在docker中启动另一个docker, 挂载目录需要挂载宿主机的真实目录地址
    DEPLOY_HOST_DIR: str = ""

    class Config:
        env_file = ".envs"


@lru_cache
def get_train_settings() -> Settings:
    """读取配置优化写法, 全局共享"""
    return Settings()  # type: ignore


settings = get_train_settings()
