from dataclasses import dataclass
import argparse
import sys
from .pylot_options import PyLOTOptions
import json

@dataclass
class PyLOTClient:
    pylot_options: PyLOTOptions = PyLOTOptions()
    @staticmethod
    def get_supported_options():
        return ["get_records"]

    @staticmethod
    def get_data(arguments):
        print("\n======= arguments =======\n", arguments)
        parser = argparse.ArgumentParser(description='Get Cumulus Data')
        parser.add_argument('-a', '--all', dest='all_things', help='All the things')

        args = parser.parse_args(arguments)
        print("\n======= args =======\n", args)

    @classmethod
    def cli(cls):
        """

        :return:
        :rtype:
        """
        argv = sys.argv
        if len(argv) <= 1:
            argv.append('-h')
        if not set(argv).isdisjoint(cls.get_supported_options()):
            [argv.remove(ele) for ele in ['-h', '--help'] if ele in argv]

        parser = argparse.ArgumentParser(description='Python cLoud operations Tool (PyLOT)', prog='PyLOT')
        parser.add_argument('option_to_use', choices=cls.get_supported_options())
        args, unknown = parser.parse_known_args()
        if not unknown:
            getattr(cls.pylot_options, args.option_to_use)(['-h'])

        # parser.add_argument('-extra', '--extra', dest='extra', default=unknown, help='Arguments to sub command')
        for arg in unknown:
            if arg.startswith(("-", "--")):
                parser.add_argument(arg, nargs='+')
        parser.parse_args()
        result = getattr(cls.pylot_options, args.option_to_use)(unknown)
        print(json.dumps(result, indent=4))


if __name__ == "__main__":
    cc = PyLOTClient()
    cc.cli()



