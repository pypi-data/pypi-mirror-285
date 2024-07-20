from pureml.schema.backend import BackendSchema
from pureml.schema.log import LogSchema
from pureml.schema.paths import PathSchema

from . import figure as pure_figure
from . import metrics as pure_metrics
from . import params as pure_params
from . import pip_requirement as pure_pip_req
from . import predict as pure_predict

# path_schema = PathSchema().get_instance()
# backend_schema = BackendSchema().get_instance()
path_schema = PathSchema()
backend_schema = BackendSchema()

post_keys = LogSchema().key


def log(label: str = None, metrics=None, params=None, step=1, **kwargs):

    if metrics is not None:
        func_params = {}

        if label is not None:
            func_params["label"] = label

        func_params["metrics"] = metrics.copy()

        func_params["step"] = step

        pure_metrics.add(**func_params)

    if params is not None:
        func_params = {}

        if label is not None:
            func_params["label"] = label

        func_params["params"] = params.copy()

        func_params["step"] = step

        pure_params.add(**func_params)

    if post_keys.figure.value in kwargs.keys():
        figure = kwargs[post_keys.figure.value]
        func_params = {}

        if label is not None:
            func_params["label"] = label

        func_params["figure"] = figure.copy()
        # func_params['step']  = step

        pure_figure.add(**func_params)

    if post_keys.predict.value in kwargs.keys():
        predict = kwargs[post_keys.predict.value]
        func_params = {}

        if label is not None:
            func_params["label"] = label

        func_params["path"] = predict

        pure_predict.add(**func_params)

    if post_keys.requirements.value in kwargs.keys():
        requirement = kwargs[post_keys.requirements.value]
        func_params = {}

        if label is not None:
            func_params["label"] = label

        func_params["path"] = requirement

        pure_pip_req.add(**func_params)
