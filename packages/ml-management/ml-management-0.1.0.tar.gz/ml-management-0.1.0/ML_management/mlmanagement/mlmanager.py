"""This module create and send request to MLManagement server."""
import inspect
import json
import os
import sys
import tarfile
import tempfile
import threading
from contextlib import _GeneratorContextManager
from tempfile import TemporaryDirectory

import cloudpickle
import httpx

import mlflow
from ML_management.loader.loader import CONFIG_KEY_ARTIFACTS
from ML_management.mlmanagement import variables
from ML_management.mlmanagement.base_exceptions import *  # noqa: F403
from ML_management.mlmanagement.base_exceptions import MLMClientError, MLMServerError
from ML_management.mlmanagement.jsonschema_inference import infer_jsonschema
from ML_management.mlmanagement.model_type import ModelType
from ML_management.mlmanagement.server_mlmanager_exceptions import *  # noqa: F403
from ML_management.mlmanagement.server_mlmanager_exceptions import (
    AuthError,
    InvalidExperimentNameError,
    InvalidVisibilityOptionError,
    ModelTypeIsNotFoundError,
)
from ML_management.mlmanagement.session import AuthSession
from ML_management.mlmanagement.variables import (
    EXPERIMENT_NAME_FOR_DATASET_LOADER,
    EXPERIMENT_NAME_FOR_EXECUTOR,
    _get_log_service_url,
    _get_server_ml_api,
    active_run_stack,
)
from ML_management.registry.exceptions import *  # noqa: F403
from mlflow.exceptions import MlflowException, RestException


def raise_error(response: httpx.Response):
    if response.status_code == 500:
        raise MLMServerError("Internal server error.")
    if response.status_code != 200:
        detail = response.read().decode()
        if not detail:
            raise MLMServerError("Internal server error.")
        try:
            detail = json.loads(detail).get("detail")
        except Exception:
            raise MLMServerError(f"Server error '{detail}' with code {response.status_code}") from None
        if not (
            isinstance(detail, dict) and "exception_class" in detail and ("params" in detail or "message" in detail)
        ):
            raise MLMServerError(detail)
        if "params" in detail:
            error = getattr(sys.modules[__name__], detail["exception_class"])(**detail["params"])
        else:
            error = getattr(sys.modules[__name__], detail["exception_class"])(detail["message"])
        if isinstance(error, AuthError):
            error.args = (
                f"{error.args[0]}. "
                "Possible reason: you are trying to upload a version of an object owned by another user.",
            )
        raise error


def create_kwargs(frame):
    """Get name and kwargs of function by its frame."""
    function_name = inspect.getframeinfo(frame)[2]  # get name of function
    _, _, _, kwargs = inspect.getargvalues(frame)  # get kwargs of function
    kwargs.pop("self", None)
    kwargs.pop("parts", None)
    kwargs.pop("python_path", None)

    return (
        function_name,
        kwargs,
    )  # return name of mlflow function and kwargs for that function


def tar_folder(w, model_folder):
    try:
        with open(w, "wb") as buff:
            with tarfile.open(mode="w|", fileobj=buff) as tar:
                tar.add(model_folder, arcname=os.path.basename(model_folder))
    except Exception as err:
        raise MLMClientError("Some error during tar the content.") from err


def untar_folder(r, to_folder):
    try:
        with open(r, "rb") as buff:
            with tarfile.open(mode="r|", fileobj=buff) as tar:
                tar.extractall(to_folder)
    except Exception as err:
        raise MLMClientError("Some error during untar the content.") from err


def open_pipe_send_request(folder, kwargs, extra_attrs, for_class, module_name, url):
    r, w = os.pipe()

    try:
        thread = threading.Thread(target=tar_folder, args=(w, folder))
        thread.start()
    except Exception as err:
        os.close(r)
        os.close(w)
        raise err

    with open(r, "rb") as buff:
        with request(
            "log_model",
            kwargs,
            extra_attrs,
            for_class,
            module_name,
            buff,
            os.path.basename(folder),
            True,
            url,
        ) as response:
            return response


