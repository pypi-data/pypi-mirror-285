"""Common variables."""
import os
import posixpath
from urllib.parse import urlparse

server_url = None
minio_url = None
minio_username = None
minio_password = None
mlm_login = None
mlm_password = None

active_run_stack = []
active_experiment_name = None

EXPERIMENT_NAME_FOR_EXECUTOR = "executors"
EXPERIMENT_NAME_FOR_DATASET_LOADER = "dataset_loaders"
FILENAME_FOR_INFERENCE_CONFIG = "predict_config.json"


def _get_server_ml_api() -> str:
    """Get server '/mlflow' endpoint URL."""
    return posixpath.join(_get_server_url(), "mlflow")


def _get_log_service_url(function_name: str) -> str:
    """Get server '/log-object' endpoint URL for log_model, log_artifact, download_artifacts functions."""
    log_object_url = os.environ.get("log_object_url")
    base_url = log_object_url if log_object_url is not None else _get_server_url()
    return posixpath.join(base_url, "log-object", function_name.replace("_", "-"))


def _get_server_url() -> str:
    """
    Get server URL.

    If you set the URL using 'mlmanagement.set_server_url' function,
    it takes precedence over the URL from the environment variable 'server_url'
    """
    return os.environ.get("server_url", "https://local.tai-dev.intra.ispras.ru") if not server_url else server_url


def _get_minio_url() -> str:
    """
    Get minio URL.

    If you set the URL using 'mlmanagement.set_minio_url' function,
    it takes precedence over the URL from the environment variable 'MINIO_URL'
    """
    server_url_inner = urlparse(_get_server_url())
    return (
        os.environ.get("MINIO_URL", server_url_inner._replace(netloc=f"minio-{server_url_inner.netloc}").geturl())
        if not minio_url
        else minio_url
    )


def _get_minio_credentials() -> (str, str):
    """
    Get minio credentials.

    If you set the URL using 'mlmanagement.set_minio_credentials' function,
    it takes precedence over the URL from the environment variables 'MINIO_USERNAME' and 'MINIO_PASSWORD'.
    """
    username = os.environ.get("MINIO_USERNAME", "minioadmin") if not minio_username else minio_username
    password = os.environ.get("MINIO_PASSWORD", "61w7QYulWjmnpm5") if not minio_password else minio_password
    return username, password


def _get_mlm_credentials() -> (str, str):
    """
    Get mlm credentials.

    If you set the URL using 'mlmanagement.set_mlm_credentials' function,
    it takes precedence over the URL from the environment variables 'MLM_LOGIN' and 'MLM_PASSWORD'.
    Environment variables 'login' and 'password' have last priority.
    """
    login = (
        (os.getenv("login") if not os.getenv("MLM_LOGIN") else os.getenv("MLM_LOGIN")) if not mlm_login else mlm_login
    )
    password = (
        (os.getenv("password") if not os.getenv("MLM_PASSWORD") else os.getenv("MLM_PASSWORD"))
        if not mlm_password
        else mlm_password
    )

    return login, password
