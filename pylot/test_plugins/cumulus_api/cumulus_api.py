import json
from argparse import SUPPRESS, RawTextHelpFormatter
from collections import defaultdict
from inspect import getmembers, isfunction

from .main import CumulusApi
from ..helpers.pylot_helpers import PyLOTHelpers


def is_action_function(value):
    ret = True
    if not isfunction(value):
        ret = False
    else:
        function_name = str(value).split('.')[-1]
        if function_name.startswith('_'):
            ret = False

    return ret


def return_parser(subparsers):
    args_t = defaultdict(set)
    for member_function in getmembers(CumulusApi, is_action_function):
        split_kwargs = str(member_function[0]).split('_', maxsplit=1)
        args_t.setdefault(split_kwargs[0], {split_kwargs[1]}).add(split_kwargs[1])

    parser = subparsers.add_parser(
        'cumulus_api',
        help='This Describes the cumulus api',
        description='Provides commandline access to the cumulus api. To see available arguments '
                    'check the cumulus documentation here: https://nasa.github.io/cumulus-api/#cumulus-api\n'
                    'Every argument is a positional argument with a string value so it can just be supplied after the '
                    'command: \n '
                    'Examples: \n'
                    ' - list collection fields="name,version": would only return the name and version of the first 10 '
                    'collections\n'
                    ' - update granule data=\'{"collectionId": "nalmaraw___1", "granuleId": '
                    '"LA_NALMA_firetower_220706_063000.dat", "status": "completed"}\'',
        usage=SUPPRESS,
        formatter_class=RawTextHelpFormatter)
    subparsers_cli = parser.add_subparsers()
    for command, options in args_t.items():
        sorted_options = str(sorted(list(options))).replace("'", '')
        subparser = subparsers_cli.add_parser(
            command, help=f'{sorted_options}',
            usage=f'{command} {sorted_options} [-h]',
            description=f'{command} the following: '
        )

        subparser.add_argument(command, nargs='?', choices=sorted_options, help=f'{sorted_options}', metavar='')


def main(args, **kwargs):
    cml = PyLOTHelpers().get_cumulus_api_instance()
    for command, target in vars(args).items():
        res = getattr(cml, f'{command}_{target}')(**kwargs)

    print(json.dumps(res, indent=2, sort_keys=True))
    return 'success'
