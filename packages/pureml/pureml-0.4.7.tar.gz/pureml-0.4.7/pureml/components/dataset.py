import json
import os

import joblib
import requests
from rich import print

from pureml.schema.dataset import DatasetSchema
from pureml.cli.helpers import get_auth_headers
from pureml.schema.config import ConfigKeys
from pureml.schema.request import AcceptHeader, ContentTypeHeader
from pureml.schema.storage import StorageSchema
from pureml.storage import upload_and_get_provider_and_path
from pureml.utils.hash import generate_hash_for_file
from pureml.utils.logger import get_logger
from pureml.utils.readme import load_readme
from pureml.utils.routes import (
    check_dataset_hash_url,
    dataset_details_url,
    dataset_init_urls,
    dataset_list_urls,
    dataset_register_url,
    dataset_version_details_url,
)
from pureml.utils.version_utils import parse_version_label

from . import get_org_id

config_keys = ConfigKeys
storage = StorageSchema().get_instance()
logger = get_logger("sdk.components.dataset")


def check_dataset_hash(hash: str, label: str):
    """
    The function `check_dataset_hash` checks if a dataset hash exists by making a POST request to a
    specific URL with the hash data.

    :param hash: The `hash` parameter in the `check_dataset_hash` function is a string that represents
    the hash value of a dataset. This hash value is used to uniquely identify the dataset and is
    typically generated using a hashing algorithm like MD5 or SHA-256. The function uses this hash value
    to check if
    :type hash: str
    :param label: The `label` parameter in the `check_dataset_hash` function is used to specify a label
    associated with the dataset. This label is then used to extract the name of the dataset by calling
    the `parse_version_label` function
    :type label: str
    :return: The function `check_dataset_hash` returns a boolean value indicating whether the dataset
    hash exists or not.
    """
    logger.info("Checking dataset hash", hash=hash, label=label)

    name, _ = parse_version_label(label)

    get_org_id()

    url = check_dataset_hash_url(name)

    headers = get_auth_headers(
        content_type=ContentTypeHeader.APP_FORM_URL_ENCODED
    )

    data = {"hash": hash}

    data = json.dumps(data)

    response = requests.post(url, data=data, headers=headers)

    hash_exists = False

    if response.ok:
        hash_exists = response.json()["data"][0]

    logger.info(f"Hash exists {hash_exists}")
    return hash_exists


def list():
    """This function will return a list of all the datasets

    Returns
    -------
        A list of all the datasets

    """
    logger.info("Fetching list of datasets")

    get_org_id()

    url = dataset_list_urls()

    headers = get_auth_headers(
        content_type=ContentTypeHeader.APP_FORM_URL_ENCODED
    )

    response = requests.get(url, headers=headers)

    if response.ok:
        # print(f"[green]Obtained list of models[/green]")

        response_text = response.json()
        dataset_list = response_text["data"]

        return dataset_list
    else:
        logger.error("Unable to obtain the list of dataset", response=response)
        print("[orange]Unable to obtain the list of dataset![/orange]")

    return


def init(label: str, readme: str = None):
    """
    This Python function initializes a dataset with a given label and optional readme content.

    :param label: The `label` parameter is a string that represents the version label of a dataset. It
    is used to extract the name of the dataset from the label
    :type label: str
    :param readme: The `readme` parameter in the `init` function is a string that represents the path to
    the readme file associated with the dataset. If no `readme` path is provided when calling the
    function, it defaults to `None` and the function will attempt to load the readme content from the
    :type readme: str
    :return: The `init` function returns a boolean value - `True` if the dataset creation was
    successful, and `False` if it was not successful.
    """

    name, _ = parse_version_label(label)

    headers = get_auth_headers(content_type=ContentTypeHeader.ALL)
    get_org_id()
    dataset_schema = DatasetSchema()

    if readme is None:
        readme = dataset_schema.PATH_DATASET_README

    file_content, file_type = load_readme(path=readme)

    url = dataset_init_urls()
    data = {
        "name": name,
        "readme": {"file_type": file_type, "content": file_content},
    }

    data = json.dumps(data)
    # files = {"file": (readme, open(readme, "rb"), file_type)}
    # response = requests.post(url, data=data, headers=headers, files=files)
    #
    response = requests.post(url, data=data, headers=headers)

    if response.ok:
        print("[green]Dataset has been created![/green]")

        return True

    else:
        print(response.text)
        print("[orange]Dataset has not been created![/orange]")

        return False


