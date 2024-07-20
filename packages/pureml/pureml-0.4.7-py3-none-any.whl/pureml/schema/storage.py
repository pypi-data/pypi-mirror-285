from pydantic import ConfigDict

from pureml.schema.singleton import Singleton_BaseModel


class StorageSchema(Singleton_BaseModel):

    STORAGE: str = "PUREML-STORAGE"
    model_config = ConfigDict(arbitrary_types_allowed=True)
