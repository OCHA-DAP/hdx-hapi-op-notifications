from os.path import join

import pytest

from hdx.api.configuration import Configuration
from hdx.data.dataset import Dataset
from hdx.scraper.op_notifications.op_notifications import OPNotifications
from hdx.utilities.downloader import Download
from hdx.utilities.errors_onexit import ErrorsOnExit
from hdx.utilities.path import temp_dir
from hdx.utilities.retriever import Retrieve
from hdx.utilities.useragent import UserAgent


class TestOPNotifications:
    @pytest.fixture(scope="function")
    def configuration(self, config_dir):
        UserAgent.set_global("test")
        Configuration._create(
            hdx_read_only=True,
            hdx_site="prod",
            project_config_yaml=join(config_dir, "project_configuration.yaml"),
        )
        return Configuration.read()

    @pytest.fixture(scope="function")
    def read_dataset(self, monkeypatch):
        def read_from_hdx(dataset_name):
            return Dataset.load_from_json(
                join(
                    "tests",
                    "fixtures",
                    "input",
                    f"dataset-{dataset_name}.json",
                )
            )

        monkeypatch.setattr(Dataset, "read_from_hdx", staticmethod(read_from_hdx))

    @pytest.fixture(scope="class")
    def fixtures_dir(self):
        return join("tests", "fixtures")

    @pytest.fixture(scope="class")
    def input_dir(self, fixtures_dir):
        return join(fixtures_dir, "input")

    @pytest.fixture(scope="class")
    def config_dir(self, fixtures_dir):
        return join("src", "hdx", "scraper", "op_notifications", "config")

    def test_op_notifications(
        self,
        configuration,
        fixtures_dir,
        input_dir,
        config_dir,
        read_dataset,
    ):
        with ErrorsOnExit() as errors_on_exit:
            with temp_dir(
                "Test_OPNotifications",
                delete_on_success=True,
                delete_on_failure=False,
            ) as tempdir:
                with Download(user_agent="test") as downloader:
                    retriever = Retrieve(
                        downloader=downloader,
                        fallback_dir=tempdir,
                        saved_dir=input_dir,
                        temp_dir=tempdir,
                        save=False,
                        use_saved=True,
                    )
                    op_notifications = OPNotifications(
                        configuration,
                        retriever,
                        errors_on_exit,
                    )
                    op_notifications.read_yaml()
                    assert op_notifications.data == {
                        "operational_presence_afg": {
                            "dataset": "afghanistan-who-does-what-where-april-to-june-2024",
                            "resource": "afghanistan-3w-operational-presence-april-june-2024.csv",
                        },
                        "operational_presence_caf": {
                            "dataset": "republique-centrafricaine-presence-operationnelle",
                            "resource": "3W_CAR_Mar2024",
                        },
                        "operational_presence_tcd": {
                            "dataset": "chad-operational-presence",
                            "resource": "3W_TCD_May2024",
                        },
                        "operational_presence_bfa": {
                            "dataset": "burkina-faso-presence-operationnelle",
                            "resource": "3W Burkina Faso March-April 2024",
                        },
                    }

                    op_notifications.check_hdx()
                    assert errors_on_exit.errors == ["tcd: chad-operational-presence"]
