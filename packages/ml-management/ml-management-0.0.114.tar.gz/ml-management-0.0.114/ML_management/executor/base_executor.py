"""Executor template for custom executor."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

from ML_management.dataset_loader import DatasetLoaderPattern
from ML_management.dataset_loader.dataset_loader_pattern_to_methods_map import DatasetLoaderMethodName
from ML_management.executor.patterns import (
    DEFAULT_ROLE,
    ArbitraryDatasetLoaderPattern,
    ArbitraryModelsPattern,
    OneDatasetLoaderPattern,
    OneModelPattern,
)
from ML_management.mlmanagement import mlmanagement, variables
from ML_management.mlmanagement.module_finder import ModuleFinder
from ML_management.mlmanagement.visibility_options import VisibilityOptions
from ML_management.model.model_type_to_methods_map import ModelMethodName
from ML_management.model.patterns.model_pattern import Model
from ML_management.model.patterns.rich_python_model import RichPythonModel

default_dataset_loader_pattern = OneDatasetLoaderPattern()


class BaseExecutor(RichPythonModel, ABC):
    """Define custom job executor."""

    DEFAULT_ROLE = DEFAULT_ROLE

    def __init__(
        self,
        executor_models_pattern: Union[OneModelPattern, ArbitraryModelsPattern],
        executor_dataset_loaders_pattern: Union[
            OneDatasetLoaderPattern, ArbitraryDatasetLoaderPattern
        ] = default_dataset_loader_pattern,
    ) -> None:
        """
        Init Executor class.

        :param executor_name: The name of the executor
        :param executor_models_pattern: Pattern of interaction with models
        :param executor_datasets_pattern: Pattern of datasets usage
        """
        if not isinstance(executor_models_pattern, OneModelPattern) and not isinstance(
            executor_models_pattern, ArbitraryModelsPattern
        ):
            raise TypeError(
                "param executor_models_pattern must be instance of OneModelPattern or ArbitraryModelsPattern"
            )
        if not isinstance(executor_dataset_loaders_pattern, OneDatasetLoaderPattern) and not isinstance(
            executor_dataset_loaders_pattern, ArbitraryDatasetLoaderPattern
        ):
            raise TypeError(
                "param executor_datasets_pattern must be instance of OneDatasetPattern or ArbitraryDatasetPattern"
            )
        self.upload_model_modes, self.desired_model_methods = executor_models_pattern.serialize()
        self.desired_dataset_loader_methods = executor_dataset_loaders_pattern.serialize()
        for methods_list in self.desired_dataset_loader_methods.values():
            if DatasetLoaderMethodName.get_dataset not in methods_list:
                raise RuntimeError(
                    "Every dataset loader must have DatasetLoaderMethodName.get_dataset method in desired methods."
                )

        # That parameters will be set automatically while loading the model.
        """
        :param self.artifacts: local path to artifacts.
        """
        self.artifacts: str

        # That parameter will be set automatically in job before the 'execute' func would be executed.
        self.role_dataset_loader_map: Dict[str, DatasetLoaderPattern] = {}
        self.role_model_map: Dict[str, Model] = {}
        self.role_dataset_map: Dict[str, Any] = {}
        self.dataset_loader_method_parameters_dict: Dict[str, Dict[DatasetLoaderMethodName, dict]] = {}
        self.model_method_parameters_dict: Dict[str, Dict[ModelMethodName, dict]] = {}
        self.model_method_schemas = {}
        """
        :param self.role_model_map: role to model map
        :param self.role_dataset_loader_map: role to dataset loader map
        :param self.role_dataset_map: role to dataset map.
            Dataset is an object obtained as a result of calling the 'get_dataset' function
            from a dataset loader with the same role.
        :param self.model_method_parameters_dict: the dict of parameters for each desired_model_methods.
            One could use it in execute() function like that:

                def execute(self):
                    self.role_model_map["role_model"].train_function(
                        **self.model_method_parameters_dict["role_model"][ModelMethodName.train_function]
                    )

            In that case method 'execute' calls train_function method of the model with corresponding parameters
            for that method.
        :param self.dataset_loader_method_parameters_dict: the dict of params for each desired_dataset_loader_methods.
            One could use it in execute() function like that:

                def execute(self):
                    self.role_dataset_loader_map["role_dataset"].get_dataset(
                        **self.dataset_loader_method_parameters_dict["role_dataset"][DatasetLoaderMethodName.get_dataset]
                    )

            In that case method 'execute' calls get_dataset method of the dataset loader with corresponding parameters
            for that method.
        """

    @abstractmethod
    def execute(self, **executor_params):
        """
        Do execution step.

        Parameter self.role_model_map with the desired model will be set
        automatically in the job before 'execute' execution.
        To get data_path use self.data_path parameter, which also will be set in the job.
        'executor_methods_params' are executor parameters. One has to define it as ordinary kwargs with type annotation.
        Also, you could use self.model_methods_parameters for call desired model method with right params.
        return param: artifacts: A dictionary containing ``<name, artifact_uri>`` entries.
                      For example, consider the following ``artifacts`` dictionary::

                        {
                            "my_file": "s3://my-bucket/path/to/my/file",
                            "my_file2": "/home/username/path/to/my/file"
                        }

                      In this case, the ``"my_file"`` artifact is downloaded from S3.
                      The ``"my_file2"`` artifact is downloaded from local path.

                      If ``None``, no artifacts are added to the model.
        """
        raise NotImplementedError

    def upload_executor(
        self,
        executor_name: str,
        pip_requirements=None,
        description: Optional[str] = None,
        extra_pip_requirements=None,
        conda_env=None,
        artifacts: Optional[dict] = None,
        visibility: VisibilityOptions = VisibilityOptions.PRIVATE,
        extra_modules_names: Optional[List[str]] = None,
        used_modules_names: Optional[List[str]] = None,
        linter_check: bool = True,
        start_build: bool = False,
    ) -> None:
        """
        Upload wrapper to MLmanagement server.

        :param pip_requirements: {{ pip_requirements }}

        :param extra_pip_requirements: {{ extra_pip_requirements }}
        `pip_requirements` and 'extra_pip_requirements' must be either a string path to a pip requirements file on the
            local filesystem or an iterable of pip requirement strings.

        :param conda_env: {{ conda_env }}
        'conda_env' must be a dict specifying the conda environment for this model.

        :param artifacts: A dictionary containing ``<name, artifact_uri>`` entries. Remote artifact URIs
                          are resolved to absolute filesystem paths, producing a dictionary of
                          ``<name, absolute_path>`` entries. ``python_model`` can reference these
                          resolved entries as the ``artifacts`` property of the ``context`` parameter
                          in :func:`PythonModel.load_context() <mlflow.pyfunc.PythonModel.load_context>`
                          and :func:`PythonModel.predict() <mlflow.pyfunc.PythonModel.predict>`.
                          For example, consider the following ``artifacts`` dictionary::

                            {
                                "my_file": "s3://my-bucket/path/to/my/file"
                            }

                          In this case, the ``"my_file"`` artifact is downloaded from S3. The
                          ``python_model`` can then refer to ``"my_file"`` as an absolute filesystem
                          path via ``context.artifacts["my_file"]``.

                          If ``None``, no artifacts are added to the executor.

        :param visibility: either a private or public executor.

        :param extra_modules_names: names of modules that should be pickled by value
            in addition to auto-detected modules.

        :param used_modules_names: modules that should be pickled by value, disables the auto-detection of modules.

        :param linter_check: if True, check code of the executor by linter.

        :param start_build: if set to True, start job to create docker image.
            This parameter may be True only if there is no models for executor.
        """
        old_experiment_name = variables.active_experiment_name
        if (self.desired_model_methods or self.upload_model_modes) and start_build:
            raise RuntimeError("Parameter start_build=True is acceptable only if there is no models for executor.")
        mlmanagement.set_experiment(variables.EXPERIMENT_NAME_FOR_EXECUTOR, visibility=VisibilityOptions.PUBLIC)
        try:
            with mlmanagement.start_run(nested=True):
                mlmanagement.log_model(
                    artifact_path="",
                    description=description,
                    artifacts=artifacts,
                    python_model=self,
                    registered_model_name=executor_name,
                    pip_requirements=pip_requirements,
                    extra_pip_requirements=extra_pip_requirements,
                    conda_env=conda_env,
                    visibility=visibility,
                    extra_modules_names=extra_modules_names,
                    used_modules_names=used_modules_names,
                    root_module_name=ModuleFinder.get_my_caller_module_name(),
                    linter_check=linter_check,
                    start_build=start_build,
                )
        except Exception as err:
            raise err
        finally:
            variables.active_experiment_name = old_experiment_name

    @property
    def model(self) -> Model:
        """Property returning a single model.

        :return: python model
        """
        if len(self.role_model_map) != 1:
            raise RuntimeError("This attribute can be used only with 1 model")
        return list(self.role_model_map.values())[0]

    @model.setter
    def model(self, model):
        """Property to change the model.

        :param: python model
        """
        if len(self.role_model_map) != 1:
            raise RuntimeError("This attribute can be used only with 1 model")
        self.role_model_map[list(self.role_model_map.keys())[0]] = model

    @property
    def dataset_loader(self) -> DatasetLoaderPattern:
        """Property returning a single dataset loader.

        :return: dataset loader object
        """
        if len(self.role_dataset_loader_map) != 1:
            raise RuntimeError("This attribute can be used only with 1 dataset loader")
        return list(self.role_dataset_loader_map.values())[0]

    @dataset_loader.setter
    def dataset_loader(self, dataset_loader: DatasetLoaderPattern):
        """Property to change the dataset loader.

        :param: dataset loader object
        """
        if len(self.role_dataset_loader_map) != 1:
            raise RuntimeError("This attribute can be used only with 1 dataset loader")
        self.role_dataset_loader_map[list(self.role_dataset_loader_map.keys())[0]] = dataset_loader

    @property
    def model_methods_parameters(self) -> Dict[ModelMethodName, dict]:
        """Property for the dictionary wrapper.

        :return: the dict of parameters for each desired_model_methods
        """
        if len(self.model_method_parameters_dict) != 1:
            raise RuntimeError("This attribute can be used only with 1 model")
        return list(self.model_method_parameters_dict.values())[0]

    @property
    def model_method_schema(self) -> Dict[ModelMethodName, dict]:
        """Property for the dictionary wrapper.

        :return: schema for each desired_model_methods
        """
        if len(self.model_method_schemas) != 1:
            raise RuntimeError("This attribute can be used only with 1 model")
        return list(self.model_method_schemas.values())[0]

    @property
    def dataset_loader_methods_parameters(self) -> Dict[DatasetLoaderMethodName, dict]:
        """Property for the dictionary wrapper.

        :return: the dict of parameters for each desired_dataset_loader_methods
        """
        if len(self.dataset_loader_method_parameters_dict) != 1:
            raise RuntimeError("This attribute can be used only with 1 model")
        return list(self.dataset_loader_method_parameters_dict.values())[0]

    @property
    def dataset(self):
        """Property returning a single dataset.

        :return: dataset object
        """
        if len(self.role_dataset_map) != 1:
            raise RuntimeError("This attribute can be used only with 1 dataset")
        return list(self.role_dataset_map.values())[0]

    @dataset.setter
    def dataset(self, dataset: Any):
        """Property to change the dataset.

        :param: dataset object
        """
        if len(self.role_dataset_map) != 1:
            raise RuntimeError("This attribute can be used only with 1 dataset")
        self.role_dataset_map[list(self.role_dataset_map.keys())[0]] = dataset
