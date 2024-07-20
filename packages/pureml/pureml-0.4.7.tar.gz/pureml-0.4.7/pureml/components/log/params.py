import json
from urllib.parse import urljoin

import requests
from rich import print

from pureml.cli.helpers import get_auth_headers
from pureml.components import convert_values_to_string, get_org_id
from pureml.schema.backend import BackendSchema
from pureml.schema.config import ConfigKeys
from pureml.schema.log import LogSchema
from pureml.schema.request import ContentTypeHeader
from pureml.utils.config import reset_config
from pureml.utils.pipeline import add_params_to_config
from pureml.utils.version_utils import parse_version_label

backend_schema = BackendSchema()
# backend_schema = BackendSchema().get_instance()
post_key_params = LogSchema().key.params.value
config_keys = ConfigKeys


def post_params(params, model_name: str, model_version: str):
    org_id = get_org_id()

    url = f"org/{org_id}/model/{model_name}/version/{model_version}/log"
    url = urljoin(backend_schema.BASE_URL, url)

    headers = get_auth_headers(
        content_type=ContentTypeHeader.APP_FORM_URL_ENCODED
    )

    params = json.dumps(params)

    data = {"data": params, "key": post_key_params}

    data = json.dumps(data)

    response = requests.post(url, data=data, headers=headers)

    if response.ok:
        print("[green]Params have been registered!")
        reset_config(key=config_keys.params.value)

    else:
        print("[orange]Params have not been registered!")

    return response


def add(
    params,
    label: str = None,
    step=1,
) -> str:
    """`add()` takes a dictionary of parameters and a model name as input and returns a string

    Parameters
    ----------
    params : dict
        a dictionary of parameters
    model_name : str
        The name of the model you want to add parameters to.
    model_version: str
        The version of the model

    Returns
    -------
        The response.text is being returned.

    """

    model_name, model_version = parse_version_label(label)

    params = convert_values_to_string(logged_dict=params)
    # params = merge_step_with_value(values_dict=params, step=step)

    add_params_to_config(
        values=params,
        model_name=model_name,
        model_version=model_version,
    )

    if model_name is not None and model_version is not None:
        response = post_params(
            params=params,
            model_name=model_name,
            model_version=model_version,
        )

    #     return response.text

    # return


def details(label: str):
    """
    Retrieve details from the log for a specific model version identified by the label.

    Args:
        label (str): The label identifying the model version.

    Returns:
        The log details for the specified model version.
    """
    model_name, model_version = parse_version_label(label)
    org_id = get_org_id()

    url = f"org/{org_id}/model/{model_name}/version/{model_version}/log"
    url = urljoin(backend_schema.BASE_URL, url)

    headers = get_auth_headers(
        content_type=ContentTypeHeader.APP_FORM_URL_ENCODED
    )

    response = requests.get(url, headers=headers)

    if response.ok:
        # T-1161 standardize api response to contains Models as a list
        response_text = response.json()
        details = response_text["data"]

        # print(model_details)

        return details

    else:
        print("[orange]Unable to fetch logs!")
        return


def get_value_from_log(details, key_log=post_key_params, key=None):
    """
    Retrieve a value from the log details based on the specified key.

    Args:
        details (list): A list of dictionaries containing log details.
        key_log (str): The key to search for in the log details.
        key (str, optional): The specific key within the log details to retrieve the value for.

    Returns:
        The value corresponding to the specified key in the log details.
    """
    value = None
    if details is not None:
        # print(details)

        for det in details:
            # print(det)
            # print(det["key"])
            if det["key"] == key_log:
                value = det["data"]
                # print(value)
                value = json.loads(value)

                if key is not None:
                    if key in value.keys():
                        value = value[key]
                    else:
                        print(
                            f"[orange]{key_log} : {key} is not available for the model!"
                        )

                return value

    print(f"[orange] Unable to find the {key}")

    return value


def fetch(label: str, param: str = None) -> str:
    """

    This function fetches the parameters of a model

    Parameters
    ----------
    model_name : str
        The name of the model you want to fetch the parameters for.
    model_version: str
        The version of the model
    param : str
        The name of the parameter to fetch. If not specified, all parameters are returned.

    Returns
    -------
        The params that are fetched

    """
    metric_details = details(label=label)

    if metric_details:

        metrics = get_value_from_log(
            details=metric_details, key_log=post_key_params, key=param
        )

        return metrics
    return


# def delete(param: str, label: str) -> str:
#     """This function deletes a parameter from a model

#     Parameters
#     ----------
#     model_name : str
#         The name of the model you want to delete the parameter from.
#     param : str
#         The name of the parameter to delete.
#     model_version: str
#         The version of the model

#     """
#     model_name, model_version = parse_version_label(label)

#     user_token = get_token()
#     org_id = get_org_id()
#     log_schema = LogSchema()

#     url = "org/{}/model/{}/version/{}/log/delete".format(
#         org_id, model_name, model_version
#     )
#     url = urljoin(log_schema.backend.BASE_URL, url)

#     headers = {
#         "Content-Type": "application/x-www-form-urlencoded",
#         "Authorization": "Bearer {}".format(user_token),
#     }

#     response = requests.delete(url, headers=headers)

#     if response.ok:
#         print(f"[green]Param has been deleted")

#     else:
#         print(f"[orange]Unable to delete Param")

#     return response.text
