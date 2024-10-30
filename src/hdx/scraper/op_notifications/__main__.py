#!/usr/bin/python
"""
Top level script. Calls other functions that generate datasets that this
script then creates in HDX.

"""

import logging
from os.path import dirname, expanduser, join

from hdx.api.configuration import Configuration
from hdx.facades.infer_arguments import facade
from hdx.utilities.downloader import Download
from hdx.utilities.errors_onexit import ErrorsOnExit
from hdx.utilities.path import temp_dir
from hdx.utilities.retriever import Retrieve
from op_notifications import OPNotifications

logger = logging.getLogger(__name__)

_USER_AGENT_LOOKUP = "hdx-hapi-op-notifications"
_SAVED_DATA_DIR = "saved_data"  # Keep in repo to avoid deletion in /tmp


def main(
    save: bool = True,
    use_saved: bool = False,
) -> None:
    with ErrorsOnExit() as errors_on_exit:
        with temp_dir() as tempdir:
            with Download() as downloader:
                with open("errors.txt", "w") as fp:
                    pass
                retriever = Retrieve(
                    downloader=downloader,
                    fallback_dir=tempdir,
                    saved_dir=_SAVED_DATA_DIR,
                    temp_dir=tempdir,
                    save=save,
                    use_saved=use_saved,
                )
                configuration = Configuration.read()

                op_notifications = OPNotifications(
                    configuration,
                    retriever,
                    errors_on_exit,
                )
                op_notifications.read_yaml()
                op_notifications.check_hdx()

                if len(errors_on_exit.errors) > 0:
                    errors = errors_on_exit.errors
                    errors = ["The following datasets mey need updating"] + sorted(errors)
                    with open("errors.txt", "w") as fp:
                        fp.writelines(_ + " | " for _ in errors)
                logger.info("Finished processing")


if __name__ == "__main__":
    facade(
        main,
        hdx_site="dev",
        user_agent_config_yaml=join(expanduser("~"), ".useragents.yaml"),
        user_agent_lookup=_USER_AGENT_LOOKUP,
        project_config_yaml=join(dirname(__file__), "config", "project_configuration.yaml"),
    )
