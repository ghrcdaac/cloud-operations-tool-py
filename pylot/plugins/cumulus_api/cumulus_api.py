import json
from argparse import SUPPRESS, RawTextHelpFormatter

from ..helpers.pylot_helpers import PyLOTHelpers


def return_parser(subparsers):
    parser = subparsers.add_parser(
        'cumulus_api',
        help='This plugin provides a commandline interface to the cumulus api endpoints.',
        description='Provides commandline access to the cumulus api. \nTo see available endpoints and possible keyword '
                    'arguments check the cumulus documentation here: https://nasa.github.io/cumulus-api/#cumulus-api\n',
        usage=SUPPRESS,
        formatter_class=RawTextHelpFormatter
    )
    parser.add_argument('verb', choices=['get', 'put', 'post', 'delete'], metavar=f'verb: [get, post, put, delete]')
    parser.add_argument(
        dest='record_type',
        metavar='record_type: The endpoint to submit the request to. View the documentation to '
                'determine which endpoint pairs with each verb.\n\n'
                'Examples: \n'
                f' - pylot cumulus_api get /granules (https://nasa.github.io/cumulus-api/#list-granules)\n'
                f' - pylot cumulus_api put /collections/{{name}}/{{version}} '
                f'(https://nasa.github.io/cumulus-api/#updatereplace-collection)'
        )


def main(**kwargs):
    cml = PyLOTHelpers().get_cumulus_api_instance()
    res = cml.crud_records(**kwargs)
    print(json.dumps(res, indent=2, sort_keys=True))
    return 0
