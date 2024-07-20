import os
import pickle as pkl
import tempfile

# from pydantic import BaseModel
import typing
import zipfile
from abc import ABC

import joblib
from pydantic import BaseModel, model_validator

from .model_framework import ModelFramework, ModelFrameworkType
from .model_packaging.catboost import CatBoost
from .model_packaging.custom import Custom
from .model_packaging.keras import Keras
from .model_packaging.lightgbm import LightGBM
from .model_packaging.pytorch import Pytorch
from .model_packaging.pytorch_tabnet import PytorchTabnet
from .model_packaging.sklearn import SKLearn
from .model_packaging.xgboost import XGBoost
from .packaging_utils import get_file_size

# from . import MODEL_FRAMEWORKS_BY_TYPE, SUPPORTED_MODEL_FRAMEWORKS


MODEL_FRAMEWORKS_BY_TYPE = {
    ModelFrameworkType.SKLEARN: SKLearn(),
    ModelFrameworkType.XGBOOST: XGBoost(),
    ModelFrameworkType.LIGHTGBM: LightGBM(),
    ModelFrameworkType.CATBOOST: CatBoost(),
    ModelFrameworkType.KERAS: Keras(),
    # ModelFrameworkType.HUGGINGFACE_TRANSFORMER: HuggingfaceTransformer(),
    ModelFrameworkType.PYTORCH: Pytorch(),
    ModelFrameworkType.PYTORCH_TABNET: PytorchTabnet(),
    ModelFrameworkType.CUSTOM: Custom(),
}


SUPPORTED_MODEL_FRAMEWORKS = [
    ModelFrameworkType.SKLEARN,
    ModelFrameworkType.XGBOOST,
    ModelFrameworkType.LIGHTGBM,
    ModelFrameworkType.KERAS,
    ModelFrameworkType.TENSORFLOW,
    # ModelFrameworkType.HUGGINGFACE_TRANSFORMER,
    ModelFrameworkType.PYTORCH,
    ModelFrameworkType.PYTORCH_TABNET,
    ModelFrameworkType.CUSTOM,
]


class Model(ABC, BaseModel):
    model_config: typing.Optional[dict] = {}
    model_config["protected_namespaces"] = ()

    model: typing.Any = None
    model_name: str = "model"
    model_path: str = None
    model_class: str = None
    model_framework: typing.Any = None
    model_requirements: list = None

    # By default predict function of a framework should be assigned to here
    # If a user gives a predict function, assign it here
    predict: typing.Any = None

    @model_validator(mode="before")
    def set_fields(values):

        return values

    # @staticmethod
    def from_dict(self, model_config: dict):

        # self.model = self.model_config["model"]
        # model_name = model_config_dict['model_name'],
        # self.model_framework = self.model_config["model_framework"]
        # self.model_requirements = self.model_config["model_requirements"]
        self.model = model_config["model"]
        self.model_framework = model_config["model_framework"]
        self.model_requirements = model_config["model_requirements"]
        if self.model_framework == "mlfow":
            print(f"Model Framework is Flow")
        else:
            pass
        #print(f"self.model :{self.model}")
        #print(f"self.model_framework: {self.model_framework}")
        #print(f"self.model_requirements: {self.model_requirements}")

    def generate_model_config(self):

        model_config_generator = {
            "model": self.model,
            "model_framework": self.model_framework,
            "model_requirements": self.model_requirements,
            "model_size": get_file_size(pkl.dumps(self.model)),
        }

        return model_config_generator

    def model_framework_from_model(self) -> ModelFramework:
        self.model_class = self.model.__class__
        model_framework = self.model_framework_from_model_class(self.model_class)

        return model_framework

    def model_framework_from_model_class(self, model_class) -> ModelFramework:

        for framework in MODEL_FRAMEWORKS_BY_TYPE.values():

            if framework.supports_model_class(model_class):
                return framework

        # raise FrameworkNotSupportedError(
        #     "Model must be one of "
        #     + "/".join([t.value for t in SUPPORTED_MODEL_FRAMEWORKS])
        # )
        framework = ModelFrameworkType.CUSTOM
        return framework

    def save_model(self):

        self.model_framework = self.model_framework_from_model()
        self.model_requirements = self.model_framework.get_requirements()

        #print(f"self.model_framework. line 127: {self.model_framework}")
        #print(f"self.model_requirements: {self.model_requirements}")

        # self.model_framework = ''
        # self.model_requirements = []

        # self.model_config = self.generate_model_config() #Error When Executed this: ValueError: "Model" object has no field "model_config"

        model_config = self.generate_model_config()
        joblib.dump(model_config, self.model_path)
        #print(f"self.model_path: {self.model_path}")
        return self.model_path

    def load_model(self):
        model_config = joblib.load(self.model_path)
        self.from_dict(model_config)
        try:
            if self.model.endswith(".zip"):
                with zipfile.ZipFile(self.model, "r") as zip_ref:
                    with tempfile.TemporaryDirectory() as temp_dir:
                        zip_ref.extractall(temp_dir)
                        extracted_files = []
                        for root, dirs, files in os.walk(temp_dir):
                            for file in files:
                                file_path = os.path.join(root, file)
                                extracted_files.append(file_path)
                        #print("Extracted files:", extracted_files)
                        self.model = extracted_files
                        return self.model
        except Exception:
            pass
        return self.model
