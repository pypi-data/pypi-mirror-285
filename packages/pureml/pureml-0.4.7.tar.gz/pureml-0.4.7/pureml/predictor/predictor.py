import typing
from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, ConfigDict

from pureml.schema.predict import Input, Output


class BasePredictor(BaseModel, ABC):
    label: str
    model: Any = None
    input: Input
    output: Output = Output()
    requirements_py: list = None
    requirements_sys: list = None
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @abstractmethod
    def load_models(self):
        pass

    @abstractmethod
    def predict(self, **kwargs: typing.Any):
        pass

    # @abstractmethod
    def load_requirements_py(self):
        pass

    # @abstractmethod
    def load_requirements_sys(self):
        pass

    # @abstractmethod
    def load_resources(self):
        pass
