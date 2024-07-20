from rich import print

from pureml.components import model


def get_model_helper(label_model):
    model_load = model.fetch(label=label_model)
    if model_load is None:
        print("[orange] Unable to fetch the model")
        return None
    else:
        print("[green] Succesfully fetched the model")
        return model_load
