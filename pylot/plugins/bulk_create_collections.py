from .helpers.pylot_helpers import PyLOTHelpers
import json
import csv


def read_csv(in_file: str) -> list:
    """
    Reads csv file and returns list of dicts representing csv
    :param in_file: Input file path
    :return: list of dicts respresenting file 
    """
    with open(in_file) as csv_file:
        collections = list(csv.DictReader(csv_file))
    return collections

def update_objects(collection: dict) -> dict:
    """
    Updates files and meta keys to reflect expect json object values
    :param collection: input collection dict
    :return: updated collection dict
    """
    # Files and Meta keys are both objects which require additional handling
    object_keys = ['files', 'meta']
    for key in object_keys:
        if key in collection:
            collection[key] = json.loads(collection[key].replace("'", '"'))
    return collection


class BulkCreateCollections:
    """
    Class for adding collections to Cumulus in bulk
    """
    def __init__(self, parser) -> None:
        self.parser = parser

    def bulk_create_collections(self, argv):
        if set(argv).isdisjoint(['-h', '--help']):
            cml = PyLOTHelpers().get_cumulus_api_instance()
        args = self.parser.parse_args(argv)
        collections = read_csv(in_file=args.path[0])
        err_response_list = list()
        success_counter = 0
        for collection in collections:
            updated_collection = update_objects(collection)
            response = cml.create_collection(data=updated_collection)
            if 'Record saved' in response['message']:
                success_counter += 1
            else: 
                response['name'] = collection['name']
                response['version'] = collection['version']
                err_response_list.append(response)
        print(f'{success_counter} records successfully saved')
        print('The following errors were encountered') if len(err_response_list) > 0 else None
        return(err_response_list)


def initialize(init_program) -> None:
    init_program.register('bulk_create_collections', BulkCreateCollections)
