from enum import Enum

from pydantic import BaseModel

from .backend import BackendSchema
from .paths import PathSchema


class LogKeys(Enum):
    metrics = "metrics"
    params = "params"
    figure = "figure"
    predict = "predict"
    requirements = "requirements"
    resources = "resources"


class LogSchema(BaseModel):
    _paths: PathSchema = PathSchema().get_instance()
    _backend: BackendSchema = BackendSchema().get_instance()
    key: LogKeys = LogKeys.metrics
