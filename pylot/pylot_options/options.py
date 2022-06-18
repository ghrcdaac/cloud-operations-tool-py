import os
from argparse import ArgumentParser
from datetime import datetime
from dataclasses import dataclass
from ..cumulus_api import CumulusApi

@dataclass
class PyLOTOptions:
    parser: ArgumentParser = ArgumentParser()

    @staticmethod
    def hash_token_file():
        now : datetime  = datetime.now()
        captured_time : int = 60
        for ele in range(0,60, 15):
            if now.minute<ele:
                captured_time = ele
                break
        return f"{now.day}-{now.hour}-{captured_time}"

    @classmethod
    def __get_cumulus_api_instance(self):
        """ Get Cumulus instance with cached token"""
        get_hashed_file_name = self.hash_token_file()
        token: str
        tempfile = f'/tmp/{get_hashed_file_name}'
        if not os.path.isfile(tempfile):
            with open(tempfile, 'w', encoding='utf-8') as _file:
                
                cml = CumulusApi()
                _file.write(cml.TOKEN)
        
        else:
            with open(tempfile, 'r', encoding='utf-8') as _file:
                token = _file.readline()
                cml = CumulusApi(token=token)
        return cml

    @classmethod
    def get_cumulus_records(self, argv):
        if set(argv).isdisjoint(['-h', '--help']):
            cml = self.__get_cumulus_api_instance()
        self.parser.prog = "get_cumulus_records"
        self.parser.add_argument('-t', '--type', dest="record_type", nargs=1, required=True,
                                choices=['collections', 'granules', 'providers', 'rules'],
                                help="Record type (Granule| Granules|Collections)")
        self.parser.add_argument('-f', '--filter', nargs='+', dest='filter',
                                help='filter the returned data (where x = y)  ')
        self.parser.add_argument('-s', '--select', nargs='+', dest='fields',
                                help="select some fields from the requested data")
        self.parser.add_argument('-l', '--limit', nargs=1, dest='limit', default=[10],
                                help='Limit the requested data')

        args = self.parser.parse_args(argv)
        kwargs = {}
        if args.filter:
            for ele in args.filter:
                temp = ele.split('=')
                kwargs[temp[0]] = temp[1]
        if args.fields:
            kwargs['fields'] = ','.join(args.fields)
        #print(f"{args=}, {kwargs=}")
        data = cml.get_generic_records(record_type=args.record_type[0], limit=args.limit[0], **kwargs)
        return data.get("results", data)