def save_dataset(dataset, name: str):
    """
    The function `save_dataset` saves a dataset object as a pickle file with a specified name.

    :param dataset: The `dataset` parameter in the `save_dataset` function is the dataset that you want
    to save. It could be any kind of data structure or object that you want to persist to a file, such
    as a DataFrame, a dictionary, a list, etc. The function saves this dataset to a
    :param name: The `name` parameter in the `save_dataset` function is a string that represents the
    name under which the dataset will be saved. It is used to construct the file name for the saved
    dataset file
    :type name: str
    :return: The function `save_dataset` returns the path where the dataset has been saved in pickle
    format (.pkl).
    """
    logger.info("Saving dataset", name=name)
    dataset_schema = DatasetSchema()
    # file_name = '.'.join([name, 'parquet'])
    file_name = ".".join([name, "pkl"])
    save_path = os.path.join(dataset_schema._paths.PATH_DATASET_DIR, file_name)

    os.makedirs(dataset_schema._paths.PATH_DATASET_DIR, exist_ok=True)

    # dataset.to_parquet(save_path)
    joblib.dump(dataset, save_path)

    logger.info("Dataset saved", save_path=save_path)
    return save_path


def register(dataset, label: str, lineage, is_empty: bool = False) -> str:
    """The function takes in a dataset, a name and a version and saves the dataset locally, then uploads the
    dataset to the PureML server

    Parameters
    ----------
    dataset
        The dataset you want to register
    name : str
        The name of the dataset.
    version: str, optional
        The version of the dataset.

    """
    logger.info("Registering dataset", label=label, is_empty=is_empty)
    name, _ = parse_version_label(label)

    get_org_id()
    DatasetSchema()

    dataset_path = save_dataset(dataset, name)

    # windows paths support
    if "\\" in dataset_path:
        dataset_path = dataset_path.replace("\\", "/")

    dataset_path.split("/")[-1]

    dataset_hash = generate_hash_for_file(
        file_path=dataset_path, name=name, is_empty=is_empty
    )

    if is_empty:
        dataset_path = save_dataset(dataset=None, name=name)
        dataset_path.split("/")[-1]

    dataset_exists = dataset_status(label)
    # print('Dataset status', dataset_exists)

    if not dataset_exists:
        dataset_created = init(label=label)
        # print('dataset_created', dataset_created)
        if not dataset_created:
            print("[orange] Unable to register the dataset[/orange]")
            return False, dataset_hash, None
    else:
        logger.info("Dataset already exists", label=label)
        print("[green] Connected to Dataset[/green]")

    dataset_exists_remote = check_dataset_hash(hash=dataset_hash, label=label)

    # print("Hash : ", dataset_hash)

    if dataset_exists_remote:

        print(
            "[green]Dataset already exists. Not registering a new version![/green]"
        )
        return True, dataset_hash, "latest"
    else:

        url = dataset_register_url(name)

        headers = get_auth_headers(
            content_type=None, accept=AcceptHeader.APP_JSON
        )

        # files = {"file": (name_with_ext, open(dataset_path, "rb"))}
        provider, file_path = upload_and_get_provider_and_path(
            dataset_path, opt_base_dir="dataset-registry"
        )

        lineage = json.dumps(lineage)

        data = {
            "name": name,
            "hash": dataset_hash,
            "lineage": lineage,
            "is_empty": is_empty,
            "storage": provider,
            "file_path": file_path,
        }

        # data = json.dumps(data)

        response = requests.post(
            url, files={"foo": "bar"}, data=data, headers=headers
        )

        if response.ok:

            dataset_version = None

            # print(response.json())
            try:
                dataset_version = response.json()["data"][0]["version"]
                print("Dataset version: ", dataset_version)
                dataset_label = ":".join([name, dataset_version])
                print("Dataset label: ", dataset_label)

                if is_empty:
                    print("[green]Lineage has been registered![/green]")
                else:
                    print(
                        "[green]Dataset and lineage have been registered![/green]"
                    )

                # reset_config(key=config_keys.dataset.value)

            except Exception as e:
                logger.error(
                    "Incorrect json response. Dataset has not been registered",
                    error=e,
                )
                print(
                    "[orange]Incorrect json response. Dataset has not been registered[/orange]"
                )
                print(e)

            return True, dataset_hash, dataset_version
        else:
            logger.error("Unable to register dataset", response=response)
            print("[orange]Dataset has not been registered![/orange]")
            print(response.text)

            return True, dataset_hash, None


