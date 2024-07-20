import json
import os
from urllib.parse import urljoin

import requests
from joblib import Parallel, delayed
from rich import print

from pureml.cli.helpers import get_auth_headers
from pureml.components import get_org_id
from pureml.schema.backend import BackendSchema
from pureml.schema.config import ConfigKeys
from pureml.schema.log import LogSchema
from pureml.schema.paths import PathSchema
from pureml.schema.request import AcceptHeader, ContentTypeHeader
from pureml.schema.storage import StorageSchema
from pureml.utils.config import reset_config
from pureml.utils.pipeline import add_pip_req_to_config
from pureml.utils.version_utils import parse_version_label

path_schema = PathSchema()
backend_schema = BackendSchema()
# path_schema = PathSchema().get_instance()
# backend_schema = BackendSchema().get_instance()
post_key_pip_req = LogSchema().key.requirements.value
config_keys = ConfigKeys
storage = StorageSchema().get_instance()


def post_pip_requirement(file_paths, model_name: str, model_version: str):
    org_id = get_org_id()

    url = "org/{}/model/{}/version/{}/logfile".format(
        org_id, model_name, model_version
    )
    url = urljoin(backend_schema.BASE_URL, url)

    headers = get_auth_headers(content_type=None, accept=AcceptHeader.APP_JSON)

    files = []
    provider = ""
    for file_name, file_path in file_paths.items():
        # print("filename", file_name)

        if os.path.isfile(file_path):
            # files.append(("file", (file_name, open(file_path, "rb"))))
            provider, file_path = upload_and_get_provider_and_path(
                file_path, opt_base_dir="pip_requirements"
            )
            files.append(file_path)

        else:
            print(
                "[orange] pip_requirement",
                file_name,
                "does not exist at the given path",
            )

    data = {
        "data": file_paths,
        "key": post_key_pip_req,
        "storage": provider,
        "file_path_json_array": json.dumps(files),
    }

    # data = json.dumps(data)

    response = requests.post(
        url, data=data, files={"foo": "bar"}, headers=headers
    )

    if response.ok:
        print("[green]pip_requirement Function has been registered!")
        reset_config(key=config_keys.pip_requirement.value)

    else:
        print("[orange]pip_requirement Function has not been registered!")

    return response


def add(label: str = None, path: str = None) -> str:

    model_name, model_version = parse_version_label(label)

    file_paths = {post_key_pip_req: path}

    add_pip_req_to_config(
        values=path,
        model_name=model_name,
        model_version=model_version,
    )

    if (
        model_name is not None
        and model_version is not None
        and model_version is not None
    ):
        response = post_pip_requirement(
            file_paths=file_paths,
            model_name=model_name,
            model_version=model_version,
        )

        print(response.text)

    # return response.text


def details(label: str):
    model_name, model_version = parse_version_label(label)
    org_id = get_org_id()

    url = f"org/{org_id}/model/{model_name}/version/{model_version}/log"
    url = urljoin(backend_schema.BASE_URL, url)

    headers = get_auth_headers(content_type=None, accept=AcceptHeader.APP_JSON)

    response = requests.get(url, headers=headers)

    if response.ok:
        # T-1161 standardize api response to contains Models as a list
        response_text = response.json()
        details = response_text["data"]

        # print(model_details)

        return details

    else:
        print("[orange]Unable to fetch pip_requirement file!")
        return


def fetch(label: str):
    model_name, model_version = parse_version_label(label)

    get_org_id()

    def fetch_pip_requirement(file_details):

        file_name, url = file_details

        save_path = os.path.join(path_schema.PATH_PREDICT_DIR, file_name)
        print("save path", save_path)

        headers = get_auth_headers(
            content_type=ContentTypeHeader.APP_FORM_URL_ENCODED,
            accept=AcceptHeader.APP_JSON,
        )

        # print("figure url", url)

        # response = requests.get(url, headers=headers)
        response = requests.get(url)

        # print(response.status_code)

        if response.ok:
            print(f"[green] pip_requirement file {file_name} has been fetched")

            save_dir = os.path.dirname(save_path)

            os.makedirs(save_dir, exist_ok=True)

            pip_requirement_bytes = response.content

            open(save_path, "wb").write(pip_requirement_bytes)

            print(
                f"[green] pip_requirement file {file_name} has been stored at {save_path}"
            )

            return response.text
        else:
            print("[orange] Unable to fetch the pip_requirement")

            return response.text

    pip_requirement_details = details(label=label)

    if pip_requirement_details is None:
        return

    # pred_urls = give_pip_requirement_urls(details=pip_requirement_details)
    pred_urls = give_pip_requirement_url(
        details=pip_requirement_details, key=post_key_pip_req
    )

    if len(pred_urls) == 1:

        res_text = fetch_pip_requirement(pred_urls[0])

    else:
        res_text = Parallel(n_jobs=-1)(
            delayed(fetch_pip_requirement)(pred_url) for pred_url in pred_urls
        )


def give_pip_requirement_url(details, key: str):
    """
    Retrieve the URL of the pip requirement file based on the provided details and key.

    Args:
        details (list): A list of dictionaries containing details.
        key (str): The key to search for in the details list.

    Returns:
        list: A list of lists containing the source path and file URL of the pip requirement file.
    """

    pip_requirement_paths = []
    # file_url = None
    source_path = None
    file_url = None
    # print(details)

    if details is not None:

        for det in details:
            # print(det["key"])
            if det["key"] == key:
                source_path = det["key"]
                file_url = det["data"]
                source_path = ".".join([source_path, "txt"])
                # source_path = os.path.join(path_schema.PATH_PREDICT_DIR, source_path)
                pip_requirement_paths.append([source_path, file_url])

                # print(source_path, file_url)

                return pip_requirement_paths
    print("[orange] Unable to find the pip_requirement file")

    return pip_requirement_paths
