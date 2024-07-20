import os
from typing import ClassVar

from pydantic import BaseModel

from .backend import BackendSchema
from .paths import PathSchema


class ModelSchema(BaseModel):
    # _paths: PathSchema = PathSchema().get_instance()
    # _backend: BackendSchema = BackendSchema().get_instance()
    _paths: PathSchema = PathSchema()
    _backend: BackendSchema = BackendSchema()
    PATH_MODEL_README: ClassVar = os.path.join(_paths.PATH_MODEL_DIR, "ReadME.md")
    PATH_MODEL: ClassVar = os.path.join(_paths.PATH_MODEL_DIR, "ran.pkl")
