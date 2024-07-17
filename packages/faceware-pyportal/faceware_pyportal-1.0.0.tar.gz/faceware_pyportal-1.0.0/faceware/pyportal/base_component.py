#############################################################################
#                                                                           #
# Copyright © 2023 Faceware Technologies, Inc.                              #
#                                                                           #
# All rights reserved.  No part of this software including any part         #
# of the coding or data forming any part thereof may be used or reproduced  #
# in any form or by any means otherwise than in accordance with any         #
# written license granted by Faceware Technologies, Inc.                    #
#                                                                           #
# Requests for permissions for use of copyright material forming            #
# part of this software (including the grant of licenses) shall be made     #
# to Faceware Technologies, Inc.                                            #
#                                                                           #
#############################################################################
"""Base class with logger and api instance."""
import logging
from . import api_requests
from typing import Optional
import re


class SensitiveDataFormatter(logging.Formatter):
    """Class used for setting up custom logs format and masking sensitive data."""

    @staticmethod
    def _filter(s):
        filters = [
            (r'"x-fti-api-key":\s*"[^"]+"',
             '"x-fti-api-key": "********"'),  # Replace api key with asterisks
        ]
        for f in filters:
            s = re.sub(f[0], f[1], s)
        return s

    def format(self, record):
        """Sets up the formatter."""
        original = logging.Formatter.format(self, record)
        return self._filter(original)


class BaseComponent():
    """Base component class to share api and log between the child classes."""
    _api: api_requests.ApiRequests = None
    _log: logging.Logger = None

    @classmethod
    def init_log(cls, parent_logger: Optional[logging.Logger] = None):
        """Creates new logger."""
        sensitive_formatter = SensitiveDataFormatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',)
        log_handler = logging.StreamHandler()
        log_handler.setFormatter(sensitive_formatter)
        if parent_logger:
            cls._log = parent_logger.getChild('pyportal')
            cls._log.setLevel(parent_logger.level)
        else:
            cls._log = logging.getLogger('pyportal')
        cls._log.addHandler(log_handler)

    @classmethod
    def init_api(cls, access_token: str, organization_id: str):
        """Initializes api with provided access token and organization id."""
        if cls._api is None:
            if cls._log is None:
                raise ValueError('Logger must be initialized before API.')
            cls._api = api_requests.ApiRequests(cls._log, access_token,
                                                organization_id)

    @property
    def api(self):
        """Returns initialized _api if any."""
        if BaseComponent._api is None:
            raise ValueError('API is not initialized')
        return BaseComponent._api

    @property
    def log(self):
        """Returns initialized _log if any."""
        if BaseComponent._log is None:
            raise ValueError('Logger is not initialized')
        return BaseComponent._log
