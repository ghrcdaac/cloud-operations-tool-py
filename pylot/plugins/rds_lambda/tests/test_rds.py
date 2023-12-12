import argparse
import os
import unittest
from unittest.mock import patch, MagicMock

from pylot.plugins.rds_lambda.main import return_parser, QueryRDS, query_rds


class TestRDS(unittest.TestCase):
    def tearDown(self) -> None:
        os.environ.pop('RDS_LAMBDA_ARN', '')

    def test_return_parser(self):
        parser = argparse.ArgumentParser(
            usage='<plugin> -h to access help for each plugin. \n',
            description='PyLOT command line utility.'
        )

        # load plugin parsers
        subparsers = parser.add_subparsers(title='plugins', dest='command', required=True)
        return_parser(subparsers)

    def test_read_json_file(self):
        rds = QueryRDS()
        data = rds.read_json_file(f'{os.path.dirname(os.path.realpath(__file__))}/test_file.json')
        self.assertEqual(data, {"some": "json"})

    @patch('json.loads')
    @patch('pylot.plugins.rds_lambda.main.QueryRDS')
    def test_query_rds(self, mock_opensearch, mock_json_loads):
        mock_opensearch.invoke_rds_lambda.return_value = ''
        mock_opensearch.invoke_rds_lambda.return_value = ''
        query_rds(query={}, record_type='')
        pass

    def test_invoke_rds_lambda(self):
        rds = QueryRDS()
        os.environ['RDS_LAMBDA_ARN'] = 'FAKE_ARN'
        mock_client = MagicMock()
        mock_client.invoke.return_value = {'StatusCode': 200}
        rds.invoke_rds_lambda(query_data={}, lambda_client=mock_client)

    def test_invoke_rds_lambda_arn_exception(self):
        rds = QueryRDS()
        mock_client = MagicMock()
        with self.assertRaises(ValueError) as context:
            rds.invoke_rds_lambda(query_data={}, lambda_client=mock_client)
            self.assertTrue('The ARN for the RDS lambda is not defined' in context.exception)

    def test_download_file(self):
        rds = QueryRDS()
        rds.download_file(bucket='', key='', results='', s3_client=MagicMock())
