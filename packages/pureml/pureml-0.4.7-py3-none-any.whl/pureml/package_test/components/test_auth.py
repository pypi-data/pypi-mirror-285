from pureml.components.auth import login


def test_login():
    org_id = ""  # Your Org ID
    api_token = ""  # Your API Token
    login(org_id=org_id, api_token=api_token)


test_login()
