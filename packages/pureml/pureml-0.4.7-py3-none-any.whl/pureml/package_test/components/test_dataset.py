from random import randint

import numpy as np
import pandas as pd

from pureml.components.dataset import details, init, list, register, version_details

num_samples = 1000
num_features = 5
features = pd.DataFrame(
    np.random.randn(num_samples, num_features),
    columns=[f"Feature_{i}" for i in range(num_features)],
)
labels = np.random.randint(0, 2, num_samples)
train_size = int(num_samples * 0.8)
x_train = features[:train_size]
x_test = features[train_size:]
y_train = labels[:train_size]
y_test = labels[train_size:]
sensitive_features = np.random.choice(
    ["Sensitive_A", "Sensitive_B", "Sensitive_C"], num_samples
)

label = f"dataset_test_{randint(1,100)}"


class DatasetTest:

    def test_list():
        result = list()
        print(f"Dataset List:\n {result}")

    def test_init():
        result = init(label=label)
        assert result == True

    def test_details():
        result = details(label)
        print(f"Details:\n {result}")

    def test_register():
        dataset = {
            "x_train": x_train,
            "x_test": x_test,
            "y_train": y_train,
            "y_test": y_test,
            "sensitive_features": sensitive_features,
        }
        lineage = {"test": "test"}
        result, dataset_hash, dataset_version = register(
            dataset=dataset, label=label, lineage=lineage
        )
        assert result == True

    def test_version_details():
        result = version_details(label=label)
        print(f"Version Details: \n{result}")

    def fetch():
        pass


dt = DatasetTest
dt.test_list()
dt.test_init()
dt.test_details()
dt.test_register()
dt.test_version_details()
