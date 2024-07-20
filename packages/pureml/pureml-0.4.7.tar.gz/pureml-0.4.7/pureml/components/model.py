import json
import os
import zipfile

import requests
from rich import print

from pureml.cli.helpers import get_auth_headers
from pureml.packaging import load_model, save_model
from pureml.schema.config import ConfigKeys
from pureml.schema.request import AcceptHeader, ContentTypeHeader
from pureml.schema.storage import StorageSchema
from pureml.storage import upload_and_get_provider_and_path
from pureml.utils.hash import generate_hash_for_file
from pureml.utils.logger import get_logger
from pureml.utils.readme import load_readme
from pureml.utils.routes import (
    check_model_hash_url,
    model_details_url,
    model_init_url,
    model_list_urls,
    model_register_url,
    model_version_details_url,
)
from pureml.utils.version_utils import parse_version_label
from pureml.schema.model import ModelSchema
from . import get_org_id

config_keys = ConfigKeys
storage = StorageSchema().get_instance()
logger = get_logger("sdk.components.model")


def check_model_hash(hash: str, label: str):
    logger.info("Checking model hash")

    name, _ = parse_version_label(label)

    get_org_id()
    ModelSchema()

    url = check_model_hash_url(name)
    headers = get_auth_headers(
        content_type=ContentTypeHeader.APP_FORM_URL_ENCODED
    )

    data = {"hash": hash}

    data = json.dumps(data)

    response = requests.post(url, data=data, headers=headers)

    hash_exists = False

    if response.ok:
        hash_exists = response.json()["data"][0]

    logger.info(f"Hash exists: {hash_exists}")
    return hash_exists


def list():
    """This function will return a list of all the modelst

    Returns
    -------
        A list of all the models

    """
    logger.info("Fetching list of models")

    get_org_id()
    ModelSchema()

    url = model_list_urls()

    headers = get_auth_headers(
        content_type=ContentTypeHeader.APP_FORM_URL_ENCODED
    )

    response = requests.get(url, headers=headers)

    if response.ok:
        # print(f"[green]Obtained list of models")

        response_text = response.json()
        model_list = response_text["data"]
        # print(model_list)

        return model_list
    else:
        logger.error("Unable to obtain the list of models", response=response)
        print(f"[orange]Unable to obtain the list of models!")

    return


def init(label: str, type: str = "ML", readme: str = None):
    logger.info("Initializing model")
    name, _ = parse_version_label(label)

    get_org_id()
    ModelSchema()

    if readme is None:
        readme = ModelSchema().PATH_MODEL_README

    file_content, file_type = load_readme(path=readme)

    url = model_init_url()

    headers = get_auth_headers(content_type=ContentTypeHeader.APP_JSON)

    data = {
        "name": name,
        "readme": {"file_type": file_type, "content": file_content},
        "type": type,
    }

    data = json.dumps(data)

    # files = {"file": (readme, open(readme, "rb"), file_type)}

    response = requests.post(url, data=data, headers=headers)
    # response = requests.post(url, data=data, headers=headers, files=files)

    if response.ok:
        print(f"[green]Model has been created!")

        return True
    else:
        logger.error("Unable to create the model", response=response)
        print(f"[orange]Model has not been created!")

        return False


