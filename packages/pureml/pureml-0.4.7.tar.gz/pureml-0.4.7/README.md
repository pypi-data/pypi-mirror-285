# Manual Setup
SDK requires poetry. You can find install instructuction [here](https://python-poetry.org/)

Clone the repo to local folder
```
git clone https://github.com/PuremlHQ/PureML
```
Navigate to packages > sdk
```
poetry install
poetry build
```

# Folder Structure

```
.
├── License
├── README.md
├── change_log.md
├── pureml
│   ├── __init__.py
│   ├── cli
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── helpers.py
│   │   ├── main.py
│   │   ├── orgs.py
│   │   ├── public.pem
│   │   ├── puremlconfig.py
│   │   └── secrets.py
│   ├── components
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── dataset.py
│   │   ├── log
│   │   │   ├── __init__.py
│   │   │   ├── arrays.py
│   │   │   ├── artifacts.py
│   │   │   ├── audio.py
│   │   │   ├── figure.py
│   │   │   ├── image.py
│   │   │   ├── log.py
│   │   │   ├── metrics.py
│   │   │   ├── params.py
│   │   │   ├── pip_requirement.py
│   │   │   ├── predict.py
│   │   │   ├── resources.py
│   │   │   ├── tabular.py
│   │   │   └── video.py
│   │   └── model.py
│   ├── config
│   │   ├── __init__.py
│   │   └── parser.py
│   ├── decorators
│   │   ├── __init__.py
│   │   ├── dataset.py
│   │   ├── load_data.py
│   │   ├── model.py
│   │   ├── pip_requirements.py
│   │   ├── predict.py
│   │   └── transformer.py
│   ├── evaluate
│   │   ├── __init__.py
│   │   ├── classification.py
│   │   ├── eval.py
│   │   ├── grade.py
│   │   ├── metrics
│   │   │   ├── __init__.py
│   │   │   ├── accuracy.py
│   │   │   ├── base.py
│   │   │   ├── confusion_matrix.py
│   │   │   ├── f1.py
│   │   │   ├── mae.py
│   │   │   ├── mse.py
│   │   │   ├── precision.py
│   │   │   ├── recall.py
│   │   │   └── roc_auc.py
│   │   └── regression.py
│   ├── lineage
│   │   ├── __init__.py
│   │   └── data
│   │       ├── __init__.py
│   │       └── create_lineage.py
│   ├── package
│   │   ├── __init__.py
│   │   ├── docker.py
│   │   └── fastapi.py
│   ├── packaging
│   │   ├── __init__.py
│   │   ├── errors.py
│   │   ├── model_framework.py
│   │   ├── model_packaging
│   │   │   ├── __init__.py
│   │   │   ├── catboost.py
│   │   │   ├── custom.py
│   │   │   ├── keras.py
│   │   │   ├── lightgbm.py
│   │   │   ├── pytorch.py
│   │   │   ├── pytorch_tabnet.py
│   │   │   ├── sklearn.py
│   │   │   ├── tensorflow.py
│   │   │   └── xgboost.py
│   │   ├── packaging.py
│   │   └── packaging_utils.py
│   ├── predictor
│   │   ├── __init__.py
│   │   └── predictor.py
│   ├── schema
│   │   ├── __init__.py
│   │   ├── backend.py
│   │   ├── config.py
│   │   ├── dataset.py
│   │   ├── env.py
│   │   ├── log.py
│   │   ├── model.py
│   │   ├── packaging.py
│   │   ├── paths.py
│   │   ├── predict.py
│   │   ├── request.py
│   │   ├── singleton.py
│   │   ├── storage.py
│   │   └── types.py
│   ├── settings
│   │   ├── __init__.py
│   │   ├── backend.py
│   │   └── storage.py
│   └── utils
│       ├── __init__.py
│       ├── config.py
│       ├── constants.py
│       ├── env.py
│       ├── hash.py
│       ├── log_utils.py
│       ├── package.py
│       ├── pipeline.py
│       ├── predict.py
│       ├── readme.py
│       ├── resources.py
│       ├── source_code.py
│       ├── types.py
│       └── version_utils.py
├── pyproject.toml
└── tests
    ├── __init__.py
    ├── components
    │   ├── __init__.py
    │   ├── test_auth.py
    │   ├── test_dataset.py
    │   ├── test_metrics.py
    │   ├── test_models.py
    │   ├── test_params.py
    │   └── test_projects.py
    └── models
        ├── __init__.py
        └── saving
            ├── __init__.py
            ├── test_catboost.py
            ├── test_keras.py
            ├── test_lightgbm.py
            ├── test_pytorch.py
            ├── test_sklearn.py
            ├── test_tensorflow.py
            └── test_xgboost.py
```

## Reporting Bugs

To report any bugs you have faced while using PureML package, please

1. Report it in [Discord](https://discord.gg/xNUHt9yguJ) channel
2. Open an [issue](https://github.com/PureMLHQ/PureML/issues)

<br />

## Contributing and Developing

Lets work together to improve the features for everyone. Here's step one for you to go through our [Contributing Guide](./CONTRIBUTING.md). We are already waiting for amazing ideas and features which you all have got.

Work with mutual respect. Please take a look at our public [Roadmap here](https://pureml.notion.site/7de13568835a4cf18913307503a2cdd4?v=82199f96833a48e5907023c8a8d565c6).

<br />

## Community

To get quick updates of feature releases of PureML, follow us on:

[<img alt="Twitter" height="20" src="https://img.shields.io/badge/Twitter-1DA1F2?style=for-the-badge&logo=twitter&logoColor=white" />](https://twitter.com/getPureML) [<img alt="LinkedIn" height="20" src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" />](https://www.linkedin.com/company/PuremlHQ/) [<img alt="GitHub" height="20" src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white" />](https://github.com/PureMLHQ/PureML) [<img alt="GitHub" height="20" src="https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white" />](https://discord.gg/DBvedzGu)

<br/>

## 📄 License

See the [Apache-2.0](./License) file for licensing information.
