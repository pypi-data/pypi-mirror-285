from dataclasses import dataclass
from typing import Optional
import json
import os

from nema.connectivity import ConnectivityManager


@dataclass
class Workflow:
    global_id: int
    name: str
    description: str
    output_folder: Optional[str] = None

    def marshall_create(self):
        return {
            "name": self.name,
            "description": self.description,
            "workflow_type": "NEMA.EXTERNAL_PYTHON.V0",
            "workflow_properties": {},
            "app": "",
        }

    def create(self):
        conn = ConnectivityManager()
        global_id = conn.create_workflow(self.marshall_create())
        return global_id

    def process_update(self):
        conn = ConnectivityManager()

        # read data from output folder
        if self.output_folder:
            with open(os.path.join(self.output_folder, "output.json"), "r") as f:
                raw_data = json.load(f)
        else:
            raise ValueError("Output folder not provided")

        # read files from output folder
        files = []
        files_output_folder = os.path.join(self.output_folder, "data-output")
        for file_name in os.listdir(files_output_folder):
            files.append(os.path.join(files_output_folder, file_name))

        conn.push_workflow_update(self.global_id, raw_data, files)
