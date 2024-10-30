#!/usr/bin/python
"""OP notifications tool"""

import logging

from hdx.api.configuration import Configuration
from hdx.data.dataset import Dataset
from hdx.utilities.errors_onexit import ErrorsOnExit
from hdx.utilities.retriever import Retrieve

logger = logging.getLogger(__name__)


class OPNotifications:
    def __init__(
        self, configuration: Configuration, retriever: Retrieve, temp_dir: str, errors: ErrorsOnExit
    ):
        self._configuration = configuration
        self._retriever = retriever
        self._temp_dir = temp_dir
        self.data = {}
        self.errors = errors

    def read_yaml(self):
        base_url = self._configuration["config_url"]
        op_yaml = self._retriever.download_yaml(base_url)
        for admin_level in ["admintwo", "adminone", "national"]:
            for pipeline_name, config in op_yaml[f"operational_presence_{admin_level}"].items():
                self.data[pipeline_name] = {
                    "dataset": config["dataset"],
                    "resource": config["resource"],
                }

    def check_hdx(self):
        for pipeline_name, dataset_info in self.data.items():
            countryiso3 = pipeline_name.split("_")[-1]
            dataset_name = dataset_info["dataset"]
            dataset = Dataset.read_from_hdx(dataset_name)
            resource_names = [r["name"] for r in dataset.get_resources()]
            expected_index = self._configuration["resource_index_exceptions"].get(countryiso3, 0)
            resource_index = resource_names.index(dataset_info["resource"])
            if resource_index != expected_index:
                self.errors.add(f"{countryiso3}: {dataset_name}")
