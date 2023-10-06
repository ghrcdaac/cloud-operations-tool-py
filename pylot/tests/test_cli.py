import unittest

from pylot.pylot_cli import import_plugins, create_arg_parser, process_unknown_args


class TestCli(unittest.TestCase):
    import_plugins()

    def test_import_plugins(self):
        plugins = import_plugins()
        self.assertEqual(len(plugins), 3)

    def test_create_argparser(self):
        plugins = import_plugins()
        parser = create_arg_parser(plugins)

    def test_process_unknown_args(self):
        args = ['limit=1', 'sort_by=granuleId']
        res = process_unknown_args(args)
        self.assertEqual(res, {'limit': 1, 'sort_by': 'granuleId'})