def request_log_model(function_name: str, kwargs: dict, extra_attrs: list, for_class: dict, module_name: str):
    """
    Send request for log_model function.

    Steps for log model:
    0) Infer jsonschema, raise if it is invalid
    1) open temporary directory
    2) Do mlflow.save_model() locally
    3) Pack it to tar file
    4) Send it to server to log model there.
    """
    delete_args_for_save_model_func = [
        "description",
        "model_version_tags",
        "artifact_path",
        "registered_model_name",
        "await_registration_for",
        # now, extra arguments
        "upload_model_mode",
        "source_model_name",
        "source_model_version",
        "visibility",
        "source_executor_name",
        "source_executor_version",
        "source_executor_role",
        "start_build",
        "create_venv_pack",
    ]  # not need for save_model

    extra_imports_args = [
        "submodules",
        "module_name",
        "used_modules_names",
        "extra_modules_names",
        "root_module_name",
        "linter_check",
    ]

    delete_args_for_log_func = [
        "python_model",
        "artifacts",
        "conda_env",
        "pip_requirements",
        "extra_pip_requirements",
    ]  # not need for log model on server

    for delete_arg in extra_imports_args:
        kwargs.pop(delete_arg, None)
    kwargs_for_save_model = kwargs.copy()
    for delete_arg in delete_args_for_save_model_func:
        kwargs_for_save_model.pop(delete_arg, None)
    python_model = kwargs_for_save_model["python_model"]

    # import some modules here because of circular import
    from ML_management.dataset_loader.dataset_loader_pattern import DatasetLoaderPattern
    from ML_management.dataset_loader.dataset_loader_pattern_to_methods_map import (
        dataset_loader_pattern_to_methods,
    )
    from ML_management.executor.base_executor import BaseExecutor
    from ML_management.executor.executor_pattern_to_methods_map import executor_pattern_to_methods
    from ML_management.model.model_type_to_methods_map import model_pattern_to_methods
    from ML_management.model.patterns.model_pattern import Model

    if python_model is not None:
        if not isinstance(python_model, BaseExecutor):
            del kwargs["visibility"]
        if isinstance(python_model, Model):
            kwargs["model_type"] = ModelType.MODEL
            model_to_methods = model_pattern_to_methods
            if variables.active_experiment_name in [
                EXPERIMENT_NAME_FOR_EXECUTOR,
                EXPERIMENT_NAME_FOR_DATASET_LOADER,
            ]:
                raise InvalidExperimentNameError(ModelType.MODEL.value, variables.active_experiment_name)
        elif isinstance(python_model, BaseExecutor):
            kwargs["model_type"] = ModelType.EXECUTOR
            model_to_methods = executor_pattern_to_methods

            if variables.active_experiment_name != EXPERIMENT_NAME_FOR_EXECUTOR:
                raise InvalidExperimentNameError(ModelType.EXECUTOR.value, variables.active_experiment_name)
            if kwargs["visibility"] is None:
                raise InvalidVisibilityOptionError(ModelType.EXECUTOR.value)
            # collect all needed model's methods
            kwargs["desired_model_methods"] = python_model.desired_model_methods
            kwargs["upload_model_modes"] = python_model.upload_model_modes
            kwargs["desired_dataset_loader_methods"] = python_model.desired_dataset_loader_methods
        elif isinstance(python_model, DatasetLoaderPattern):
            kwargs["model_type"] = ModelType.DATASET_LOADER
            model_to_methods = dataset_loader_pattern_to_methods
            if variables.active_experiment_name != EXPERIMENT_NAME_FOR_DATASET_LOADER:
                raise InvalidExperimentNameError(kwargs["model_type"].value, variables.active_experiment_name)
        else:
            raise ModelTypeIsNotFoundError()

        # now we need to infer schemas for methods.
        methods_schema = {}
        for model_type, methods_name_to_schema_map in model_to_methods.items():
            if isinstance(python_model, model_type):
                for method_name_to_schema in methods_name_to_schema_map:
                    model_method = getattr(python_model, method_name_to_schema.name, None)
                    model_method_schema = infer_jsonschema(model_method)
                    methods_schema[method_name_to_schema.value] = model_method_schema

        kwargs["model_method_schemas"] = methods_schema

        for delete_arg in delete_args_for_log_func:
            kwargs.pop(delete_arg, None)

        if function_name == "log_model":
            kwargs["loader_module"] = mlflow.pyfunc.model.__name__
            with TemporaryDirectory() as temp_dir:
                model_folder = "model"
                path_for_model_folder = os.path.join(temp_dir, model_folder)
                mlflow.pyfunc.save_model(path=path_for_model_folder, **kwargs_for_save_model)
                model_folder = path_for_model_folder
                return open_pipe_send_request(
                    model_folder, kwargs, extra_attrs, for_class, module_name, url=_get_log_service_url("log_model")
                )
        else:
            artifacts_path = os.path.join(kwargs["model_path"], CONFIG_KEY_ARTIFACTS)
            if os.path.isfile(artifacts_path):
                raise Exception(f"The artifact file {artifacts_path} is invalid. The artifact must be a directory.")

            model_folder = kwargs["model_path"]

            del kwargs["model_path"]
            kwargs["loader_module"] = "ML_management.loader.loader"

            return open_pipe_send_request(
                model_folder, kwargs, extra_attrs, for_class, module_name, url=_get_log_service_url("log_model")
            )

    else:
        raise Exception("python_model parameter must be specified")


