from pathlib import Path

import yaml
from yaml.loader import SafeLoader


class YAMLFile:
    """
    YAMLFile is base class that is used to read and write YAML files
    """

    def __init__(self, path: Path):
        super().__init__()
        self._path = path

    @property
    def path(self) -> Path:
        """
        Get the path associated with the object.

        Returns:
            Path: The path associated with the object.
        """
        return self._path

    def exists(self) -> bool:
        """
        Check if the path associated with the object exists.

        Returns:
            bool: True if the path exists, False otherwise.
        """
        return self._path.exists()

    def read(self) -> dict:
        """
        Read and load the content of the file associated with the object as a dictionary.

        Returns:
            dict: The content of the file loaded as a dictionary.
        """
        with open(self._path, "r") as stream:
            return yaml.load(stream, Loader=SafeLoader)

    def __str__(self) -> str:
        """
        Return the string representation of the path associated with the object.

        Returns:
            str: The string representation of the path.
        """
        return self._path.as_posix()


class PureMLConfigYML:
    """
    PureMLConfigYML is a class that is used to generate the configuration file `puremlconfig.yaml`
    It is capable of reading and writing the configuration file
    """

    def __init__(self, path: Path):
        self._yaml_file = YAMLFile(path)
        self._yaml_document = None

    @property
    def file(self) -> YAMLFile:
        """
        Get the YAML file associated with the object.

        Returns:
            YAMLFile: The YAML file associated with the object.
        """
        return self._yaml_file

    @property
    def data(self) -> dict:
        """
        Get the data from the YAML file associated with the object. If the YAML document is not loaded, it reads the file content.

        Returns:
            dict: The data from the YAML file.
        """
        if self._yaml_document is None:
            if self._yaml_file.exists():
                self._yaml_document = self._yaml_file.read()
            else:
                self._yaml_document = {}
        return self._yaml_document

    def save(self, data: dict = None) -> None:
        """
        Save the provided data to the YAML file associated with the object.

        Args:
            data (dict, optional): The data to be saved. If not provided, uses the existing data associated with the object.

        Returns:
            None
        """
        if data is None:
            data = self.data
        if len(data.keys()) == 0:
            print("No configuration data to save")
            return
        with open(self._yaml_file.path, "w") as stream:
            yaml.dump(data, stream, default_flow_style=False)

    def reload(self) -> None:
        """
        Reload the YAML document associated with the object by setting it to None.
        Returns:
            None
        """

        self._yaml_document = None
