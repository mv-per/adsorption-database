from contextlib import contextmanager
from pathlib import Path
from h5py import File


class StorageProvider:
    def get_file_path(self) -> Path:

        return Path(
            Path(__file__).parent.absolute() / "storage" / "storage.hdf5"
        )  # pragma: no cover

    @contextmanager
    def get_editable_file(self) -> File:
        """
        Get a storage file object in a context manager fashion.

        This method returns a file object that provides read and write access to a storage file. The file is automatically
        closed when the context is exited using the 'with' statement.

        Returns:
            File: The storage file object.

        Example:
            >>> my_obj = MyClass()
            >>> with my_obj.get_editable_file() as file:
            ...     # Access the storage file using 'file' as the file object
            ...     # Read from or write to the storage file here
            ...
            # File is automatically closed when the context is exited
        """
        f = File(self.get_file_path().resolve(), "a")
        yield f
        f.close()

    @contextmanager
    def get_readable_file(self) -> File:
        """
        Get a storage file object in a context manager fashion.

        This method returns a file object that provides read and write access to a storage file. The file is automatically
        closed when the context is exited using the 'with' statement.

        Returns:
            File: The storage file object.

        Example:
            >>> my_obj = MyClass()
            >>> with my_obj.get_readable_file() as file:
            ...     # Access the storage file using 'file' as the file object
            ...     # Read from the storage file here
            ...
            # File is automatically closed when the context is exited
        """
        f = File(self.get_file_path().resolve(), "r")
        yield f
        f.close()
