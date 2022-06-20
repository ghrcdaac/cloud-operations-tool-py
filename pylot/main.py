from dataclasses import dataclass, field
import argparse
import sys
from .plugins import PyLOTHelpers
from .options_factory import  create
from .options_loader import load_plogins


@dataclass
class PyLOTClient:
    options: dict = field(default_factory=dict[str, str])
    
    @classmethod
    def get_supported_options(cls):
        cls.options = PyLOTHelpers.get_config_options()
        supported_options : list[str] = []
        for progs in cls.options['options']:
            supported_options.append(progs['prog']['name'])
        return supported_options

    @classmethod
    def cli(cls):
        """

        :return:
        :rtype:
        """
        argv = sys.argv
        if len(argv) <= 1:
            argv.append('-h')
        supported_options = cls.get_supported_options()
        if not set(argv).isdisjoint(supported_options):
            [argv.remove(ele) for ele in ['-h', '--help'] if ele in argv]

        parser = argparse.ArgumentParser(description='Python cLoud operations Tool (PyLOT)', prog='PyLOT')
        parser.add_argument('option_to_use', choices=supported_options)
        args, unknown = parser.parse_known_args()
        

        # parser.add_argument('-extra', '--extra', dest='extra', default=unknown, help='Arguments to sub command')
        for arg in unknown:
            if arg.startswith(("-", "--")):
                parser.add_argument(arg, nargs='+')
        parser.parse_args()

        load_plogins(cls.options['plugins'])
        options_added = [create(item) for item in cls.options['options']]
        for option_added in options_added:
            print(option_added)
        if not unknown:
            getattr(cls.pylot_options, args.option_to_use)(['-h'])

        # result = getattr(cls.pylot_options, args.option_to_use)(unknown)
        # print(json.dumps(result, indent=4))
        print("hello")


if __name__ == "__main__":
    cc = PyLOTClient()
    cc.cli()



