import os
import httpx
import time
from ai_butler_sdk.utils import unzip_file
from ai_butler_sdk.apis.client import update_train_task_status, TrainStatusEnum
from loguru import logger
import shutil
import traceback


class TrainBase:
    def __init__(
        self,
        train_task_id: str,
        network: str,
        data_set_urls: list[str],
        train_params: dict,
        log_upload_url: str,
        model_weight_upload_url: str,
        pretrain_model_weight_download_url: str | None = None,
        base_dir: str = "",
    ):
        # train中产生的所有文件保存至output/train/{train_task_id}下, 训练完成将自动清理
        self.root_path = os.path.join(base_dir, f"output/train/{train_task_id}/")
        os.makedirs(self.root_path, exist_ok=True)
        # train中产生的训练日志存放到./output/train/网络/训练任务id/train.log
        self.log_local_path = os.path.join(base_dir, f"output/train/{train_task_id}/train.log")
        # train中产生的训练结果文件与标签文件label.txt压缩后的zip
        # 存放到./output/train/网络/训练任务id/result.zip
        self.result_local_path = os.path.join(base_dir, f"output/train/{train_task_id}/result.zip")
        # 本地数据集存放目录
        self.data_sets_local_path = os.path.join(base_dir, f"output/train/{train_task_id}/data_sets/")
        os.makedirs(self.data_sets_local_path, exist_ok=True)
        # 本地追加训练基础结果文件
        self.pretrain_local_path = os.path.join(base_dir, f"output/train/{train_task_id}/pretrain/")
        os.makedirs(f"output/train/{train_task_id}/pretrain", exist_ok=True)
        self.train_task_id = train_task_id
        self.network = network
        self.data_set_urls = data_set_urls
        self.pretrain_model_weight_download_url = pretrain_model_weight_download_url
        self.train_params = train_params
        self.log_upload_url = log_upload_url
        self.model_weight_upload_url = model_weight_upload_url

    def download_data_sets(self):
        """下载数据集到本地目录"""
        logger.info("---------------------------------开始下载数据集---------------------------------")
        for data_set_url in self.data_set_urls:
            timestamp = str(int(time.time() * 1000))
            with httpx.stream("GET", url=data_set_url) as resp:
                # 打开本地文件以二进制写模式
                target_path = os.path.join(self.data_sets_local_path, f"{timestamp}.zip")
                with open(target_path, "wb") as f:
                    for chunk in resp.iter_bytes():
                        f.write(chunk)
                        # 可选地在这里调用flush来确保数据及时写入磁盘
                        f.flush()
                # 解压文件
                unzip_file(target_path, target_path[:-4])
            os.remove(target_path)  # 删除压缩包
        logger.info("---------------------------------数据集下载完成---------------------------------")

    def download_base_task(self):
        """现在追加训练的基础任务结果文件"""
        if download_url := self.pretrain_model_weight_download_url:
            logger.info("---------------------------------开始下载预训练文件---------------------------------")
            timestamp = str(int(time.time() * 1000))
            with httpx.stream("GET", url=download_url) as resp:
                # 打开本地文件以二进制写模式
                target_path = os.path.join(self.pretrain_local_path, f"{timestamp}.zip")
                with open(target_path, "wb") as f:
                    for chunk in resp.iter_bytes():
                        f.write(chunk)
                        # 可选地在这里调用flush来确保数据及时写入磁盘
                        f.flush()
                # 解压文件
                unzip_file(target_path, self.pretrain_local_path)
            os.remove(target_path)  # 删除压缩包
            logger.info("---------------------------------预训练文件下载完成---------------------------------")

    def download(self):
        """下载训练所需文件"""
        self.download_data_sets()
        self.download_base_task()

    def pre_train(self):
        pass

    def train(self):
        raise NotImplementedError

    def after_train(self):
        pass

    def upload_result(self):
        logger.info("---------------------------------开始上传训练结果---------------------------------")
        with open(self.result_local_path, "rb") as f:
            content = f.read()
        resp = httpx.put(self.model_weight_upload_url, content=content, timeout=None)
        if resp.status_code != 200:
            logger.error("结果权重文件上传失败!")
            raise
        logger.info("---------------------------------训练结果上传完成---------------------------------")

    def upload_log(self):
        logger.info("---------------------------------开始上传训练日志---------------------------------")
        with open(self.log_local_path, "rb") as f:
            content = f.read()
        resp = httpx.put(self.log_upload_url, content=content)
        if resp.status_code != 200:
            logger.error("训练日志文件上传失败!")
            raise
        logger.info("---------------------------------训练日志上传完成---------------------------------")

    def __call__(self):
        is_exception = False
        try:
            update_train_task_status(self.train_task_id, TrainStatusEnum.TRAINING)
            self.download()
            self.pre_train()
            self.train()
            self.after_train()
            self.upload_result()
        except Exception:
            logger.error(f"训练任务失败: {traceback.format_exc()}")
            update_train_task_status(self.train_task_id, TrainStatusEnum.FAILURE)
            is_exception = True
        else:
            update_train_task_status(self.train_task_id, TrainStatusEnum.FINISH)
        finally:
            self.upload_log()
            if not is_exception:  # 没有异常时删除目录, 异常时保留数据集用于排查
                shutil.rmtree(self.root_path, ignore_errors=True)