def register(
    label,
    model=None,
    model_path=None,
    model_framework="mlflow",
    is_empty: bool = False,
):
    project_root = os.path.abspath(os.path.dirname(__file__))

    logger.info("Registering model")
    name, _ = parse_version_label(label)
    get_org_id()
    model_schema = ModelSchema()

    if model is not None and model_path is None:
        model_file_name = ".".join([name, "pkl"])
        model_path = os.path.join(
            model_schema._paths.PATH_MODEL_DIR, model_file_name
        )
        os.makedirs(model_schema._paths.PATH_MODEL_DIR, exist_ok=True)
        save_model(model, name, model_path=model_path)
        model_hash = generate_hash_for_file(
            file_path=model_path, name=name, is_empty=is_empty
        )

    if model is None and model_path is not None:
        full_model_path = os.path.abspath(model_path.rstrip("/"))
        if os.path.exists(full_model_path):
            zip_file_path = full_model_path + ".zip"
            with zipfile.ZipFile(
                zip_file_path, "w", zipfile.ZIP_DEFLATED
            ) as zipf:
                if os.path.isfile(full_model_path):
                    zipf.write(
                        full_model_path, os.path.basename(full_model_path)
                    )
                elif os.path.isdir(full_model_path):
                    for root, dirs, files in os.walk(full_model_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            zipf.write(
                                file_path,
                                os.path.relpath(file_path, full_model_path),
                            )
            model_file_name = ".".join([name, "zip"])
            model_save_path = os.path.join(
                model_schema._paths.PATH_MODEL_DIR, model_file_name
            )
            os.makedirs(model_schema._paths.PATH_MODEL_DIR, exist_ok=True)
            save_model(
                zip_file_path,
                name,
                model_path=model_save_path,
                model_framework=model_framework,
            )
            model_hash = generate_hash_for_file(
                file_path=zip_file_path, name=name, is_empty=is_empty
            )
        else:
            print(
                f"Error: The provided model_path '{full_model_path}' does not exist."
            )

    model_exists = model_status(label)

    if not model_exists:
        model_created = init(label)
        # print("model_created", model_created)
        if not model_created:
            print("[orange] Unable to register the model")
            return False, model_hash, "latest"

    model_exists_remote = check_model_hash(hash=model_hash, label=label)

    if model_exists_remote:
        print(
            f"[green]Model already exists. Not registering a new version![/green]"
        )
        return True, model_hash, "latest"
    else:

        url = model_register_url(name)
        headers = get_auth_headers(
            content_type=None, accept=AcceptHeader.APP_JSON
        )

        # files = {"file": (model_file_name, open(model_path, "rb"))}
        provider, file_path = upload_and_get_provider_and_path(
            model_path, opt_base_dir="models"
        )

        data = {
            "name": name,
            "hash": model_hash,
            "is_empty": is_empty,
            "storage": provider,
            "file_path": file_path,
        }

        response = requests.post(
            url, files={"foo": "bar"}, data=data, headers=headers
        )

        if response.ok:

            model_version = None

            # print(response.json())
            try:
                print(f"[green]Model has been registered!")

                model_version = response.json()["data"][0]["version"]
                print("Model version: ", model_version)
                model_label = ":".join([name, model_version])
                print("Model label: ", model_label)

                # reset_config(key=config_keys.model.value)
            except Exception as e:
                print(
                    "[orange] Incorrect json response. Model has not been registered"
                )
                print(e)

            return True, model_hash, model_version

        else:
            logger.error("Unable to register the model", response=response)
            print(f"[orange]Model has not been registered!")
            print(response.text)

        return False, model_hash, None


def model_status(label: str):
    logger.info("Checking model status")
    name, _ = parse_version_label(label)

    model_details = details(label=label)

    logger.info(f"Model details: {model_details}")
    if model_details:
        return True
    else:
        return False


def details(label: str):
    """It fetches the details of a model.

    Parameters
    ----------
    name : str
        The name of the model
    version: str
        The version of the model
    Returns
    -------
        The details of the model.

    """
    logger.info("Fetching model details")

    name, _ = parse_version_label(label)

    get_org_id()
    ModelSchema()

    url = model_details_url(name)

    headers = get_auth_headers(
        content_type=ContentTypeHeader.APP_FORM_URL_ENCODED,
        accept=AcceptHeader.APP_JSON,
    )

    response = requests.get(url, headers=headers)
    # print(response.url)
    # print(response.text)

    if response.ok:
        # print(f"[green]Model details have been fetched")
        response_text = response.json()
        model_details = response_text["data"][0]
        # print(model_details)

        return model_details

    else:
        logger.error("Unable to fetch model details", response=response)
        print(f"[orange]Model details have not been found")
        return


def version_details(label: str):
    """It fetches the details of a model.

    Parameters
    ----------
    name : str
        The name of the model
    version: str
        The version of the model
    Returns
    -------
        The details of the model.

    """
    logger.info("Fetching model version details")

    name, version = parse_version_label(label)

    get_org_id()
    ModelSchema()

    url = model_version_details_url(name)

    headers = get_auth_headers(
        content_type=ContentTypeHeader.APP_FORM_URL_ENCODED
    )

    response = requests.get(url, headers=headers)

    if response.ok:
        # print(f"[green]Model Version details have been fetched")
        response_text = response.json()
        model_details = response_text["data"][0]
        # print(model_details)

        return model_details

    else:
        logger.error("Unable to fetch model version details", response=response)
        print(f"[orange]Model details have not been found")
        return


def fetch(label: str):
    """This function fetches a model from the server and returns it as a `Model` object

    Parameters
    ----------
    name : str, optional
        The name of the model you want to fetch.
    version: str
        The version of the model

    Returns
    -------
        The model is being returned.

    """
    logger.info("Fetching model")

    name, version = parse_version_label(label)

    get_org_id()

    model_details = version_details(label=label)

    if model_details is None:
        print(f"[orange]Unable to fetch Model version")
        return

    is_empty = model_details["is_empty"]

    if is_empty:
        print("[orange]Model file is not registered to the version")
        return

    # storage_path = model_details["path"]["source_path"]
    # storage_source_type = model_details["path"]["source_type"]["public_url"]

    # model_url = urljoin(storage_source_type, storage_path)

    # print(f"Line 362. model.py: {model_details}")
    model_url = model_details["path"]
    source_type = model_details["source_type"]

    logger.info(f"Model URL: {model_url}")
    logger.info(f"Source type: {source_type}")
    model_url = model_url.strip()
    if source_type != "file":
        response = requests.get(model_url)

        if response.ok:
            model_bytes = response.content
            with open("temp_model.pure", "wb") as file:
                file.write(model_bytes)

            model = load_model(model_path="temp_model.pure")

            # print(f"[green]Model version has been fetched")
            return model
        else:
            logger.error("Unable to fetch Model version", response=response)
            print(f"[orange]Unable to fetch Model version")
            return
    else:
        if os.path.exists(model_url):
            model = load_model(model_path=model_url)

            return model
        else:
            logger.error(
                "Unable to fetch Model from local path", path=model_url
            )
            print(f"[orange]Unable to fetch Model")
            return


# def delete(label: str) -> str:
#     """This function deletes a model from the project

#     Parameters
#     ----------
#     name : str
#         The name of the model you want to delete
#     version : str
#         The version of the model to delete.

#     """

#     name, _ = parse_version_label(label)

#     user_token = get_token()
#     org_id = get_org_id()
#     model_schema = ModelSchema()

#     url = "models/{}/delete".format(org_id, name)
#     url = urljoin(model_schema.backend.BASE_URL, url)

#     headers = {
#         "Content-Type": ContentTypeHeader.APP_FORM_URL_ENCODED.value,
#         "Authorization": "Bearer {}".format(user_token),
#     }

#     response = requests.delete(url, headers=headers)

#     if response.ok:
#         print(f"[green]Model has been deleted")

#     else:
#         print(f"[orange]Unable to delete Model")

#     return response.text


def serve_model():
    pass
