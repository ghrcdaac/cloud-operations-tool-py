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
            plugin = f'pylot.plugins.{file}.main'
            print(f'Loading plugin: {plugin}')
            module = importlib.import_module(plugin)
            plugins[file] = module

    return plugins


def create_arg_parser(plugins):
    parser = argparse.ArgumentParser(
        usage='<plugin> -h to access help for each plugin. \n',
        description='PyLOT command line utility.'
    )

    # load plugin parsers
    subparsers = parser.add_subparsers(title='plugins', dest='command', required=True)
    for name, module in plugins.items():
        try:
            module.return_parser(subparsers)
        except AttributeError:
            raise ValueError(f'Plugin {name} does not have a return_parser function.')
    return parser


def process_unknown_args(unknown):
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

    return keyword_args


def main():
    if len(sys.argv) == 1:
        sys.argv.append('-h')
    plugins = import_plugins()
    parser = create_arg_parser(plugins)
    args, unknown = parser.parse_known_args()
    keyword_args = {**vars(args), **process_unknown_args(unknown)}
    # Try to call the plugin's main
    command = keyword_args.pop('command')
    plugin = plugins.get(command)
    getattr(plugin, 'main')(**keyword_args)

    return 0


if __name__ == '__main__':
    main()
    pass
