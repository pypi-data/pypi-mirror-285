import os
import shutil

from ..provider import StorageProvider


class LocalStorageProvider(StorageProvider):
    def __init__(self, base_path: str):
        mod_base_path = os.path.join(base_path, "pureml_storage")
        if not os.path.exists(mod_base_path):
            os.makedirs(mod_base_path)
        self.base_path = mod_base_path

    def upload_file(self, source_file, relative_destination):
        destination = os.path.join(self.base_path, relative_destination)
        shutil.copy(source_file, destination)

    def download_file(self, relative_source, destination_file):
        source = os.path.join(self.base_path, relative_source)
        shutil.copy(source, destination_file)

    def exists(self, file_path) -> bool:
        return os.path.exists(file_path)
