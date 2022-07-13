from argparse import ArgumentParser
from dataclasses import dataclass
from typing import Any, ClassVar, Dict


@dataclass
class PyLOTOptionsFactory():

    character_creation_instances: ClassVar[dict] = {}

    @classmethod
    def register(cls, prog_name:str, creation_inst):
        """Create new instance"""
        cls.character_creation_instances[prog_name] = creation_inst


    @classmethod
    def create(cls, arguments: Dict[str, Any]):
        """
        Will accept arguments as follow
        {'prog' : {'name': '<name>', 'flags' : [<flags>]}}
        """

        prog = arguments['prog']
        prog_name = prog['name']
        try:
            creation_inst = cls.character_creation_instances[prog_name]
            flags = prog['flags']
            parser = ArgumentParser(prog=prog_name)
            for flag in flags:
                name_or_flags = flag.pop('name_or_flags')
                parser.add_argument(*name_or_flags.split(), **flag)
            return creation_inst(parser)
        except KeyError:
            raise ValueError(f"Unknown prog name {prog_name}")