def request_log_artifacts(function_name, kwargs, extra_attrs, for_class, module_name):
    """Send request for log artifact."""
    local_path = kwargs["local_path"]
    if not os.path.exists(local_path):
        raise FileNotFoundError(f"Path: {local_path} does not exist.")
    if not os.path.isdir(local_path):
        basename = os.path.basename(os.path.normpath(local_path))
        with open(local_path, "rb") as file:
            with request(
                function_name,
                kwargs,
                extra_attrs,
                for_class,
                module_name,
                file,
                basename,
                url=_get_log_service_url(function_name),
            ) as response:
                return response

    return open_pipe_send_request(
        local_path, kwargs, extra_attrs, for_class, module_name, url=_get_log_service_url(function_name)
    )


def request_download_artifacts(function_name, kwargs, extra_attrs, for_class, module_name):
    with request(
        function_name, kwargs, extra_attrs, for_class, module_name, url=_get_log_service_url(function_name), stream=True
    ) as response:
        raise_error(response)

        is_tar = response.headers.get("content-type", "application/octet-stream") == "application/x-tar"
        dst_path = kwargs.get("dst_path")
        path = kwargs.get("path")
        if dst_path is None:
            dst_path = tempfile.mkdtemp()
        dst_path = os.path.abspath(os.path.normpath(dst_path))
        local_path = os.path.join(dst_path, os.path.normpath(path))
        if is_tar:
            r, w = os.pipe()

            try:
                thread = threading.Thread(target=untar_folder, args=(r, local_path))
                thread.start()
            except Exception as err:
                os.close(r)
                os.close(w)
                raise err

            with open(w, "wb") as wfd:
                for chunk in response.iter_raw():
                    wfd.write(chunk)
            thread.join()
            return local_path
        else:
            dirs = os.path.dirname(local_path)
            if not os.path.exists(dirs):
                os.makedirs(dirs)
            with open(local_path, "wb") as f:
                for chunk in response.iter_bytes():
                    f.write(chunk)
            return local_path


