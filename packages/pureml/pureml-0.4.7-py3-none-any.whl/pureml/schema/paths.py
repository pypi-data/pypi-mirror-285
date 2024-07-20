import os
from typing import ClassVar

from pydantic import ConfigDict, model_validator

from .singleton import Singleton_BaseModel

# project_path = os.getcwd()
# if os.path.exists(project_path / "puremlconfig.yaml"):
#     puremlconfig = PureMLConfigYML(project_path / "puremlconfig.yaml")
# else:
#     puremlconfig = None


class PathSchema(Singleton_BaseModel):

    # Probably for future relative path configuration using config file
    # if puremlconfig is not None:
    #     if str(puremlconfig.data["repository"]).startswith("file://"):
    #         relative_base_url = str(puremlconfig.data["repository"]).removeprefix("file://")

    PATH_PUREML_RELATIVE: ClassVar[str] = ".pureml"
    PATH_PREDICT_DIR_RELATIVE: ClassVar[str] = "predict"

    PATH_USER_TOKEN: ClassVar[str] = os.path.join(
        os.path.expanduser("~"), PATH_PUREML_RELATIVE, "token"
    )

    PATH_USER_PROJECT_DIR: ClassVar[str] = os.path.join(
        os.getcwd(), PATH_PUREML_RELATIVE
    )

    PATH_USER_PROJECT: ClassVar[str] = os.path.join(
        PATH_USER_PROJECT_DIR, "pure.project"
    )

    PATH_CONFIG: ClassVar[str] = os.path.join(
        PATH_USER_PROJECT_DIR, "config.pkl"
    )  # 'temp.yaml'

    PATH_ARTIFACT_DIR: ClassVar[str] = os.path.join(PATH_USER_PROJECT_DIR, "artifacts")
    PATH_ARRAY_DIR: ClassVar[str] = os.path.join(PATH_USER_PROJECT_DIR, "array")
    PATH_AUDIO_DIR: ClassVar[str] = os.path.join(PATH_USER_PROJECT_DIR, "audio")
    PATH_FIGURE_DIR: ClassVar[str] = os.path.join(PATH_USER_PROJECT_DIR, "figure")
    PATH_TABULAR_DIR: ClassVar[str] = os.path.join(PATH_USER_PROJECT_DIR, "tabular")
    PATH_VIDEO_DIR: ClassVar[str] = os.path.join(PATH_USER_PROJECT_DIR, "video")
    PATH_IMAGE_DIR: ClassVar[str] = os.path.join(PATH_USER_PROJECT_DIR, "image")

    PATH_DATASET_DIR: ClassVar[str] = os.path.join(PATH_USER_PROJECT_DIR, "dataset")

    PATH_MODEL_DIR: ClassVar[str] = os.path.join(PATH_USER_PROJECT_DIR, "model")

    PATH_PREDICT_DIR: ClassVar[str] = os.path.join(
        PATH_USER_PROJECT_DIR, PATH_PREDICT_DIR_RELATIVE
    )
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @model_validator(mode="after")
    @classmethod
    def create_base_folders(cls, values):
        os.makedirs(values.PATH_USER_PROJECT_DIR, exist_ok=True)

        return values

    @model_validator(mode="after")
    @classmethod
    def create_log_folders(cls, values):
        os.makedirs(values.PATH_ARTIFACT_DIR, exist_ok=True)
        os.makedirs(values.PATH_ARRAY_DIR, exist_ok=True)
        os.makedirs(values.PATH_AUDIO_DIR, exist_ok=True)
        os.makedirs(values.PATH_FIGURE_DIR, exist_ok=True)
        os.makedirs(values.PATH_TABULAR_DIR, exist_ok=True)
        os.makedirs(values.PATH_VIDEO_DIR, exist_ok=True)
        os.makedirs(values.PATH_IMAGE_DIR, exist_ok=True)

        return values

    @model_validator(mode="after")
    @classmethod
    def create_model_folders(cls, values):
        os.makedirs(values.PATH_MODEL_DIR, exist_ok=True)

        return values

    @model_validator(mode="after")
    @classmethod
    def create_dataset_folders(cls, values):
        os.makedirs(values.PATH_DATASET_DIR, exist_ok=True)

        return values

    @model_validator(mode="after")
    @classmethod
    def create_predict_folders(cls, values):
        os.makedirs(values.PATH_PREDICT_DIR, exist_ok=True)

        return values
