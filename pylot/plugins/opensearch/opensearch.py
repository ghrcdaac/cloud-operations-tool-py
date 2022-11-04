import json
import os

import boto3


class OpenSearch:
    @staticmethod
    def read_json_file(filename):
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.loads(file.read())

        return data

    @staticmethod
    def query_opensearch(query_data, record_type, terminate_after=100):
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
            Filename=f'{os.getcwd()}/query_results.json'
        )

        ret = f'{ret_dict.get("record_count")} records obtained: {os.getcwd()}/query_results.json'
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
    group = subparser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '-d', '--data',
        help='The name of a file containing a json query: <filename>.json',
        metavar=''
    )
    group.add_argument(
        '-q', '--query',
        help='A JSON query string using the OpenSearch DSL: '
             'https://opensearch.org/docs/latest/opensearch/query-dsl/index/ '
             'Example: \'{"query": {"term": {"collectionId": "goesimpacts___1"}}}\'',
        metavar=''
    )


def main(record_type, query=None, data=None, **kwargs):
    query = json.loads(query) if query else OpenSearch.read_json_file(data)
    res = OpenSearch.query_opensearch(query_data=query, record_type=record_type, **kwargs)
    print(res)

    return 0
