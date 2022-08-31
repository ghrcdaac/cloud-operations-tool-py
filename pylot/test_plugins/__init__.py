import importlib
import os
from os.path import dirname, basename, isfile, join
import glob
modules = glob.glob(join(dirname(__file__), "*.py"))
__all__ = sorted([basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')])
# print(f'all: {__all__}')

# for x in __all__:
#     importlib.import_module(f'{os.getcwd()}/test_plugins/{x}')
from . import *
# importlib.import_module()
# print(__all__)
# print('hello')
# import importlib
# import os
# for module in os.listdir(os.path.dirname(__file__)):
#     if module == '__init__.py' or module[-3:] != '.py':
#         continue
#     importlib.__import__(module[:-3], locals(), globals())
# del module
