import os
from typing import ClassVar

from pydantic import BaseModel, ConfigDict

from .backend import BackendSchema
from .paths import PathSchema


class FastAPISchema(BaseModel):
    # paths: PathSchema = PathSchema().get_instance()
    paths: PathSchema = PathSchema()
    PATH_FASTAPI_FILE: ClassVar = os.path.join(
        paths.PATH_PREDICT_DIR, "fastapi_server.py"
    )
    PORT_FASTAPI: ClassVar = 8005  # Same port as docker server
    API_IP_HOST: ClassVar = "0.0.0.0"
    model_config = ConfigDict(arbitrary_types_allowed=True)


class DockerSchema(BaseModel):
    # paths: PathSchema = PathSchema().get_instance()
    # backend: BackendSchema = BackendSchema().get_instance()
    paths: PathSchema = PathSchema()
    backend: BackendSchema = BackendSchema()
    PATH_DOCKER_IMAGE: ClassVar = os.path.join(paths.PATH_PREDICT_DIR, "Dockerfile")
    PATH_DOCKER_CONFIG: ClassVar = os.path.join(
        paths.PATH_PREDICT_DIR, "DockerConfig.yaml"
    )
    PORT_DOCKER: ClassVar = FastAPISchema().PORT_FASTAPI  # Same port as fastapi server
    PORT_HOST: ClassVar = 8000
    BASE_IMAGE_DOCKER: ClassVar = "python:3.8-slim"
    API_IP_DOCKER: ClassVar = FastAPISchema().API_IP_HOST
    API_IP_HOST: ClassVar = "0.0.0.0"
    model_config = ConfigDict(arbitrary_types_allowed=True)
