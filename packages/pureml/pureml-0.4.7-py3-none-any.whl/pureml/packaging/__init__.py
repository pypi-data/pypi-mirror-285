from pathlib import Path

from .packaging import Model


def save_model(model, model_name, model_path, model_framework=None) -> None:
    """The function takes in a model and a model name, and saves the model to the default `models` directory.

    Parameters
    ----------
    model
        The model you want to save.
    model_name
        The name of the model.

    """
    # print(model_dir)
    # os.makedirs(model_dir, exist_ok=True)
    Model(
        model=model,
        model_name=model_name,
        model_path=model_path,
        model_framework=model_framework,
    ).save_model()


def load_model(model_path: Path):
    """Loads a model from a given path

    Parameters
    ----------
    model_path : Path
        The path to the model you want to load.

    Returns
    -------
        The model is being returned.

    """
    model = Model(model_path=model_path).load_model()

    return model
