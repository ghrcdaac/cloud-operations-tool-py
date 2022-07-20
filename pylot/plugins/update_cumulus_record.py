import json
from typing import Union

from .helpers.pylot_helpers import PyLOTHelpers


class UpdateCumulusRecord:
    def __init__(self, parser) -> None:
        self.parser = parser

    def read_json_file(self, filename):
        with open(filename, 'r') as file:
            data = json.loads(file.read())

        return data

    def update_collection(self, argv) -> Union[object, None]:
        if set(argv).isdisjoint(['-h', '--help']):
            cml = PyLOTHelpers().get_cumulus_api_instance()

        args = self.parser.parse_args(argv)
        data = self.read_json_file(args.collection_data[0])
        response = cml.update_collection(data=data)

        return response

    def update_provider(self, argv) -> Union[object, None]:
        if set(argv).isdisjoint(['-h', '--help']):
            cml = PyLOTHelpers().get_cumulus_api_instance()

        args = self.parser.parse_args(argv)
        data = self.read_json_file(args.provider_data[0])
        response = cml.update_provider(data=data)

        return response

    def update_granule(self, argv) -> Union[object, None]:
        if set(argv).isdisjoint(['-h', '--help']):
            cml = PyLOTHelpers().get_cumulus_api_instance()

        args = self.parser.parse_args(argv)
        data = self.read_json_file(args.granule_data[0])
        response = cml.update_granule(data=data)

        return response


def initialize(init_program) -> None:
    init_program.register('update_collection', UpdateCumulusRecord)
    init_program.register('update_provider', UpdateCumulusRecord)
    init_program.register('update_granule', UpdateCumulusRecord)