def dataset_status(label: str):
    """
    The function `dataset_status` checks if dataset details are available based on the provided label.

    :param label: The `label` parameter is a string that represents the version label of a dataset
    :type label: str
    :return: The function `dataset_status` is returning a boolean value - `True` if `dataset_details` is
    not empty, and `False` if `dataset_details` is empty.
    """

    name, _ = parse_version_label(label)

    dataset_details = details(label=label)

    if dataset_details:
        return True
    else:
        return False


def details(
    label: str,
):
    """It fetches the details of a dataset.

    Parameters
    ----------
    name : str
        The name of the dataset
    version: str
        The version of the dataset
    Returns
    -------
        The details of the dataset.

    """

    name, _ = parse_version_label(label)

    get_org_id()
    DatasetSchema()

    url = dataset_details_url(name)

    headers = get_auth_headers(
        content_type=ContentTypeHeader.APP_FORM_URL_ENCODED
    )
    response = requests.get(url, headers=headers)
    if response.ok:
        # print(f"[green]Dataset details have been fetched[/green]")
        response_text = response.json()
        dataset_details = response_text["data"][0]

        return dataset_details

    else:
        print("[yellow]Dataset details have not been found[/yellow]")
        return


def version_details(label: str):
    """It fetches the details of a dataset.

    Parameters
    ----------
    name : str
        The name of the dataset
    version: str
        The version of the dataset
    Returns
    -------
        The details of the dataset.

    """

    name, version = parse_version_label(label)
    get_org_id()
    DatasetSchema()

    url = dataset_version_details_url(name)

    headers = get_auth_headers(
        content_type=ContentTypeHeader.APP_FORM_URL_ENCODED
    )

    response = requests.get(url, headers=headers)
    if response.ok:
        # print(f"[green]Dataset Version details have been fetched[/green]")
        response_text = response.json()
        dataset_details = response_text["data"][0]
        # print(dataset_details)

        return dataset_details

    else:
        print("[yellow]Dataset version details have not been found[/yellow]")
        return


def fetch(label: str):
    """This function fetches a dataset from the server and returns it as a dataframe object

    Parameters
    ----------
    name : str, optional
        The name of the dataset you want to fetch.
    version: str
        The version of the dataset

    Returns
    -------
        The dataset dataframe is being returned.

    """

    name, version = parse_version_label(label)

    get_org_id()
    DatasetSchema()

    dataset_details = version_details(label=label)

    if dataset_details is None:
        print("[orange]Unable to fetch Dataset version[/orange]")
        return

    is_empty = dataset_details["is_empty"]

    if is_empty:
        print("[orange]Dataset file is not registered to the version[/orange]")
        return

    # storage_path = dataset_details["path"]["source_path"]
    # storage_source_type = dataset_details["path"]["source_type"]["public_url"]

    # dataset_url = urljoin(storage_source_type, storage_path)

    dataset_url = dataset_details["path"]
    source_type = dataset_details["source_type"]
    dataset_url = dataset_url.strip()

    if source_type != "file":
        response = requests.get(dataset_url)
        if response.ok:
            dataset_bytes = response.content
            # open('temp_dataset.parquet', 'wb').write(dataset_bytes)
            # dataset = pd.read_parquet('temp_dataset.parquet')

            with open("temp_dataset.pkl", "wb") as file:
                file.write(dataset_bytes)
            dataset = joblib.load("temp_dataset.pkl")

            # print(f"[green]Dataset has been fetched[/green]")
            return dataset
        else:
            print("[orange]Unable to fetch Dataset[/orange]")
            return
    else:
        if os.path.exists(dataset_url):
            dataset = joblib.load(dataset_url)
            return dataset
        else:
            print("[orange]Unable to fetch Dataset[/orange]")
            return


# def delete(label: str) -> str:
#     """This function deletes a dataset from the project

#     Parameters
#     ----------
#     name : str
#         The name of the dataset you want to delete
#     version : str
#         The version of the dataset to delete.

#     """

#     name, version = parse_version_label(label)

#     user_token = get_token()
#     org_id = get_org_id()
#     dataset_schema = DatasetSchema()

#     url = "datasets/{}/delete".format(org_id, name)
#     url = urljoin(dataset_schema.backend.BASE_URL, url)

#     headers = {
#         "Content-Type": ContentTypeHeader.APP_FORM_URL_ENCODED.value,
#         "Authorization": "Bearer {}".format(user_token),
#     }

#     data = {"version": version}

#     data = json.dumps(data)

#     response = requests.delete(url, headers=headers, data=data)

#     if response.ok:
#         print(f"[green]Dataset has been deleted[/green]")

#     else:
#         print(f"[orange]Unable to delete Dataset[/orange]")

#     return response.text