def request(
    function_name,
    kwargs,
    extra_attrs,
    for_class=None,
    module_name=None,
    file=None,
    basename=None,
    is_tar=False,
    url=None,
    stream=False,
) -> _GeneratorContextManager:
    """Create mlflow_request and send it to server."""
    mlflow_request = {
        "function_name": function_name,
        "kwargs": kwargs,
        "for_class": for_class,
        "extra_attrs": extra_attrs,
        "module_name": module_name,
        "experiment_name": variables.active_experiment_name,
        "active_run_ids": [run.info.run_id for run in active_run_stack],
    }

    url = url if url is not None else _get_server_ml_api()

    if not file:
        return AuthSession().post(url=url, stream=stream, json=mlflow_request)

    # upload multipart
    data = {"mlflow_request": json.dumps(mlflow_request)}
    headers = {"Transfer-Encoding": "chunked"}

    file_content_type = "application/octet-stream"
    if is_tar:
        file_content_type = "application/x-tar"

    files = {"file": (basename, file, file_content_type)}

    return AuthSession().post(
        url=url,
        stream=stream,
        data=data,
        files=files,
        headers=headers,
    )


def send_request_to_server(function_name, kwargs, extra_attrs, for_class, module_name):
    """
    Send request to server.

    Takes frame of mlflow func and extra_attr
    extra_attr is needed if original mlflow function is in the mlflow.<extra_attr> package
    for example function log_model is in mlflow.pyfunc module (mlflow.pyfunc.log_model())
    """
    # special case for log_model, load_model, save_model
    if function_name == "log_model" or function_name == "log_object_src":
        response = request_log_model(function_name, kwargs, extra_attrs, for_class, module_name)
        return raise_error(response)
    elif function_name == "save_model":
        return mlflow.pyfunc.save_model(**kwargs)
    elif function_name == "log_artifact":
        response = request_log_artifacts(function_name, kwargs, extra_attrs, for_class, module_name)
        return raise_error(response)
    elif function_name in ["download_artifacts", "download_job_artifacts"]:
        return request_download_artifacts(
            function_name,
            kwargs,
            extra_attrs,
            for_class,
            module_name,
        )

    with request(function_name, kwargs, extra_attrs, for_class, module_name) as response:
        response_content = response.content

        try:
            decoded_result = cloudpickle.loads(response_content)
        except Exception:
            raise MLMServerError(f"Server error: {response_content.decode()}, status: {response.status_code}") from None

        # raise error if mlflow is supposed to raise error
        if isinstance(decoded_result, MlflowException):
            is_rest = decoded_result.json_kwargs.pop("isRest", False)
            if is_rest:
                created_json = {
                    "error_code": decoded_result.error_code,
                    "message": decoded_result.message,
                }
                decoded_result = RestException(created_json)
            raise decoded_result
        elif isinstance(decoded_result, AuthError) and (
            function_name == "log_model" or function_name == "log_object_src"
        ):
            decoded_result.args = (
                f"{decoded_result.args[0]}. "
                "Possible reason: you are trying to upload a version of an object owned by another user",
            )
            raise decoded_result
        elif isinstance(decoded_result, Exception):
            raise decoded_result
        return decoded_result


def _check_if_call_from_predict_function():
    """
    Check if call to server was from predict function of model.

    Calls from predict function are prohibited and will do and return nothing.
    """
    from ML_management.model.model_type_to_methods_map import ModelMethodName
    from ML_management.model.patterns.model_pattern import Model

    predict_func_name = ModelMethodName.predict_function.name

    for frame in inspect.stack():
        if frame.function == predict_func_name and Model in frame[0].f_locals.get("self").__class__.__mro__:
            return True
    return False


def request_for_function(frame, extra_attrs=None, for_class=None, module_name=None):
    """
    Send request to server or call mlflow function straightforward.

    Input parameters:
    :param frame: frame of equivalent mlflow function
    :param extra_attrs: list of extra modules for mlflow library, for example "tracking" (mlflow.tracking)
    :param for_class: parameters in case of mlflow class (for example mlflow.tracking.MLflowClient() class)
    """
    if _check_if_call_from_predict_function():
        return None
    if extra_attrs is None:
        extra_attrs = []
    if module_name is None:
        module_name = "mlflow"

    function_name, kwargs = create_kwargs(frame)

    return send_request_to_server(function_name, kwargs, extra_attrs, for_class, module_name)
