import inspect
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
        function_name = str(value).rsplit('.', maxsplit=1)[-1]
        if function_name.startswith('_'):
            ret = False

    return ret


def extract_action_target_args():
    # Actions -> targets -> params
    action_target_dict = {}
    for member_function in getmembers(CumulusApi, is_action_function):
        arguments_set = set()
        inspection = inspect.getfullargspec(member_function[1])
        fas = inspect.getfullargspec(member_function[1])
        # print(f'{member_function[0]}: {fas.args}')
        # print(f'{member_function[0]}: {inspect.getdoc(member_function[1])}')
        # temp = inspect.getdoc(member_function[1])
        # print(temp.split(':'))
        # print(f'{member_function[0]}: {inspect.getcomments(member_function[1])}')
        for argument in inspection.args[1:]:
            arguments_set.add(argument)
        # print(target_parameters)
        split_action_target = str(member_function[0]).split('_', maxsplit=1)
        if len(arguments_set) == 0:
            arguments_set = ''
        # print(f'Handling {split_action_target[0]} and {split_action_target[1]}')
        action_target_dict.setdefault(
            split_action_target[0], {split_action_target[1]: arguments_set}
        )[split_action_target[1]] = arguments_set
        # print(action_target_dict)

    return action_target_dict


def generate_parser(subparsers, action_target_dict):
    cumulus_api_parser = subparsers.add_parser(
        'cumulus_api',
        help='This plugin provides a commandline interface to the cumulus api endpoints.',
        description='Provides commandline access to the cumulus api. To see available arguments '
                    'check the cumulus documentation here: https://nasa.github.io/cumulus-api/#cumulus-api\n'
                    'If more than 10 records are needed to be returned use the limit keyword argument: limit=XX\n'
                    'Examples: \n'
                    ' - pylot cumulus_api list collection fields="name,version"\n'
                    ' - pylot cumulus_api update granule \'{"collectionId": "nalmaraw___1", "granuleId": '
                    '"LA_NALMA_firetower_220706_063000.dat", "status": "completed"}\'\n'
                    ' - pylot cumulus_api update granule update.json',
        usage=SUPPRESS,
        formatter_class=RawTextHelpFormatter
    )

    action_subparsers = cumulus_api_parser.add_subparsers(dest='action')
    action_subparsers.metavar = '               '
    for action_k, target_v in action_target_dict.items():
        options = ', '.join(target_v)
        action_parser = action_subparsers.add_parser(
                action_k, help=options,
                description=f'{action_k} action for the cumulus API',
                usage=SUPPRESS,
            )
        target_subparsers = action_parser.add_subparsers(dest='target')
        target_subparsers.metavar = '               '
        for target_k, argument_v in target_v.items():
            # print(f'creating parser: {target_k}')
            params = ', '.join(argument_v)
            # print(f'sorted params: {params}')
            target_subparser = target_subparsers.add_parser(
                target_k, help=f'',
                usage=SUPPRESS,
                description=f'{target_k} target for cumulus API commands'
            )
            for argument in argument_v:
                # print(f'adding: {x}')
                arg_help_text = ''
                # print(argument)
                if argument == 'data':
                    arg_help_text = f"a json file <filename>.json or a json string containing {target_k} {action_k}" \
                                    f" definition: \'{{\"field_1\": \"value_1\", \"field_2\": \"value_2\"}}\'"
                else:
                    arg_help_text = f'Provide a {argument}'
                    pass
                target_subparser.add_argument(argument, nargs='?', help=arg_help_text)
            pass
    pass


def return_parser(subparsers):
    new_command_dict = extract_action_target_args()
    return generate_parser(subparsers, new_command_dict)


def return_parser_old(subparsers):
    action_target_dict = defaultdict(set)
    for member_function in getmembers(CumulusApi, is_action_function):
        parameters = set()
        inspection = inspect.getfullargspec(member_function[1])
        # print(f'{member_function[0]}: {inspect.getfullargspec(member_function[1])}')
        for x in inspection.args[1:]:
            parameters.add(x)
        # print(parameters)
        split_action_target = str(member_function[0]).split('_', maxsplit=1)
        action_target_dict.setdefault(split_action_target[0], {split_action_target[1]}).add(split_action_target[1])
        # print(action_target_dict)

    # print(targets)
    parser = subparsers.add_parser(
        'cumulus_api',
        help='This plugin provides a commandline interface to the cumulus api endpoints.',
        description='Provides commandline access to the cumulus api. To see available arguments '
                    'check the cumulus documentation here: https://nasa.github.io/cumulus-api/#cumulus-api\n'
                    'If more than 10 records are needed to be returned use the limit keyword argument: limit=XX\n'
                    'Examples: \n'
                    ' - pylot cumulus_api hello list collections fields="name,version"\n'
                    ' - pylot cumulus_api update granule \'{"collectionId": "nalmaraw___1", "granuleId": '
                    '"LA_NALMA_firetower_220706_063000.dat", "status": "completed"}\' \n'
                    ' - pylot cumulus_api update granule update.json',
        usage=SUPPRESS
    )
    subparsers_cli = parser.add_subparsers()
    for action, target in action_target_dict.items():
        sorted_options = str(sorted(list(target))).replace("'", '')
        subparser = subparsers_cli.add_parser(
            action, help=f'{sorted_options}',
            usage=f'{action} <positional argument>',
            description=f'{action} action for the cumulus API'
        )

        sorted_options_list = sorted_options.replace('[', '').replace(']', '').replace(' ', '').split(',')
        subparser.add_argument(action, nargs='?', default=' ', choices=sorted_options_list, help=f'{sorted_options}',
                               metavar='')


def post_process_data_arg(filename):
    with open(filename, 'r') as file:
        data_dict = json.load(file)

    return data_dict


def main(**kwargs):
    cml = PyLOTHelpers().get_cumulus_api_instance()
    print(f'here {__file__}: {kwargs}')
    action = kwargs.pop('action')
    target = kwargs.pop('target')

    data_val = kwargs.get('data', None)
    if data_val and data_val.endswith('.json'):
        kwargs.update({'data': post_process_data_arg(data_val)})

    results = []
    while True:
        print(f'{action}_{target}: kwargs: {kwargs}')
        response = getattr(cml, f'{action}_{target}')(**kwargs)
        try:
            search_context = response.get('meta', {}).get('searchContext')
        except AttributeError:
            search_context = None
            pass

        if search_context:
            count = response.get("meta", {}).get("count")
            results += response.get('results', [])
            kwargs.update({'searchContext': search_context})
            if len(results) >= kwargs.get('limit',  10) or len(results) >= count:
                break
        else:
            # If there is no searchContext we have all of the results
            results = response
            break

    print(json.dumps(results, indent=2, sort_keys=True))

    return 0
