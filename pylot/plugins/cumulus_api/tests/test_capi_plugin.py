import argparse
import inspect
import unittest

from pylot.plugins.cumulus_api.main import is_action_function, extract_action_target_args, generate_parser


class FakeClass:
    temp = ''
    def __init__(self):
        temp_2 = ''

    def public_function(self, data, not_data):
        self.__private_function(data, not_data)
        pass

    def __private_function(self, data, not_data):
        pass

    @staticmethod
    def static_function(data, not_data):
        pass


class TestCumulusApi(unittest.TestCase):
    def test_fake_class(self):
        fc = FakeClass()
        fc.public_function('', '')
        fc.static_function('', '')
        pass

    def test_is_action_function(self):
        fc = FakeClass()
        action_function_names = []

        for member in inspect.getmembers(fc, is_action_function):
            action_function_names.append(member[0])

        self.assertEqual(action_function_names, ['public_function', 'static_function'])

    def test_extract_action_target_args(self):
        res = extract_action_target_args(FakeClass)
        self.assertEqual(res, {'public': {'function': ['data', 'not_data']}, 'static': {'function': ['not_data']}})

    def test_generate_parser(self):
        parser = argparse.ArgumentParser(
            usage='<plugin> -h to access help for each plugin. \n',
            description='PyLOT command line utility.'
        )

        # load plugin parsers
        subparsers = parser.add_subparsers(title='plugins', dest='command', required=True)
        res = generate_parser(subparsers, extract_action_target_args(FakeClass))
        print(res)


if __name__ == '__main__':
    pass


