#!/usr/bin/python
"""OP notifications tool"""

import logging

from hdx.api.configuration import Configuration
from hdx.data.dataset import Dataset
from hdx.data.hdxobject import HDXError

logger = logging.getLogger(__name__)


class OPNotifications:
    def __init__(
        self, configuration: Configuration
    ):
        self._configuration = configuration

