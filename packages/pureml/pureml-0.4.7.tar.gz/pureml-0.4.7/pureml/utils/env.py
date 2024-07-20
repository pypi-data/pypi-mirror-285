import os

from dotenv import load_dotenv
from rich import print

from pureml.schema.env import Env


def generate_env_dict(env_path):
    load_dotenv(dotenv_path=env_path)

    org_id = os.getenv(Env.ORG_ID.value)
    access_token = os.getenv(Env.ACCESS_TOKEN.value)
    api_token = os.getenv(Env.API_TOKEN.value)

    env_dict = {}

    if org_id is None:
        print("[orange]", Env.ORG_ID.value, "is not set in .env")
    else:
        env_dict[Env.ORG_ID.value] = org_id

    if access_token is None:
        print("[orange]", Env.ACCESS_TOKEN.value, "is not set in .env")
    else:
        env_dict[Env.ACCESS_TOKEN.value] = access_token

    if api_token is None:
        print("[orange]", Env.API_TOKEN.value, "is not set in .env")
    else:
        env_dict[Env.API_TOKEN.value] = api_token

    return env_dict


def validate_env_docker(env_dict):
    env_dict_set = set(list(env_dict.keys()))
    env_dict_docker = set([Env.ORG_ID.value, Env.API_TOKEN.value])

    if env_dict_docker.issubset(env_dict_set):
        return True

    return False
