import argparse
import inspect
import json
from collections import defaultdict
from inspect import getmembers, isfunction
from operator import attrgetter

from tabulate import tabulate

from pylot.plugins import PyLOTHelpers
from pylot.cumulus_api import CumulusApi
from test_plugins.test_plugin import return_parser, add_args


class CumulusPyCLI:
    def __init__(self):
        self.cml = PyLOTHelpers().get_cumulus_api_instance()
        pass


def is_action_function(value):
    ret = True
    if not isfunction(value):
        ret = False
    else:
        function_name = str(value).split('.')[-1]
        # print(f'function_name: {function_name}')
        if function_name.startswith('_'):
            ret = False

    return ret


class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


class SortingHelpFormatter(argparse.HelpFormatter):
    def add_arguments(self, actions):
        # print(f'actions: {actions}')
        actions = sorted(actions, key=attrgetter('prog'))
        super(SortingHelpFormatter, self).add_arguments(actions)


def main():
    # Extract module methods
    args_t = defaultdict(set)
    for member_function in getmembers(CumulusApi, is_action_function):
        split_kwargs = str(member_function[0]).split('_', maxsplit=1)
        args_t.setdefault(split_kwargs[0], {split_kwargs[1]}).add(split_kwargs[1])
    # print(json.dumps(args_t, indent=2, cls=SetEncoder))

    # Create argparser
    parser = argparse.ArgumentParser(
        prog='prog',
        description='Command line interface for the python cumulus API. '
                    'Each action can be used with any option as well as -h'
                    ' to see available help information.'
                    ' apply -h will show the help text for the apply action.'
                    '\nThe api documentation can be found here: '
                    'https://nasa.github.io/cumulus-api/',
        usage=argparse.SUPPRESS)

    # For each action create a subparser and add arguments
    subparsers = parser.add_subparsers()
    for command, options in args_t.items():
        t = str(sorted(list(options))).replace("'", '')
        subparser = subparsers.add_parser(f'{command}', help=f'{t}', description='Descri')
        # group = subparser.('valid target')
        # t = str(sorted(list(options))).replace("'", '')
        subparser.add_argument(command, nargs='?', choices=t, help=f'{t}', metavar='')

    args, unknown = parser.parse_known_args()
    # print(vars(args))

    # Processed unknown arguments are keyword arguments to be passed to the request
    keyword_args = {}
    for argument in unknown:
        arg_iter = iter(argument.split('='))
        keyword_args.update({next(arg_iter): next(arg_iter)})

    cml = PyLOTHelpers().get_cumulus_api_instance()
    for k, v in vars(args).items():
        action = k
        record_type = v
        try:
            funct = getattr(cml, f'{action}_{record_type}')
            # print(f'var_names: {dir(funct)}')
            print(f'var_names: {inspect.getfullargspec(funct).args}')

            res = funct(**keyword_args)
            print(json.dumps(res, indent=2))
        except AttributeError as e:
            raise ValueError(f'"{action} {record_type}" is an invalid command. Verify options with "{action} -h".')
    pass

    return 0


if __name__ == '__main__':
    main()
    pass
