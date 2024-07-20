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
from pureml.schema.predict import PredictSchema
from pureml.schema.request import AcceptHeader, ContentTypeHeader
from pureml.schema.storage import StorageSchema
from pureml.utils.config import reset_config
from pureml.utils.pipeline import add_resource_to_config
from pureml.utils.resources import unzip_content, zip_content
from pureml.utils.version_utils import parse_version_label

path_schema = PathSchema()
backend_schema = BackendSchema()
# path_schema = PathSchema().get_instance()
predict_schema = PredictSchema()
# backend_schema = BackendSchema().get_instance()
post_key_resources = LogSchema().key.resources.value
config_keys = ConfigKeys
storage = StorageSchema().get_instance()


def post_resource(path, model_name: str, model_version: str):
    org_id = get_org_id()

    url = "org/{}/model/{}/version/{}/logfile".format(
        org_id, model_name, model_version
    )
    url = urljoin(backend_schema.BASE_URL, url)

    headers = get_auth_headers(content_type=None, accept=AcceptHeader.APP_JSON)

    try:
        zip_content(src_path=path, dst_path=predict_schema.PATH_RESOURCES)
    except Exception as e:
        print(e)

    if not os.path.exists(predict_schema.PATH_RESOURCES):
        print(f"[orange]Unable to zip the resource!")
        return

    file_paths = {post_key_resources: path}
    provider, file_path = upload_and_get_provider_and_path(
        predict_schema.PATH_RESOURCES, opt_base_dir="resources"
    )
    files = [file_path]

    data = {
        "data": file_paths,
        "key": post_key_resources,
        "storage": provider,
        "file_path_json_array": json.dumps(files),
    }

    # data = json.dumps(data)

    response = requests.post(
        url, data=data, files={"foo": "bar"}, headers=headers
    )

    if response.ok:
        print(f"[green]resource has been registered!")
        reset_config(key=config_keys.resource.value)

    else:
        print(f"[orange]resource has not been registered!")

    return response


def add(
    label: str = None,
    path: str = None,
) -> str:

    model_name, model_version = parse_version_label(label)

    add_resource_to_config(
        values=path,
        model_name=model_name,
        model_version=model_version,
    )

    if (
        model_name is not None
        and model_version is not None
        and model_version is not None
    ):
        response = post_resource(
            path=path,
            model_name=model_name,
            model_version=model_version,
        )

        print(response.text)

    # return response.text


def details(label: str):
    model_name, model_version = parse_version_label(label)
    org_id = get_org_id()

    url = "org/{}/model/{}/version/{}/log".format(
        org_id, model_name, model_version
    )
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
        print(f"[orange]Unable to fetch resource!")
        return


def fetch(label: str):
    model_name, model_version = parse_version_label(label)

    get_org_id()

    def fetch_resource(file_details):

        file_name, url = file_details

        save_path = os.path.join(path_schema.PATH_PREDICT_DIR, file_name)
        # print("save path", save_path)

        headers = get_auth_headers(
            content_type=ContentTypeHeader.APP_FORM_URL_ENCODED,
            accept=AcceptHeader.APP_JSON,
        )

        # print("resorce url", url)

        # response = requests.get(url, headers=headers)
        response = requests.get(url)

        # print(response.status_code)

        if response.ok:
            print("[green] resource {} has been fetched".format(file_name))

            save_dir = os.path.dirname(save_path)

            os.makedirs(save_dir, exist_ok=True)

            resource_bytes = response.content

            open(save_path, "wb").write(resource_bytes)
            unzip_content(save_path, path_schema.PATH_PREDICT_DIR)

            print(
                "[green] resource {} has been stored at {}".format(
                    file_name, save_path
                )
            )

            return response.text
        else:
            print("[orange] Unable to fetch the resource")

            return response.text

    resource_details = details(label=label)
    # print("resource_details", resource_details)

    if resource_details is None:
        return

    # pred_urls = give_resource_urls(details=resource_details)
    pred_urls = give_resource_url(
        details=resource_details, key=post_key_resources
    )

    if len(pred_urls) == 1:

        res_text = fetch_resource(pred_urls[0])

    else:
        res_text = Parallel(n_jobs=-1)(
            delayed(fetch_resource)(pred_url) for pred_url in pred_urls
        )


def give_resource_url(details, key: str):
    resource_paths = []
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
                source_path = ".".join([source_path, "zip"])
                # source_path = os.path.join(path_schema.PATH_PREDICT_DIR, source_path)
                resource_paths.append([source_path, file_url])

                # print(source_path, file_url)

                return resource_paths
    print("[orange] Unable to find the resource")

    return resource_paths
