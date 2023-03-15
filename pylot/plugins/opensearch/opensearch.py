import collections
import json
import os
import concurrent.futures

import boto3
from ..helpers.pylot_helpers import PyLOTHelpers


class OpenSearch:
    @staticmethod
    def read_json_file(filename, **kwargs):
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.loads(file.read())

        return data

    @staticmethod
    def query_opensearch(query_data, record_type, results='query_results.json', terminate_after=100, **kwargs):
        lambda_arn = os.getenv('OPENSEARCH_LAMBDA_ARN')
        if not lambda_arn:
            raise Exception('The ARN for the OpenSearch lambda is not defined. Provide it as an environment variable.')

        # Invoke OpenSearch lambda
        payload = {
            'config': {
                'query': query_data,
                'record_type': str(record_type).rstrip('s'),
                'terminate_after': int(terminate_after)}
        }

        print('Invoking OpenSearch lambda...')
        client = boto3.client('lambda')
        rsp = client.invoke(
            FunctionName=lambda_arn,
            Payload=json.dumps(payload).encode('utf-8')
        )
        if rsp.get('StatusCode') != 200:
            raise Exception(
                f'The OpenSearch lambda failed. Check the Cloudwatch logs for {os.getenv("OPENSEARCH_LAMBDA_ARN")}'
            )

        # Download results from S3
        print('Downloading query results...')
        ret_dict = json.loads(rsp.get('Payload').read().decode('utf-8'))
        # print(f'ret_dict: {ret_dict}')
        s3_client = boto3.client('s3')
        s3_client.download_file(
            Bucket=ret_dict.get('bucket'),
            Key=ret_dict.get('key'),
            Filename=f'{os.getcwd()}/{results}'
        )

        ret = f'{ret_dict.get("record_count")} {record_type} records obtained: {os.getcwd()}/{results}'
        return ret


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
        '-d', '--data',
        help='The name of a file containing a json query: <filename>.json',
        metavar=''
    )
    group.add_argument(
        '-q', '--query',
        help='A json query string using the OpenSearch DSL: '
             'https://opensearch.org/docs/latest/opensearch/query-dsl/index/ '
             'Example: \'{"query": {"term": {"collectionId": "goesimpacts___1"}}}\'',
        metavar=''
    )

    subparser.add_argument(
        '-u', '--update-data',
        help='A json file with desired fields and values. '
             'Example: {"status": "running"} would update all records that match the provided OpenSearch query to '
             'have a running status. Any number of fields can be used.',
        metavar=''
    )


def process_update_data(update_data, results='query_results.json'):
    results_file = f'{os.getcwd()}/{results}'
    with open(results_file, 'r', encoding='utf-8') as json_file:
        query_results = json.load(json_file)

    # Remove extra OpenSearch information
    i = 0
    while i < len(query_results):
        query_results[i] = query_results[i].get('_source')
        i += 1

    update_file = f'{os.getcwd()}/{update_data}'
    print(f'Attempting to update using data file: {update_file} ')
    with open(update_file, 'r', encoding='utf-8') as json_file:
        update_dict = json.load(json_file)

    for record in query_results:
        update_dictionary(record, update_dict)

    return query_results


def update_dictionary(results_dict, update_dict):
    for k, v in update_dict.items():
        if isinstance(v, collections.Mapping):
            results_dict[k] = update_dictionary(update_dict.get(k, {}), v)
        else:
            results_dict[k] = v

    return results_dict


def update_cumulus(record_type, query_results):
    cml = PyLOTHelpers().get_cumulus_api_instance()
    update_function = getattr(cml, f'update_{record_type}')

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for record in query_results:
            futures.append(executor.submit(update_function, record))
        for future in concurrent.futures.as_completed(futures):
            print(future.result())

    print(f'Updated {len(query_results)} records.')


def main(record_type, results=None, query=None, data=None, update_data=None, **kwargs):
    query = json.loads(query) if query else OpenSearch.read_json_file(data)
    res = OpenSearch.query_opensearch(query_data=query, record_type=record_type, results=results, **kwargs)
    print(res)
    if update_data:
        updated_results = process_update_data(update_data)
        update_cumulus(record_type, updated_results)

    return 0
