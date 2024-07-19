from dataclasses import dataclass
from typing import Dict, Optional
import json
import os

from .data import Data


@dataclass
class DataCollection:
    items: Dict[str, Data]

    def __getattr__(self, item_id: str):
        try:
            return self.items[item_id]
        except KeyError:
            raise AttributeError(
                f"This DataCollection object has no attribute '{item_id}'"
            )

    def sync_data_from_API(self, job_id: Optional[str] = None):
        # Sync data from the API

        for item in self.items.values():
            item.sync_from_API()

    def save_updates_locally(self, job_id: str):
        # Process updates

        # find which items have been used
        filtered_input_data = filter(
            lambda x: x.cache_info.number_of_times_hit > 0,
            self.items.values(),
        )

        # find which items have been updated
        filtered_output_data = filter(lambda x: x.is_updated, self.items.values())

        # output data to folder
        folder = os.path.join(".nema-output", job_id)
        os.makedirs(folder, exist_ok=True)

        data_output_folder = os.path.join(folder, "data-output")
        os.makedirs(data_output_folder, exist_ok=True)

        raw_data = [
            *[("used_data", data.global_id) for data in filtered_input_data],
            *[
                (
                    "updated_data",
                    json.dumps(
                        data.process_output_data(destination_folder=data_output_folder)
                    ),
                )
                for data in filtered_output_data
            ],
        ]

        output_file = os.path.join(folder, "output.json")
        with open(output_file, "w") as f:
            f.write(json.dumps(raw_data))

        # write to terminal the output file location
        print(f"Output written to folder: {folder}")
