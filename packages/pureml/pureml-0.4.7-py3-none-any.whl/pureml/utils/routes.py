from urllib.parse import urljoin

from pureml.schema.backend import BackendSchema
from pureml.schema.dataset import DatasetSchema
from pureml.schema.model import ModelSchema


def dataset_base_url():
    dataset_schema = DatasetSchema()
    return dataset_schema._backend.BASE_URL


def check_dataset_hash_url(name):  # URL to check Dataset Hash
    url = f"datasets/{name}/hash-status"
    return urljoin(dataset_base_url(), url)


def dataset_list_urls():
    url = "datasets"
    return urljoin(dataset_base_url(), url)


def dataset_init_urls():
    url = "datasets"
    return urljoin(dataset_base_url(), url)


def dataset_register_url(name):
    url = f"datasets/{name}/register"
    return urljoin(dataset_base_url(), url)


def dataset_details_url(name):
    url = f"datasets?dataset_name={name}"
    return urljoin(dataset_base_url(), url)


def dataset_version_details_url(name):
    url = f"datasets/{name}/versions"
    return urljoin(dataset_base_url(), url)


def model_base_url():
    model_schema = ModelSchema()
    return model_schema._backend.BASE_URL


def check_model_hash_url(name):
    url = f"models/{name}/hash-status"
    return urljoin(model_base_url(), url)


def model_list_urls():
    url = "models"
    return urljoin(model_base_url(), url)


def model_init_url():
    url = "models"
    return urljoin(model_base_url(), url)


def model_register_url(name):
    url = f"models/{name}/register"
    return urljoin(model_base_url(), url)


def model_details_url(name):
    url = f"models?model_name={name}"
    return urljoin(model_base_url(), url)


def model_version_details_url(name):
    url = f"models/{name}/versions"
    return urljoin(model_base_url(), url)


def model_metadata(name):
    url = f"models/{name}/metadata"
    return urljoin(model_base_url(), url)


def backend_base_url():
    backend_schema = BackendSchema()
    return backend_schema.BASE_URL


def login_url():
    url = "orgs/users"
    return urljoin(backend_base_url(), url)


def secrets_url(repository_argument):
    url = f"secrets/{str(repository_argument)}"
    return urljoin(backend_base_url(), url)
