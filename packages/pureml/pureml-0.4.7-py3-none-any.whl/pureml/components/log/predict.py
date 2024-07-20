import json
import os

import requests
from joblib import Parallel, delayed
from rich import print

from pureml.cli.helpers import get_auth_headers
from pureml.schema.backend import BackendSchema
from pureml.schema.config import ConfigKeys
from pureml.schema.log import LogSchema
from pureml.schema.paths import PathSchema
from pureml.schema.request import AcceptHeader, ContentTypeHeader
from pureml.schema.storage import StorageSchema
from pureml.storage import upload_and_get_provider_and_path
from pureml.utils.config import reset_config
from pureml.utils.pipeline import add_pred_to_config
from pureml.utils.routes import model_metadata
from pureml.utils.version_utils import parse_version_label

from . import pip_requirement, resources

path_schema = PathSchema()
backend_schema = BackendSchema()
post_key_predict = LogSchema().key.predict.value
post_key_requirements = LogSchema().key.requirements.value
post_key_resources = LogSchema().key.resources.value
config_keys = ConfigKeys
storage = StorageSchema().get_instance()


def post_predict(file_paths, model_name: str, model_version: str):

    url = model_metadata(model_name)
    headers = get_auth_headers(content_type=None, accept=AcceptHeader.APP_JSON)

    files = []
    for file_name, file_path in file_paths.items():
        # print("filename", file_name)

        if os.path.isfile(file_path):
            # files.append(("file", (file_name, open(file_path, "rb"))))
            provider, file_path = upload_and_get_provider_and_path(
                file_path, opt_base_dir="logfiles"
            )
            files.append(file_path)

        else:
            print(
                "[orange] Predict",
                file_name,
                "does not exist at the given path",
            )

    params = {"version": model_version}

    data = {
        "predict": {
            "data": file_paths,
            "key": post_key_predict,
            "storage": provider,
            "file_path_json_array": json.dumps(files),
        },
        "requirements": {},
        "resources": {},
    }

    response = requests.post(url, json=data, params=params, headers=headers)
    #print(f"response: {response}")
    if response.ok:
        print("[green]Predict Function has been registered!")
        reset_config(key=config_keys.pred_function.value)

    else:
        print("[orange]Predict Function has not been registered!")

    return response


def add(label: str = None, paths: dict = None) -> str:

    model_name, model_version = parse_version_label(label)

    pred_path = paths[post_key_predict]

    if post_key_requirements in paths:
        pip_requirement.add(label, path=paths[post_key_requirements])

    if post_key_resources in paths:
        resources.add(label, path=paths[post_key_resources])

    file_paths = {post_key_predict: pred_path}

    add_pred_to_config(
        values=pred_path,
        model_name=model_name,
        model_version=model_version,
    )

    if (
        model_name is not None
        and model_version is not None
        and model_version is not None
    ):
        response = post_predict(
            file_paths=file_paths,
            model_name=model_name,
            model_version=model_version,
        )

        # print(response.text)

    # return response.text


def details(label: str):
    model_name, model_version = parse_version_label(label)

    url = model_metadata(model_name)
    params = {"version": model_version}

    headers = get_auth_headers(content_type=None, accept=AcceptHeader.APP_JSON)

    response = requests.get(url, headers=headers, params=params)

    if response.ok:
        # T-1161 standardize api response to contains Models as a list
        response_text = response.json()
        details = response_text["data"]

        # print(model_details)

        return details

    else:
        print(f"[orange]Unable to fetch Predict!")
        return


def fetch(label: str):
    model_name, model_version = parse_version_label(label)

    def fetch_predict(file_details):

        file_name, url = file_details
        #print(f"file_name: {file_name}")
        #print(f"url: {url}")

        save_path = os.path.join(path_schema.PATH_PREDICT_DIR, file_name)
        # print("save path", save_path)

        if "http" in url:
            headers = get_auth_headers(
                content_type=ContentTypeHeader.APP_FORM_URL_ENCODED,
                accept=AcceptHeader.APP_JSON,
            )

            response = requests.get(url)

            #print(response.status_code)

            if response.ok:
                print(f"[green] predict file {file_name} has been fetched")

                save_dir = os.path.dirname(save_path)

                os.makedirs(save_dir, exist_ok=True)

                predict_bytes = response.content

                with open(save_path, "wb") as f:
                    f.write(predict_bytes)

                # open(save_path, "wb").write(predict_bytes)

                # print(
                #     "[green] predict file {} has been stored at {}".format(
                #         file_name, save_path
                #     )
                # )
                # print(f"save Path: {save_path}")
                return save_path
                # return response.text
            else:
                print("[orange] Unable to fetch the predict function")

                return response.text
        else:
            print("[green] predict file {} has been fetched".format(file_name))

            return url

    predict_details = details(label=label)
    #print(f"Predict Details : {predict_details}")

    if predict_details is None:
        return

    # pred_urls = give_predict_urls(details=predict_details)
    pred_urls = give_predict_url(details=predict_details, key=post_key_predict)
    #print(f"pred_urls: {pred_urls}")
    if len(pred_urls) == 1:

        res_text = fetch_predict(pred_urls[0])
        return res_text

    else:
        res_text = Parallel(n_jobs=-1)(
            delayed(fetch_predict)(pred_url) for pred_url in pred_urls
        )
        return res_text


def give_predict_url(details, key: str):
    predict_paths = []
    # file_url = None
    source_path = None
    file_url = None
    # print(details)
    # print(f"Key: {key}")
    if details is not None:
        for det in details:
            if "metadata" in det:
                if "predict" in det["metadata"]:
                    if "storage" in det["metadata"]["predict"]:
                        if det["metadata"]["predict"]["storage"] == "file":
                            source_path = det["metadata"]["predict"]["key"]
                            file_url = det["metadata"]["predict"]["data"]
                            source_path = ".".join([source_path, "py"])
                            predict_paths.append([source_path, file_url])
                            return predict_paths
                        else:
                            if (
                                "file_path_json_array"
                                in det["metadata"]["predict"]
                            ):
                                source_path = det["metadata"]["predict"]["key"]
                                predict_url = det["metadata"]["predict"][
                                    "file_path_json_array"
                                ]
                                url_list = json.loads(predict_url)
                                predict_paths.extend(
                                    [source_path, url] for url in url_list
                                )
                                return predict_paths

    print("[orange] Unable to find the predict file")

    return predict_paths
