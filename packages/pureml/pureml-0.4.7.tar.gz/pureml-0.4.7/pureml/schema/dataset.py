import os
from typing import ClassVar

from pydantic import BaseModel

from .backend import BackendSchema
from .paths import PathSchema


class DatasetSchema(BaseModel):

    # _paths: PathSchema = PathSchema().get_instance()
    # _backend: BackendSchema = BackendSchema().get_instance()

    # When Executed the above lines, the following error is thrown:  Is it  pydantic.fields.ModelPrivateAttr
    # So, Created a Class Instance and Accessed them

    _paths: PathSchema = PathSchema()
    _backend: BackendSchema = BackendSchema()
    PATH_DATASET_README: ClassVar = os.path.join(_paths.PATH_DATASET_DIR, "ReadME.md")
    # Since PathSchema is ModelPrivateAttr, it cannot be named directly, We need to use "_" infront of variable name. So, _paths is used instead of paths.

    # Required Type Annotation when accessing ModelPrivateAttr, so used ClassVar
