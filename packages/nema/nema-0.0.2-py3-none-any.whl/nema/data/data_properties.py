from dataclasses import dataclass, field
import shutil
import tempfile
import os

from nema.utils.file_name import generate_random_file_name


@dataclass
class DataProperties:

    @property
    def is_blob_data(self):
        return False

    @property
    def data_type(self):
        raise NotImplementedError("This method should be implemented by the subclass")

    def get_value(self):
        raise NotImplementedError("This method should be implemented by the subclass")

    def __nema_marshall__(self):
        raise NotImplementedError("This method should be implemented by the subclass")

    @classmethod
    def __nema_unmarshall__(cls, data: dict):
        raise NotImplementedError("This method should be implemented by the subclass")


@dataclass
class SingleValue(DataProperties):

    def __nema_marshall__(self):
        return {"value": self.value}

    @classmethod
    def __nema_unmarshall__(cls, data: dict):
        return cls(value=data["value"])

    def get_value(self):
        return self.value


@dataclass
class BooleanValue(SingleValue):
    value: bool = False

    @property
    def data_type(self):
        return "BOOL"


@dataclass
class StringValue(SingleValue):
    value: str = ""

    @property
    def data_type(self):
        return "STRING"


@dataclass
class IntegerValue(SingleValue):
    value: int = 0

    @property
    def data_type(self):
        return "INT"


@dataclass
class FloatValue(SingleValue):
    value: float = 0.0

    @property
    def data_type(self):
        return "FLOAT"


@dataclass
class BlobDataProperties(DataProperties):

    @property
    def is_blob_data(self):
        return True


@dataclass
class FileDataProperties(BlobDataProperties):
    _file_name: str = ""
    _temp_file: tempfile.NamedTemporaryFile = field(init=False, default=None)
    temp_file_name: str = field(init=False, default=None)

    def __nema_marshall__(self):
        return {"file_name": self._file_name}

    @classmethod
    def __nema_unmarshall__(cls, data: dict):
        return cls(_file_name=data["file_name"])

    def __enter__(self):
        self._temp_file = tempfile.NamedTemporaryFile(mode="w+b", delete=False)
        self.temp_file_name = self._temp_file.name
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self._temp_file and not self._temp_file.closed:
            self._temp_file.flush()
            self._temp_file.close()

    @property
    def file_extension(self):
        return self._file_name.split(".")[-1]

    def write_data_to_file_and_return_file_name(self, destination_folder: str):
        # move to destination folder
        output_file_name = generate_random_file_name(self.file_extension)
        destination_file_path = os.path.join(destination_folder, output_file_name)
        shutil.move(self.temp_file_name, destination_file_path)

        return output_file_name
