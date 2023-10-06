import argparse
import os
import unittest

from pylot.plugins.opensearch.main import return_parser, OpenSearch


class TestOpenSearch(unittest.TestCase):
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

    def test_query_opensearch(self):
        pass
