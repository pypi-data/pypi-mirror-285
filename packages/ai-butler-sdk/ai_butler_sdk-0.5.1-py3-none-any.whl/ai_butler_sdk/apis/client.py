import httpx
import enum
from ai_butler_sdk.settings import settings
from loguru import logger

base_url = settings.AI_BUTLER_SDK_BASE_URL
token = settings.AI_BUTLER_SDK_TOKEN


class TrainStatusEnum(str, enum.Enum):
    """
    训练状态
    """

    WAITING = "WAITING"
    TRAINING = "TRAINING"
    FAILURE = "FAILURE"
    FINISH = "FINISH"


class DeployOnlineInferStatusEnum(str, enum.Enum):
    """
    部署在线推理服务的状态
    """

    WAITING = "WAITING"
    DEPLOYING = "DEPLOYING"
    FAILURE = "FAILURE"
    FINISH = "FINISH"


def worker_online(name: str, listen_queue: str, concurrency: int, ip_address: str, ports: list) -> bool:
    """worker上线时通知管理后台"""
    headers = {"Authorization": f"Bearer {token}"}
    url = base_url + "/system/celery-workers/online"
    data = {
        "name": name,
        "listen_queue": listen_queue,
        "concurrency": concurrency,
        "ip_address": ip_address,
        "available_ports": ports,
    }
    resp = httpx.post(url, json=data, headers=headers)
    if resp.status_code == 200:
        logger.info(f"{data} worker上线成功!")
        return True
    elif resp.status_code == 400:
        logger.info(f"{data} worker上线失败! {resp.json()}")
        return False
    else:
        logger.info(f"{data} worker上线失败! status_code: {resp.status_code} 请检查网络状态!")
        return False


def worker_offline(name: str):
    """worker下线时通知管理后台"""
    headers = {"Authorization": f"Bearer {token}"}
    url = base_url + "/system/celery-workers/offline"
    data = {
        "name": name,
    }
    resp = httpx.post(url, json=data, headers=headers)
    if resp.status_code == 200:
        logger.info(f"{data} worker下线成功!")
    else:
        logger.info(f"{data} worker下线失败! status_code: {resp.status_code}")


def update_train_task_status(task_id: str, status: TrainStatusEnum):
    """更新训练任务状态"""
    headers = {"Authorization": f"Bearer {token}"}
    url = base_url + f"/ai-models/train-task-groups/train-tasks/{task_id}/status"
    resp = httpx.put(url, json={"status": status}, headers=headers)
    if resp.status_code == 200:
        logger.info(f"训练任务id: {task_id}, 状态变更为: {status}")
    else:
        logger.error(f"训练任务id: {task_id}, 状态变更失败! " f"status_code: {resp.status_code}, 期待变更为: {status}")


def update_deploy_task(
    task_id: str, status: DeployOnlineInferStatusEnum, infer_address: str = "", container_id: str = "", reason: str = ""
):
    """更新训练任务状态"""
    headers = {"Authorization": f"Bearer {token}"}
    url = base_url + f"/applications/deploy-online-infers/{task_id}/by-worker"
    data = {"status": status, "infer_address": infer_address, "container_id": container_id, "reason": reason}
    resp = httpx.put(url, json=data, headers=headers)
    if resp.status_code == 200:
        logger.info(f"部署任务id: {task_id}, 状态变更为: {status}")
    else:
        logger.error(f"部署任务id: {task_id}, 状态变更失败! " f"status_code: {resp.status_code}, 期待变更为: {status}")
