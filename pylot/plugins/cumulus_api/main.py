import logging
import os
from configparser import ConfigParser, SectionProxy
from json.decoder import JSONDecodeError
from typing import Union

import requests

from .cumulus_token import CumulusToken


class CumulusApi:
    def __init__(self, use_os_env: bool = True, config_path: str = None, token: str = None):
        """
        Initiate cumulus API instance, by default it reads from OS environment
        :param config_path: absolute or relative path to config file
        :param token: earthdata token
        """
        # The user should provide the config file or the token
        if {None, False} == {config_path, token, use_os_env}:
            error = "Config file path, environment variables or token should be supplied"
            logging.error(error)
            raise ValueError(error)
        config: Union[SectionProxy, dict] = os.environ.copy()
        # If the token provided ignore the config file
        if config_path:
            config_parser = ConfigParser(config)
            config_parser.read(config_path)
            config = config_parser['DEFAULT']
        self.config = config
        self.INVOKE_BASE_URL = self.config["INVOKE_BASE_URL"].rstrip('/')
        self.cumulus_token = CumulusToken(config=config)
        self.TOKEN = token if token else self.cumulus_token.get_token()
        self.HEADERS = {'Authorization': f'Bearer {self.TOKEN}'}

    def crud_records(self, record_type, verb, data=None, **kwargs):
        """
        :param verb: HTTP requests verbs GET|POST|PUT|DELETE
        :param record_type: Provider | Collection | PDR ...
        :param data: json data to be ingested
        :return: False in case of error
        """
        allowed_verbs = ['GET', 'POST', 'PUT', 'DELETE']
        if verb.upper() not in allowed_verbs:
            return f"{verb} is not a supported http request"
        url = f"{self.INVOKE_BASE_URL}/v1/{record_type}"
        and_sign = ""
        query = ""
        for key, value in kwargs.items():
            query = f"{query}{and_sign}{key}={value}"
            and_sign = "&"
        if kwargs:
            url = f"{url}?{query}"
        re = getattr(requests, verb.lower())(url=url, json=data, headers=self.HEADERS)
        try:
            return re.json()
        except JSONDecodeError as err:

            logging.error("Cumulus CRUD: %s", err)
            return re.content
