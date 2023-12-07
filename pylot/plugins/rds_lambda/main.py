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
    else:
        query_data = json.loads(query_data)

    query_data = {'rds_config': query_data, 'is_test': True}


    rsp = rds.invoke_rds_lambda(query_data)
    ret_dict = json.loads(rsp.get('Payload').read().decode('utf-8'))

    # Download results from S3
    file = rds.download_file(bucket=ret_dict.get('bucket'), key=ret_dict.get('key'), results=results)
    print(
        f'{ret_dict.get("count")} {query_data.get("rds_config").get("records")} records obtained: '
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


def main(query=None, records=None, **kwargs):
    query_rds(query_data=query, record_type=records)
    print('Complete')

    return 0
