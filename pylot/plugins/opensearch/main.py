import json
import os
import concurrent.futures
import pathlib

import boto3
from ..helpers.pylot_helpers import PyLOTHelpers


class OpenSearch:
    @staticmethod
    def read_json_file(filename, **kwargs):
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.loads(file.read())

        return data

    @staticmethod
    def invoke_opensearch_lambda(query_data, record_type, terminate_after, lambda_client=boto3.client('lambda'), **kwargs):
        lambda_arn = os.getenv('OPENSEARCH_LAMBDA_ARN')
        if not lambda_arn:
            raise ValueError('The ARN for the OpenSearch lambda is not defined. Provide it as an environment variable.')

        # Invoke OpenSearch lambda
        payload = {
            'config': {
                'query': query_data,
                'record_type': str(record_type).rstrip('s'),
                'terminate_after': int(terminate_after)}
        }

        print('Invoking OpenSearch lambda...')
        rsp = lambda_client.invoke(
            FunctionName=lambda_arn,
            Payload=json.dumps(payload).encode('utf-8')
        )
        print(rsp)
        if rsp.get('StatusCode') != 200:
            raise Exception(
                f'The OpenSearch lambda failed. Check the Cloudwatch logs for {os.getenv("OPENSEARCH_LAMBDA_ARN")}'
            )

        return rsp

    @staticmethod
    def download_file(bucket, key, results, s3_client=boto3.client('s3')):
        print('Downloading query results...')
        s3_client.download_file(
            Bucket=bucket,
            Key=key,
            Filename=f'{os.getcwd()}/{results}'
        )

        file = f'{os.getcwd()}/{results}'
        return file


def query_opensearch(query_data, record_type, results='query_results.json', terminate_after=100, **kwargs):
    open_search = OpenSearch()
    if isinstance(query_data, str) and os.path.isfile(query_data):
        query_data = open_search.read_json_file(query_data)

    rsp = open_search.invoke_opensearch_lambda(query_data, record_type, terminate_after)
    ret_dict = json.loads(rsp.get('Payload').read().decode('utf-8'))

    # Download results from S3
    file = open_search.download_file(ret_dict.get('Bucket'), ret_dict.get('Key'), results)
    print(f'{ret_dict.get("record_count")} {record_type} records obtained: {os.getcwd()}/{results}')
    return file


def return_parser(subparsers):
    subparser = subparsers.add_parser(
        'opensearch',
        help='This plugin is used to submit queries directly to OpenSearch bypassing the cumulus API.',
        description='Submit queries to opensearch'
    )
    choices = ['granule', 'collection', 'provider', 'pdr', 'rule', 'logs', 'execution', 'reconciliationReport']
    choice_str = str(choices).strip('[').strip(']').replace("'", '')
    subparser.add_argument(
        'record_type',
        help=f'The OpenSearch record type to be queried: {choice_str}',
        metavar='record_type',
        choices=choices
    )
    subparser.add_argument(
        '-t', '--terminate-after',
        help='Limit the number of records returned from OpenSearch. Default is 100. Use 0 to retrieve all matches.',
        metavar='',
        default=100
    )
    subparser.add_argument(
        '-r', '--results',
        help='The name to give to the OpenSearch results file.',
        metavar='',
        default='query_results.json'
    )

    group = subparser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '-q', '--query',
        help='The name of a file containing an OpenSearch query: <filename>.json or a json query string '
             'using the OpenSearch DSL: \'{"query": {"term": {"collectionId": "goesimpacts___1"}}}\'. '
             'See: https://opensearch.org/docs/latest/opensearch/query-dsl/index/ ',
        metavar=''
    )

    subparser.add_argument(
        '-u', '--update-data',
        help='The name of a json file containing key values pairs to update records with: <filename>.json',
        metavar=''
    )

    subparser.add_argument(
        '-d', '--delete',
        help='The name of a json file containing a cumulus bulk delete definition. The ids will be populated'
             'from the query results: <filename>.json',
        metavar=''
    )

    subparser.add_argument(
        '-b', '--bulk',
        help='If True the Cumulus bulk delete endpoint will be used for delete operations',
        metavar='',
        default=False
    )


def process_update_data(update_data, query_results):
    if not os.path.isfile(update_data):
        update_data = f'{pathlib.Path(__file__).parent.resolve()}/{update_data}'

    print(f'Attempting to update using data file: {update_data} ')
    with open(update_data, 'r', encoding='utf-8') as json_file:
        update_dict = json.load(json_file)

    for record in query_results:
        update_dictionary(record, update_dict)
        if not isinstance(record.get('productVolume'), str):
            record.update({'productVolume': str(record.get('productVolume'))})

    return query_results


def update_dictionary(results_dict, update_dict):
    for k, v in update_dict.items():
        if isinstance(v, dict):
            results_dict[k] = update_dictionary(update_dict.get(k, {}), v)
        else:
            results_dict[k] = v

    return results_dict


def bulk_delete_cumulus(delete_file, query_results):
    cml = PyLOTHelpers().get_cumulus_api_instance()
    if not os.path.isfile(delete_file):
        delete_file = f'{pathlib.Path(__file__).parent.resolve()}/{delete_file}'
    print(f'Opening delete definition: {delete_file}')
    with open(delete_file, 'r+', encoding='utf-8') as delete_definition:
        delete_config = json.load(delete_definition)

    id_array = []
    for granule in query_results:
        granule_id = granule.get('granuleId')
        id_array.append(granule_id)
    print('Adding granule IDs to delete request...')
    delete_config.update({'ids': id_array})

    # Execute bulk delete
    print('Submitting bulk delete request...')
    rsp = cml.bulk_delete(delete_config)
    print(f'Check bulk delete status using: pylot cumulus_api get async_operation {rsp.get("id")}')


def thread_function(function, records):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for record in records:
            futures.append(executor.submit(function, record))
        for future in concurrent.futures.as_completed(futures):
            print(future.result())


def delete_cumulus(query_results):
    cml = PyLOTHelpers().get_cumulus_api_instance()

    records_to_update = []
    for record in query_results:
        product_volume = record.get('productVolume', '')
        if not isinstance(product_volume, str):
            record.update({'product_volume': str(product_volume)})
            records_to_update.append(record)

    if records_to_update:
        update_cumulus('granule', records_to_update)

    granule_ids = [x.get('granuleId') for x in query_results]
    print('Removing from CMR...')
    thread_function(cml.remove_granule_from_cmr, granule_ids)
    print('CMR removal complete\n')

    print('Deleting records...')
    print(granule_ids)
    thread_function(cml.delete_granule, granule_ids)
    print('Deletion complete\n')


def update_cumulus(record_type, query_results):
    print('Updating records...')
    cml = PyLOTHelpers().get_cumulus_api_instance()
    update_function = getattr(cml, f'update_{record_type}')
    thread_function(update_function, query_results)
    print('Updating complete\n')


def main(record_type, bulk=False, results=None, query=None, update_data=None, delete=None, **kwargs):
    results_file = query_opensearch(query_data=query, record_type=record_type, results=results, **kwargs)

    if update_data or delete:
        with open(results_file, 'r', encoding='utf-8') as results_file:
            query_results = json.load(results_file)

        # Remove extra OpenSearch information
        i = 0
        while i < len(query_results):
            query_results[i] = query_results[i].get('_source')
            i += 1

        if update_data:
            updated_results = process_update_data(update_data, query_results)
            query_results = updated_results
            update_cumulus(record_type, updated_results)

        if delete:
            if bulk:
                bulk_delete_cumulus(delete, query_results)
            else:
                delete_cumulus(query_results)

    return 0
