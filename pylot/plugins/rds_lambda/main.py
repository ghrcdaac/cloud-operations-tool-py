import json
import os

import boto3


class QueryRDS:
    @staticmethod
    def read_json_file(filename, **kwargs):
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.loads(file.read())

        return data

    @staticmethod
    def invoke_rds_lambda(query_data, lambda_client=boto3.client('lambda'), **kwargs):
        lambda_arn = os.getenv('RDS_LAMBDA_ARN')
        if not lambda_arn:
            raise ValueError('The ARN for the RDS lambda is not defined. Provide it as an environment variable.')

        # Invoke RDS lambda
        print('Invoking RDS lambda...')
        rsp = lambda_client.invoke(
            FunctionName=lambda_arn,
            Payload=json.dumps(query_data).encode('utf-8')
        )
        if rsp.get('StatusCode') != 200:
            raise Exception(
                f'The RDS lambda failed. Check the Cloudwatch logs for {os.getenv("RDS_LAMBDA_ARN")}'
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


def query_rds(query_data, results='query_results.json', **kwargs):
    rds = QueryRDS()
    if isinstance(query_data, str) and os.path.isfile(query_data):
        query_data = rds.read_json_file(query_data)

    rsp = rds.invoke_rds_lambda(query_data)
    ret_dict = json.loads(rsp.get('Payload').read().decode('utf-8'))

    # Download results from S3
    file = rds.download_file(ret_dict.get('Bucket'), ret_dict.get('Key'), results)
    print(f'{ret_dict.get("record_count")} records obtained: {os.getcwd()}/{results}')
    return file


def return_parser(subparsers):
    query = {
        "rds_config": {
            "records": "granules",
            "where": "name LIKE nalma% ",
            "columns": ["granule_id", "status"],
            "limit": 10
        }
    }
    subparser = subparsers.add_parser(
        'rds_lambda',
        help='This plugin is used to submit queries directly to the cumulus RDS bypassing the cumulus API.',
        description='Submit queries to the Cumulus RDS instance.\n'
                    f'Example query: {json.dumps(query)}'
    )
    choices = ['granules', 'collections', 'providers', 'pdrs', 'rules', 'logs', 'executions', 'reconciliationReport']
    choice_str = str(choices).strip('[').strip(']').replace("'", '')
    subparser.add_argument(
        'record_type',
        help=f'The RDS table to be queried: {choice_str}',
        metavar='record_type',
        choices=choices
    )
    subparser.add_argument(
        '-l', '--limit',
        help='Limit the number of records returned from RDS. Default is 100. Use 0 to retrieve all matches.',
        metavar='',
        default=100
    )
    subparser.add_argument(
        '-r', '--results',
        help='The name to give to the results file.',
        metavar='',
        default='query_results.json'
    )

    group = subparser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '-q', '--query',
        help='The name of a file containing an RDS lambda query: <filename>.json',
        metavar=''
    )
    group.add_argument(
        '-s', '--query-string',
        help='A json query string using the RDS DSL: '
             'https://github.com/ghrcdaac/ghrc_rds_lambda#querying '
             'Example: '
             '\'{"rds_config": {"records": "", "columns": ["granule_id"], "where": "name=nalmaraw", "limit": 0}}\'',
        metavar=''
    )


def main(query=None, **kwargs):
    query_rds(query_data=query)
    print('Complete')

    return 0
