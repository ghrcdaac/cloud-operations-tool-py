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
    def query_rds(payload, results='query_results.json', **kwargs):
        lambda_arn = os.getenv('RDS_LAMBDA_ARN')
        if not lambda_arn:
            raise Exception('The ARN for the RDS lambda is not defined. Provide it as an environment variable.')

        # Invoke RDS lambda
        print('Invoking RDS lambda...')
        client = boto3.client('lambda')
        rsp = client.invoke(
            FunctionName=lambda_arn,
            Payload=json.dumps(payload).encode('utf-8')
        )
        if rsp.get('StatusCode') != 200:
            raise Exception(
                f'The RDS lambda failed. Check the Cloudwatch logs for {os.getenv("RDS_LAMBDA_ARN")}'
            )

        # Download results from S3
        ret_dict = json.loads(rsp.get('Payload').read().decode('utf-8'))
        print(f'Query matched {ret_dict.get("count")} records.')
        print(f'Downloading results to file: {os.getcwd()}/{results}')
        s3_client = boto3.client('s3')
        s3_client.download_file(
            Bucket=ret_dict.get('bucket'),
            Key=ret_dict.get('key'),
            Filename=f'{os.getcwd()}/{results}'
        )
        print(f'Deleting remote S3 results file: {ret_dict.get("bucket")}/{ret_dict.get("key")}')
        s3_client.delete_object(
            Bucket=ret_dict.get('bucket'),
            Key=ret_dict.get('key')
        )

        file = f'{os.getcwd()}/{results}'

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


def main(record_type, results=None, query=None, query_string=None, **kwargs):
    rds = QueryRDS()
    query = rds.read_json_file(query) if query else json.loads(query_string)
    print(f'Using query: {json.dumps(query)}')
    rds.query_rds(payload=query)
    print('Complete')
    return 0
