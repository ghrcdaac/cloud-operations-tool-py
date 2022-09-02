# import importlib
# import os
#
# filter = [
#     'helpers'
# ]
#
# __all__ = []
# dir_path = os.path.dirname(os.path.realpath(__file__))
# for file in sorted(os.listdir(dir_path)):
#     if not file.startswith('_') and file not in filter:
#         __all__.append(file)
#
# for module in __all__:
#     importlib.import_module(f'.{module}', __name__)
import pkgutil

__all__ = []
for loader, module_name, is_pkg in pkgutil.walk_packages(__path__):
    __all__.append(module_name)
    _module = loader.find_module(module_name).load_module(module_name)
    globals()[module_name] = _module
