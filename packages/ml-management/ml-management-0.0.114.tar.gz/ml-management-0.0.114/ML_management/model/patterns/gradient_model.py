"""Class inherits from base class of Model with a specific method for obtaining gradients."""
from abc import ABC, abstractmethod
from typing import Callable

import numpy as np

from ML_management.mlmanagement.jsonschema_inference import SkipJsonSchema
from ML_management.model.patterns import model_pattern


class GradientModel(model_pattern.Model, ABC):
    """Implementation of gradient model."""

    @abstractmethod
    def get_grad(self, loss_fn: SkipJsonSchema[Callable], input_batch: SkipJsonSchema[np.ndarray]) -> np.ndarray:
        """Define get_grad function."""
        raise NotImplementedError
