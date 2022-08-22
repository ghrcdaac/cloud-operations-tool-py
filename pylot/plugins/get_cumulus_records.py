import json
import os

import boto3

from .helpers.pylot_helpers import PyLOTHelpers


class GetCumulusRecords:
    def __init__(self, parser) -> None:
        self.parser = parser

    def read_json_file(self, filename):
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.loads(file.read())

        return data

    def get_cumulus_records(self, argv):
        if set(argv).isdisjoint(['-h', '--help']):
            cml = PyLOTHelpers().get_cumulus_api_instance()
        args = self.parser.parse_args(argv)
        kwargs = {}
        if args.filter:
            for ele in args.filter:
                temp = ele.split('=')
                kwargs[temp[0]] = temp[1]
        if args.fields:
            kwargs['fields'] = ','.join(args.fields)

        lambda_arn = os.getenv('OPENSEARCH_LAMBDA_ARN')
        if not lambda_arn and args.query_data[0]:
            raise Exception(f'The ARN for the OpenSearch lambda is not defined. Provide it as an environment variable.')

        if lambda_arn and args.query_data:
            data = self.read_json_file(args.query_data[0])

            # Invoke OpenSearch lambda
            payload = {
                'query': data,
                'record_type': str(args.record_type[0]).rstrip('s'),
                'limit': None if args.limit[0] == 0 else args.limit[0]
            }
            print(f'Invoking OpenSearch lambda...')
            client = boto3.client('lambda')
            rsp = client.invoke(
                FunctionName=lambda_arn,
                Payload=json.dumps(payload).encode('utf-8')
            )
            if rsp.get('StatusCode') != 200:
                raise Exception(f'The OpenSearch lambda failed. Check the Cloudwatch logs for '
                                f'{os.getenv("OPENSEARCH_LAMBDA_ARN")}')

            # Download results from S3
            print('Downloading query results...')
            temp = rsp.get('Payload').read().decode('utf-8')
            ret_dict = json.loads(temp)
            s3_client = boto3.client('s3')
            rsp = s3_client.get_object(
                Bucket=ret_dict.get('bucket'),
                Key=ret_dict.get('key')
            )

            with open('query_results.json', 'w+') as json_file:
                json.dump(rsp.get('Body').read().decode('utf-8'), fp=json_file, indent=2)

            ret = f'Query results: {os.getcwd()}/query_results.json'

        else:
            data = cml.get_generic_records(record_type=args.record_type[0], limit=args.limit[0], **kwargs)
            ret = data.get("results", data)
            if args.count[0] == "true":
                data_meta = data.get("meta", data)
                ret = {args.record_type[0]: {'count': data_meta.get('count', 0)}}

        return ret


def initialize(init_program) -> None:
    init_program.register('get_cumulus_records', GetCumulusRecords)
