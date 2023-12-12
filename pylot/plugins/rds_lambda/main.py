import json
import os

import boto3


class QueryRDS:
    @staticmethod
    def read_json_file(filename, **kwargs):
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.loads(file.read())

        return data

    def invoke_rds_lambda(self, query_data, lambda_client=None, **kwargs):
        if not lambda_client:
            lambda_client = boto3.client('lambda')
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

    def download_file(self, bucket, key, results, s3_client=None):
        if not s3_client:
            s3_client = boto3.client('s3')
        print('Downloading query results...')
        s3_client.download_file(
            Bucket=bucket,
            Key=key,
            Filename=f'{os.getcwd()}/{results}'
        )

        file = f'{os.getcwd()}/{results}'
        return file


def query_rds(query, results='query_results.json', **kwargs):
    rds = QueryRDS()
    if isinstance(query, str) and os.path.isfile(query):
        query = rds.read_json_file(query)
    else:
        query = json.loads(query)

    query = {'rds_config': query, 'is_test': True}

    rsp = rds.invoke_rds_lambda(query)
    ret_dict = json.loads(rsp.get('Payload').read().decode('utf-8'))

    # Download results from S3
    file = rds.download_file(bucket=ret_dict.get('bucket'), key=ret_dict.get('key'), results=results)
    print(
        f'{ret_dict.get("count")} {query.get("rds_config").get("records")} records obtained: '
        f'{os.getcwd()}/{results}'
    )
    return file


def return_parser(subparsers):
    query = {
        "records": "granules",
        "where": "name LIKE nalma% ",
        "columns": ["granule_id", "status"],
        "limit": 10
    }
    subparser = subparsers.add_parser(
        'rds_lambda',
        help='This plugin is used to submit queries directly to the cumulus RDS bypassing the cumulus API.',
        description='Submit queries to the Cumulus RDS instance.\n'
                    f'Example query: {json.dumps(query)}'
    )
    subparser.add_argument(
        'query',
        help='A file containing an RDS Lambda query: <filename>.json or a json query string '
             'using the RDS DSL syntax: https://github.com/ghrcdaac/ghrc_rds_lambda?tab=readme-ov-file#querying',
        metavar='query'
    )
    subparser.add_argument(
        '-r', '--results',
        help='The name to give to the results file.',
        metavar='',
        default='query_results.json'
    )


def main(**kwargs):
    query_rds(**kwargs)
    print('Complete')

    return 0
