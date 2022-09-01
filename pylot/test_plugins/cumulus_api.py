from collections import defaultdict
from inspect import getmembers, isfunction

from pylot.plugins import PyLOTHelpers
from pylot import CumulusApi


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


def return_parser(subparsers):
    args_t = defaultdict(set)
    for member_function in getmembers(CumulusApi, is_action_function):
        split_kwargs = str(member_function[0]).split('_', maxsplit=1)
        args_t.setdefault(split_kwargs[0], {split_kwargs[1]}).add(split_kwargs[1])

    parser = subparsers.add_parser('cumulus_api', help='Cumulus cli plugin help text')
    subparsers_cli = parser.add_subparsers()
    for command, options in args_t.items():
        t = str(sorted(list(options))).replace("'", '')
        # subparser = subparsers.add_parser(command, help=f'{t}', description='Descri')
        subparser = subparsers_cli.add_parser(command, help=f'{t}', description='Descri')
        # subparser = subparsers_cli.add_parser(command, help=f'The subparser help text can be anything',
        #                                       description='Description of the sub parser here')
        subparser.add_argument(command, nargs='?', choices=t, help=f'{t}', metavar='')


def main(args, **kwargs):
    cml = PyLOTHelpers().get_cumulus_api_instance()
    for command, target in vars(args).items():
       res = getattr(cml, f'{command}_{target}')(**kwargs)

    print(res)
    return 'success'
