from typing import Callable, Any
from dataclasses import dataclass
from typing import Protocol

@dataclass
class PyLOTOptions(Protocol):
    def crud_records(self, argv: list[str]) -> dict:
        """Generic function to Create Read Update Delete records"""
        ...

options_creation_functs: dict[str, Callable[..., PyLOTOptions]] = {}

def register(prog_name:str, creation_func:  Callable[..., PyLOTOptions]):
    """Register a new program"""
    options_creation_functs[prog_name] = creation_func

def unregister(prog_name:str):
    """Register a new charachter type"""
    options_creation_functs.pop(prog_name, False)

def create(arguments: dict[str, Any]) -> PyLOTOptions:
    arguments_copy = arguments.copy()
    prog = arguments_copy.pop('prog')
    prog_name = prog.pop('name')
    try:
        creation_funct = options_creation_functs[prog_name]
        print(creation_funct)
        return creation_funct(**prog['flags'][0])
    except KeyError:
        raise ValueError(f"Unknown program name {prog_name}")