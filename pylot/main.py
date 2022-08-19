import argparse
import json
import sys
from dataclasses import dataclass, field
from typing import Dict

import pyfiglet

from .options_factory import PyLOTOptionsFactory
from .plugins import PyLOTHelpers
from .plugins_loader import load_plugins

PYLOT_FIGLET = pyfiglet.figlet_format("PyLOT")


@dataclass
class PyLOTClient:
    options: Dict = field(default_factory=Dict[str, str])

    @classmethod
    def get_supported_options(cls):
        cls.options = PyLOTHelpers.get_config_options()
        supported_options: list[str] = []
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
        if argv[1] in ['-h', '--help']:
            print(PYLOT_FIGLET)

        supported_options = cls.get_supported_options()
        if not set(argv).isdisjoint(supported_options):
            _ = [argv.remove(ele) for ele in ['-h', '--help'] if ele in argv]
        parser = argparse.ArgumentParser(description='Python cLoud operations Tool (PyLOT)', prog='pylot')
        parser.add_argument('option_to_use', choices=supported_options)
        args, unknown = parser.parse_known_args()

        for arg in unknown:
            if arg.startswith(("-", "--")):
                parser.add_argument(arg, nargs='+')
        parser.parse_args()
        load_plugins(cls.options['plugins'])
        pylot_options = {}
        for progs in cls.options['options']:
            pylot_options.update({progs['prog']['name']: PyLOTOptionsFactory.create(progs)})
        if not unknown:
            unknown = ['-h']
            print(PYLOT_FIGLET)
        result = getattr(pylot_options[args.option_to_use], args.option_to_use)(unknown)
        if result:
            print(json.dumps(result, indent=4))


if __name__ == "__main__":
    cc = PyLOTClient()
    cc.cli()
