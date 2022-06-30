import json
import os
import pathlib
from tempfile import mkdtemp
from dataclasses import dataclass
from datetime import datetime


from ..cumulus_api import CumulusApi


@dataclass
class PyLOTHelpers:

    @classmethod
    def get_config_options(cls):
        with open(os.path.join(pathlib.Path(__file__).parent.absolute(),
                               './config.json'), 'r', encoding='utf-8') as _file:
            options = json.load(_file)
        return options


    @staticmethod
    def get_hash_token_file():
        now : datetime  = datetime.now()
        captured_time : int = 60
        for ele in range(0,60, 15):
            if now.minute<ele:
                captured_time = ele
                break
        return f"{now.day}-{now.hour}-{captured_time}"

    @classmethod
    def get_cumulus_api_instance(cls):
        """ Get Cumulus instance with cached token"""
        get_hashed_file_name = cls.get_hash_token_file()
        token: str
        tempfile = f'{mkdtemp()}/{get_hashed_file_name}'
        if not os.path.isfile(tempfile):
            with open(tempfile, 'w', encoding='utf-8') as _file:
                cml = CumulusApi()
                _file.write(cml.TOKEN)
        else:
            with open(tempfile, 'r', encoding='utf-8') as _file:
                token = _file.readline()
                cml = CumulusApi(token=token)
        return cml