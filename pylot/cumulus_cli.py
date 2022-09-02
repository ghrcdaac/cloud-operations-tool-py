import argparse
import importlib
import json
import os
import sys
from json import JSONDecodeError


plugins = {}
plugin_filter = [
    'helpers'
]


def import_plugins():
    plugin_dir = f'{str(__file__).rsplit("/", maxsplit=1)[0]}/test_plugins'
    for file in os.listdir(plugin_dir):
        if not file.startswith('_') and file not in plugin_filter:
            ret = importlib.import_module(f'pylot.test_plugins.{file}.{file}')
            plugins[file] = ret


def main():
    import_plugins()

    # Create argparser
    parser = argparse.ArgumentParser(
        # prog='prog',
        usage=f'<positional_argument> -h to access help for each plugin. \n',
        description='PyLOT command line utility.')

    # load plugin parsers
    subparsers = parser.add_subparsers()
    for name, module in plugins.items():
        try:
            module.return_parser(subparsers)
        except AttributeError:
            raise ValueError(f'Plugin {name} does not have a return_parser function.')

    args, unknown = parser.parse_known_args()

    # Processed unknown arguments are keyword arguments to be passed to the request
    keyword_args = {}
    for argument in unknown:
        params = argument.split('=', maxsplit=1)
        variable = params[0]
        value = params[1]

        # Assume the value is a json string
        try:
            value = json.loads(value)
        except JSONDecodeError:
            pass

        keyword_args.update({variable: value})

    # Call plugin's main
    try:
        command = plugins.get(sys.argv[1])
        getattr(command, 'main')(args, **keyword_args)
    except AttributeError:
        raise ValueError(f'Plugin {sys.argv[1]} does not have a main function.')

    return 0


if __name__ == '__main__':
    main()
    pass
