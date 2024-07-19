from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
from typing import Type
from copy import deepcopy

from nema.connectivity import ConnectivityManager

from .data_properties import DataProperties


@dataclass
class CacheInfo:
    last_time_updated: datetime = datetime(1970, 1, 1)
    number_of_times_hit: int = 0
    in_sync_cloud: bool = False


@dataclass
class Data:
    _global_id: str
    _data: DataProperties
    _cache_info: CacheInfo = field(default_factory=CacheInfo)
    _userdefined_id: Optional[str] = None

    @classmethod
    def init_from_cloud(
        cls,
        global_id: str,
        data_class: Type[DataProperties],
        userdefined_id: Optional[str] = None,
    ):
        data = data_class()

        return cls(
            _global_id=global_id,
            _userdefined_id=userdefined_id,
            _data=data,
        )

    @property
    def global_id(self):
        return self._global_id

    @property
    def data(self):
        # update cache info
        self._cache_info.number_of_times_hit += 1

        return self._data

    @property
    def value(self):
        return self.data.get_value()

    def update_data(self, new_data: DataProperties):
        if self._cache_info.number_of_times_hit > 0:
            raise ValueError("Data can only be updated if it has not been accessed")

        self._data = new_data
        self._cache_info.last_time_updated = datetime.now()
        self._cache_info.number_of_times_hit = 0
        self._cache_info.in_sync_cloud = False

    @property
    def userdefined_id(self):
        return self._userdefined_id

    @userdefined_id.setter
    def userdefined_id(self, value: str):
        self._userdefined_id = value

    @property
    def cache_info(self):
        return deepcopy(self._cache_info)

    def sync_from_API(self):
        # Sync data from the API

        conn = ConnectivityManager()

        raw_data = conn.pull_in_memory_data(self.global_id)

        # we need to use _data here, otherwise we record a cache hit
        self._data = self._data.__nema_unmarshall__(raw_data["data_properties"])

    def marshall_data_properties(self):
        return self._data.__nema_marshall__()

    @property
    def is_updated(self):
        return (
            self._cache_info.in_sync_cloud == False
            and self._cache_info.last_time_updated.year > 1980
        )

    @property
    def data_type(self):
        return self._data.data_type

    def process_output_data(self, destination_folder: str):

        core_dict = {
            "global_id": self.global_id,
            "data_properties": self.marshall_data_properties(),
            "data_type": self.data_type,
        }

        if self._data.is_blob_data:
            core_dict["file_name"] = self._data.write_data_to_file_and_return_file_name(
                destination_folder=destination_folder
            )

        return core_dict
