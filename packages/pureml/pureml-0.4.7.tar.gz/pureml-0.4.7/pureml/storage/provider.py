class StorageProvider:
    def upload_file(self, source_file, destination) -> str or None:
        """
        Upload a file to the provided relative destination path

        Returns - relative file path (str)
        """
        raise NotImplementedError("Subclasses must implement this method")

    def download_file(self, source, destination_file) -> None:
        """
        Download a file from the relative source path to the destination path

        Returns None
        """
        raise NotImplementedError("Subclasses must implement this method")

    def exists(self, file_path) -> bool:
        """
        Checks whether the file path exists

        Returns - True if exists (bool)
        """
        raise NotImplementedError("Subclasses must implement this method")
