import json
from typing import Union

from .helpers.pylot_helpers import PyLOTHelpers


class ManageCumulusRecords:
    def __init__(self, parser) -> None:
        self.parser = parser

    def read_json_file(self, filename):
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.loads(file.read())

        return data

    def create_collection(self, argv) -> Union[object, None]:
        if set(argv).isdisjoint(['-h', '--help']):
            cml = PyLOTHelpers().get_cumulus_api_instance()

        args = self.parser.parse_args(argv)
        data = self.read_json_file(args.collection_data[0])
        response = cml.create_collection(data=data)

        return response

    def create_provider(self, argv) -> Union[object, None]:
        if set(argv).isdisjoint(['-h', '--help']):
            cml = PyLOTHelpers().get_cumulus_api_instance()

        args = self.parser.parse_args(argv)
        data = self.read_json_file(args.provider_data[0])
        response = cml.create_provider(data=data)

        return response

    def create_granule(self, argv) -> Union[object, None]:
        if set(argv).isdisjoint(['-h', '--help']):
            cml = PyLOTHelpers().get_cumulus_api_instance()

        args = self.parser.parse_args(argv)
        data = self.read_json_file(args.granule_data[0])
        response = cml.create_granule(data=data)

        return response

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

    def remove_cmr(self, argv) -> Union[object, None]:
        if set(argv).isdisjoint(['-h', '--help']):
            cml = PyLOTHelpers().get_cumulus_api_instance()

        args = self.parser.parse_args(argv)
        response = cml.remove_granule_from_cmr(args.granule_id)

        return response

    def initialize(init_program) -> None:
        init_program.register('remove_cmr', ManageCumulusRecords)


def initialize(init_program) -> None:
    init_program.register('create_collection', ManageCumulusRecords)
    init_program.register('create_provider', ManageCumulusRecords)
    init_program.register('create_granule', ManageCumulusRecords)
    init_program.register('update_collection', ManageCumulusRecords)
    init_program.register('update_provider', ManageCumulusRecords)
    init_program.register('update_granule', ManageCumulusRecords)
    init_program.register('remove_cmr', ManageCumulusRecords)
