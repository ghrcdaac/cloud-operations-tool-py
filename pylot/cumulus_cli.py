import argparse
import importlib
import json
import os
import sys
from json import JSONDecodeError


def import_plugins():
    plugin_filter = {
        'helpers'
    }
    plugins = {}
    plugin_dir = f'{os.path.abspath(os.path.dirname(__file__))}/plugins'
    for file in os.listdir(plugin_dir):
        if not file.startswith('_') and file not in plugin_filter:
            module = importlib.import_module(f'pylot.plugins.{file}.{file}')
            plugins[file] = module

    return plugins


def main():
    plugins = import_plugins()
    # Create argparser
    parser = argparse.ArgumentParser(
        usage='<positional_argument> -h to access help for each plugin. \n',
        description='PyLOT command line utility.'
    )

    # load plugin parsers
    subparsers = parser.add_subparsers(dest='command')
    subparsers.metavar = '                    '
    for name, module in plugins.items():
        try:
            module.return_parser(subparsers)
        except AttributeError:
            raise ValueError(f'Plugin {name} does not have a return_parser function.')

    args, unknown = parser.parse_known_args()
    print(f'args: {args}')
    for value in vars(args).values():
        if not value:
            parser.print_help()
            sys.exit(1)

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

    keyword_args = {**vars(args), **keyword_args}
    # Try to call the plugin's main
    command = keyword_args.pop('command')
    # print(command)
    # print(plugins.get(command))
    getattr(plugins.get(command), 'main')(**keyword_args)

    return 0


if __name__ == '__main__':
    main()
    pass
