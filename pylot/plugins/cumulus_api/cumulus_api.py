import inspect
import json
import os
from argparse import SUPPRESS, RawTextHelpFormatter
from inspect import getmembers, isfunction

from .main import CumulusApi
from ..helpers.pylot_helpers import PyLOTHelpers


def is_action_function(value):
    """
    Used to determine if the value passed in is a public method. The value passed in is assumed to be in the form
    module.function_name
    :param value: string to determine if it is a publish function or not
    :return: boolean
    """
    ret = True
    if not isfunction(value):
        ret = False
    else:
        function_name = str(value).rsplit('.', maxsplit=1)[-1]
        if function_name.startswith('_'):
            ret = False

    return ret


def extract_action_target_args():
    """
    Extracts and processes all public member functions in the CumulusApi file and returns a dictionary of the form
    {"action": {"target": {arguments}}}
    These values are derived from the function signatures update_granule(self, data) where update, granule, and data are
    the action, target, and arguments respectively.
    """
    # Actions -> targets -> params
    action_target_dict = {}
    for member_function in getmembers(CumulusApi, is_action_function):
        arguments_set = set()
        inspection = inspect.getfullargspec(member_function[1])
        for argument in inspection.args[1:]:
            arguments_set.add(argument)
        split_action_target = str(member_function[0]).split('_', maxsplit=1)
        if len(arguments_set) == 0:
            arguments_set = ''
        action_target_dict.setdefault(
            split_action_target[0], {split_action_target[1]: arguments_set}
        )[split_action_target[1]] = arguments_set

    return action_target_dict


def generate_parser(subparsers, action_target_dict):
    cumulus_api_parser = subparsers.add_parser(
        'cumulus_api',
        help='This plugin provides a commandline interface to the cumulus api endpoints.',
        description='Provides commandline access to the cumulus api. To see available arguments '
                    'check the cumulus documentation here: https://nasa.github.io/cumulus-api/#cumulus-api\n'
                    'If more than 10 records are needed to be returned use the limit keyword argument: limit=XX\n'
                    'Examples: \n'
                    ' - pylot cumulus_api list collections fields="name,version"\n'
                    ' - pylot cumulus_api list collections fields="name,version" limit=12 name__in="msuttp,msutls"\n'
                    ' - pylot cumulus_api update granule \'{"collectionId": "nalmaraw___1", "granuleId": '
                    '"LA_NALMA_firetower_220706_063000.dat", "status": "completed"}\' \n'
                    ' - pylot cumulus_api update granule update.json\n',
        usage='<action> -h to see help for each action.',
        formatter_class=RawTextHelpFormatter
    )
    action_subparsers = cumulus_api_parser.add_subparsers(title='actions', dest='action', required=True)
    for action_k, target_v in action_target_dict.items():
        action_parser = action_subparsers.add_parser(
                action_k, help=f'{action_k} action for the cumulus API',
                usage=f'{action_k} <target> ',
                description=f'{action_k} action for the cumulus API'
            )
        target_subparsers = action_parser.add_subparsers(title='target', dest='target', required=True)
        for target_k, argument_v in target_v.items():
            plural = ''
            for arg in argument_v:
                plural += f'<{arg}> '
            target_subparser = target_subparsers.add_parser(
                target_k, help=f'',
                usage=f'{target_k} {plural}',
                description=f'{target_k} target for cumulus API commands'
            )
            for argument in argument_v:
                if argument == 'data':
                    arg_help_text = f"a json file <filename>.json or a json string containing {target_k} {action_k}" \
                                    f" definition: \'{{\"field_1\": \"value_1\", \"field_2\": \"value_2\"}}\'"
                else:
                    arg_help_text = f'Provide a {argument}'
                target_subparser.add_argument(argument, nargs='?', help=arg_help_text)
            pass
    pass


def return_parser(subparsers):
    new_command_dict = extract_action_target_args()
    return generate_parser(subparsers, new_command_dict)


def main(**kwargs):
    cml = PyLOTHelpers().get_cumulus_api_instance()
    action = kwargs.pop('action')
    target = kwargs.pop('target')
    data_val = kwargs.get('data', None)
    if data_val:
        if os.path.isfile(data_val):
            with open(data_val, 'r') as file:
                kwargs.update({'data': json.load(file)})
        else:
            kwargs.update({'data': json.loads(data_val)})

    results = []
    while True:
        response = getattr(cml, f'{action}_{target}')(**kwargs)
        try:
            search_context = response.get('meta', {}).get('searchContext')
        except AttributeError:
            search_context = None

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
