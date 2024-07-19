"""Base model template."""
from mlflow.pyfunc import PythonModel


class RichPythonModel(PythonModel):
    """Placeholder for mflow PythonModel with realization of predict function."""

    def predict(self, **kwargs):
        """Placeholder for mlflow model abstract method."""
        pass
