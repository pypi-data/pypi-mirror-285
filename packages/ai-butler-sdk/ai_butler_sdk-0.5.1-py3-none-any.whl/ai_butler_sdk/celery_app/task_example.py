from ai_butler_sdk.train import TrainBase
from ai_butler_sdk.celery_app import celery_app
from ai_butler_sdk.deploy_onnx import DeployOnnxInfer


class MockTrain(TrainBase):
    def train(self):
        with open(self.log_local_path, "w") as f:
            f.write("123")
        with open(self.result_local_path, "wb") as f:
            f.write(b"123")


@celery_app.task
def pytorch_object_detection_train(
    train_task_id: str,
    network: str,
    data_set_urls: list[str],
    train_params: dict,
    log_upload_url: str,
    model_weight_upload_url: str,
    pretrain_model_weight_download_url: str | None = None,
):
    """模拟训练"""
    mock_train = MockTrain(
        train_task_id,
        network,
        data_set_urls,
        train_params,
        log_upload_url,
        model_weight_upload_url,
        pretrain_model_weight_download_url,
    )
    mock_train()


@celery_app.task
def deploy_onnx_infer_by_train_task(
    deploy_id: str, inner_token: str, train_result_url: str | None = None, is_gpu: bool = False,
    service_type: str = "OBJECT_DETECTION"
):
    deploy_onnx_infer = DeployOnnxInfer(deploy_id, inner_token, train_result_url, service_type, is_gpu)
    deploy_onnx_infer()
