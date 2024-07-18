import os
import httpx
import time
from ai_butler_sdk.utils import unzip_file
from loguru import logger
import shutil
import traceback


class EvalBase:
    def __init__(
        self,
        eval_task_id: str,
        data_set_urls: list[str],
        model_weight_download_url: str | None = None,
        base_dir: str = "",
    ):
        # 评估中产生的所有文件
        self.root_path = os.path.join(base_dir, f"output/eval/{eval_task_id}/")
        os.makedirs(self.root_path, exist_ok=True)
        # 本地数据集存放目录
        self.data_sets_local_path = os.path.join(base_dir, f"output/eval/{eval_task_id}/data_sets/")
        os.makedirs(self.data_sets_local_path, exist_ok=True)
        # 本地训练权重文件
        self.pretrain_local_path = os.path.join(base_dir, f"output/eval/{eval_task_id}/pretrain/")
        os.makedirs(f"output/train/{eval_task_id}/pretrain", exist_ok=True)
        self.eval_task_id = eval_task_id
        self.data_set_urls = data_set_urls
        self.model_weight_download_url = model_weight_download_url

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
        if download_url := self.model_weight_download_url:
            logger.info("---------------------------------开始下载模型权重---------------------------------")
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
            logger.info("---------------------------------模型权重下载完成---------------------------------")

    def download(self):
        """下载所需文件"""
        self.download_data_sets()
        self.download_base_task()

    def pre_eval(self):
        pass

    def eval(self):
        raise NotImplementedError

    def after_eval(self):
        pass

    def __call__(self):
        try:
            # update_train_task_status(self.train_task_id, TrainStatusEnum.TRAINING)
            self.download()
            self.pre_eval()
            result = self.eval()
            self.after_eval()
        except Exception:
            logger.error(f"评估任务失败: {traceback.format_exc()}")
            # update_train_task_status(self.train_task_id, TrainStatusEnum.FAILURE)
        else:
            pass
            # update_train_task_status(self.train_task_id, TrainStatusEnum.FINISH)
        finally:
            shutil.rmtree(self.root_path, ignore_errors=True)
