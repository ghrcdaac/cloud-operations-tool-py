import argparse
import os
import unittest
from unittest.mock import patch, MagicMock

from pylot.plugins.opensearch.main import return_parser, OpenSearch, update_dictionary, thread_function, \
    bulk_delete_cumulus, process_update_data, delete_cumulus, update_cumulus, query_opensearch


class TestOpenSearch(unittest.TestCase):
    def tearDown(self) -> None:
        os.environ.pop('OPENSEARCH_LAMBDA_ARN', '')

    def test_return_parser(self):
        parser = argparse.ArgumentParser(
            usage='<plugin> -h to access help for each plugin. \n',
            description='PyLOT command line utility.'
        )

        # load plugin parsers
        subparsers = parser.add_subparsers(title='plugins', dest='command', required=True)
        return_parser(subparsers)

    def test_read_json_file(self):
        opensearch = OpenSearch()
        data = opensearch.read_json_file(f'{os.path.dirname(os.path.realpath(__file__))}/test_file.json')
        self.assertEqual(data, {"some": "json"})

    @patch('json.loads')
    @patch('pylot.plugins.opensearch.main.OpenSearch')
    def test_query_opensearch(self, mock_opensearch, mock_json_loads):
        mock_opensearch.invoke_opensearch_lambda.return_value = ''
        mock_opensearch.invoke_opensearch_lambda.return_value = ''
        query_opensearch(query_data={}, record_type='')
        pass

    def test_invoke_opensearch_lambda(self):
        opensearch = OpenSearch()
        os.environ['OPENSEARCH_LAMBDA_ARN'] = 'FAKE_ARN'
        mock_client = MagicMock()
        mock_client.invoke.return_value = {'StatusCode': 200}
        opensearch.invoke_opensearch_lambda(
            query_data={}, record_type='', terminate_after=0, lambda_client=mock_client
        )

    def test_invoke_opensearch_lambda_arn_exception(self):
        opensearch = OpenSearch()
        mock_client = MagicMock()
        with self.assertRaises(ValueError) as context:
            opensearch.invoke_opensearch_lambda(
                query_data={}, record_type='', terminate_after=0, lambda_client=mock_client
            )
            self.assertTrue('The ARN for the OpenSearch lambda is not defined' in context.exception)

    def test_download_file(self):
        opensearch = OpenSearch()
        opensearch.download_file(bucket='', key='', results='', s3_client=MagicMock())

    def test_process_update_data(self):
        query_res = [{'productVolume': 1, 'testField': 'testValue'}]
        updated_res = process_update_data('/tests/fake_update.json', query_res)
        expected = [{'productVolume': '1', 'testField': 'testValueUpdated'}]
        self.assertEqual(updated_res, expected)

    def test_update_dictionary(self):
        target = {'key_1': {'key_2': 'value_1'}, 'key_3': 'value_3'}
        update = {'key_1': {'key_2': 'value_1_updated'}, 'key_4': 'value_4'}
        target = update_dictionary(target, update)
        print(target)
        expected = {'key_1': {'key_2': 'value_1_updated'}, 'key_3': 'value_3', 'key_4': 'value_4'}
        self.assertEqual(target, expected)

    @patch('pylot.plugins.helpers.pylot_helpers.PyLOTHelpers.get_cumulus_api_instance')
    def test_bulk_delete_cumulus(self, gcapi):
        bulk_delete_cumulus('/tests/fake_delete.json', [{'granuleId': 'fake_granuleId'}])

    def test_thread_function(self):
        thread_function(print, [1, 2, 3])

    @patch('pylot.plugins.helpers.pylot_helpers.PyLOTHelpers.get_cumulus_api_instance')
    def test_delete_cumulus(self, gcapi):
        query_results = [{'productVolume': 1}]
        delete_cumulus(query_results)

    @patch('pylot.plugins.helpers.pylot_helpers.PyLOTHelpers.get_cumulus_api_instance')
    def test_update_cumulus(self, gcapi):
        query_res = [{'record': 'value'}]
        update_cumulus('test', query_res)

