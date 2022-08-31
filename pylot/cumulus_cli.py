import argparse
import inspect
import json
import sys
from collections import defaultdict
from inspect import getmembers, isfunction
from operator import attrgetter
import test_plugins


from pylot.plugins import PyLOTHelpers
from pylot.cumulus_api import CumulusApi


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
        print(f'actions: {actions}')
        actions = sorted(actions, key=attrgetter('option_strings'))
        super(SortingHelpFormatter, self).add_arguments(actions)


def main():
    # Extract module methods
    args_t = defaultdict(set)
    for member_function in getmembers(CumulusApi, is_action_function):
        split_kwargs = str(member_function[0]).split('_', maxsplit=1)
        args_t.setdefault(split_kwargs[0], {split_kwargs[1]}).add(split_kwargs[1])

    # Create argparser
    parser = argparse.ArgumentParser(
        prog='prog',
        description='Command line interface for the python cumulus API. '
                    'Each action can be used with any option as well as -h'
                    ' to see available help information.'
                    ' apply -h will show the help text for the apply action.'
                    '\nThe api documentation can be found here: '
                    'https://nasa.github.io/cumulus-api/',
        epilog='Testing epilog',
        usage=argparse.SUPPRESS)

    # For each action create a subparser and add arguments
    subparsers = parser.add_subparsers()
    for command, options in args_t.items():
        t = str(sorted(list(options))).replace("'", '')
        subparser = subparsers.add_parser(command, help=f'{t}', description='Descri')
        subparser.add_argument(command, nargs='?', choices=t, help=f'{t}', metavar='')

    line_break = subparsers.add_parser('Plugins', help='All commands past this point are non-Cumulus plugins:')
    line_break.add_argument('Plugins', help='help_meh_too', metavar='')

    # load plugin parsers
    print(f'test_plugins: {test_plugins.__all__}')
    for x in test_plugins.__all__:
        eval(f'test_plugins.{x}.return_parser(subparsers)')

    args, unknown = parser.parse_known_args()

    clsmembers = inspect.getmembers(test_plugins.__all__[-1], inspect.isclass)
    print(f'cls: {test_plugins.__all__}')
    print(f'-1: {test_plugins.__all__[-1]}')
    temp = test_plugins.opensearch.OpenSearch()

    # Processed unknown arguments are keyword arguments to be passed to the request
    keyword_args = {}
    for argument in unknown:
        arg_iter = iter(argument.split('='))
        keyword_args.update({next(arg_iter): next(arg_iter)})

    if sys.argv[1] not in test_plugins.__all__:
        cml = PyLOTHelpers().get_cumulus_api_instance()
        for k, v in vars(args).items():
            print(f'k: {k}')
            print(f'v: {v}')
            action = k
            record_type = v
            try:
                funct = getattr(cml, f'{action}_{record_type}')
                # print(f'var_names: {dir(funct)}')
                # print(f'members: {inspect.getmembers(funct).__doc__}')
                # print(f'members: {funct.__doc__}')

                # print(f'var_names: {inspect.getfullargspec(funct).args}')

                res = funct(**keyword_args)
                print(json.dumps(res, indent=2))
            except AttributeError as e:
                raise ValueError(f'"{action} {record_type}" is an invalid command. Verify options with "{action} -h".')
    else:
        print('elsing')
        t = f'test_plugins.{sys.argv[1]}.main({sys.argv[1]}.py, {args})'
        print(getattr(eval(f'test_plugins.{sys.argv[1]}'), 'main')(args, **keyword_args))
        # eval(t)

    return 0


if __name__ == '__main__':
    main()
    # a = ['a', 'b', 'c']
    # i = a.index('b')
    # print(i)
    # a[a.index()]
    pass

