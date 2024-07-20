from importlib import import_module

from pydantic import BaseModel
from rich import print

from pureml.predictor.predictor import BasePredictor


class get_predictor_helper(BaseModel):
    predictor: BasePredictor = None
    predictor_path: str = "predict.py"

    def load_predictor(self):
        module_path = self.predictor_path.replace(".py", "")
        module_import = import_module(module_path)

        predictor_class = getattr(module_import, "Predictor")

        self.predictor = predictor_class()
        print(f"self.predictor: {self.predictor}")
        print("[green] Succesfully fetched the predictor")

        return self.predictor if self.predictor != None else None
