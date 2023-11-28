import json
import os
import pathlib
from time import time
from dataclasses import dataclass
from tempfile import gettempdir

from cumulus_api import CumulusApi


@dataclass
class PyLOTHelpers:

    @classmethod
    def get_config_options(cls):
        with open(os.path.join(pathlib.Path(__file__).parent.absolute(),
                               '../config.json'), 'r', encoding='utf-8') as _file:
            options = json.load(_file)
        return options

    @classmethod
    def get_cumulus_api_instance(cls):
        token_file = f'{gettempdir()}/pylot_token/token'
        token = None
        if os.path.isfile(token_file):
            file_stat = os.stat(token_file)
            if int(time()) - int(file_stat.st_mtime) < 3600:
                with open(token_file, 'r', encoding='utf-8') as _file:
                    token = _file.readline()

        cml = CumulusApi(token=token)
        if not token and cml.TOKEN:
            with open(token_file, 'w', encoding='utf-8') as _file:
                cml = CumulusApi()
                _file.write(cml.TOKEN)

        return cml
