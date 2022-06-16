from argparse import ArgumentParser
from dataclasses import dataclass
from ..cumulus_api import CumulusApi


@dataclass
class PyLOTOptions:
    parser: ArgumentParser = ArgumentParser()

    @staticmethod
    def get_cumulus_api_instance():
        return CumulusApi()

    @classmethod
    def get_records(cls, argv):
        cml = CumulusApi()
        cls.parser.prog = "get_records"
        cls.parser.add_argument('-t', '--type', dest="record_type", nargs=1, required=True,
                                choices=['collections', 'granules', 'providers', 'rules'],
                                help="Record type (Granule| Granules|Collections)")
        cls.parser.add_argument('-f', '--filter', nargs='+', dest='filter',
                                help='filter the returned data (where x = y)  ')
        cls.parser.add_argument('-s', '--select', nargs='+', dest='fields',
                                help="select some fields from the requested data")
        cls.parser.add_argument('-l', '--limit', nargs=1, dest='limit', default=[10],
                                help='Limit the requested data')

        args = cls.parser.parse_args(argv)
        kwargs = {}
        if args.filter:
            for ele in args.filter:
                temp = ele.split('=')
                kwargs[temp[0]] = temp[1]
        if args.fields:
            kwargs['fields'] = ','.join(args.fields)
        #print(f"{args=}, {kwargs=}")
        data = cml.get_generic_records(record_type=args.record_type[0], limit=args.limit[0], **kwargs)
        return data["results"]
