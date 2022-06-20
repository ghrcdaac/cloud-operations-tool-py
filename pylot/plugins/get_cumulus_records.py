
from argparse import ArgumentParser
from .helpers import PyLOTHelpers
class GetCumulusRecords():
    def __init__(self, flags) -> None:
        self.flags = flags

    def init_parser(self):
        parser = ArgumentParser()
        parser.prog = "get_cumulus_records"
        for flag in self.flags:
            parser.add_argument(**flag)
        return parser

        


    def get_cumulus_records(self, argv):
        
        parser = self.init_parser()
        if set(argv).isdisjoint(['-h', '--help']):
            cml = PyLOTHelpers().get_cumulus_api_instance()
    

        
        
            

        args = parser.parse_args(argv)
        kwargs = {}
        if args.filter:
            for ele in args.filter:
                temp = ele.split('=')
                kwargs[temp[0]] = temp[1]
        if args.fields:
            kwargs['fields'] = ','.join(args.fields)
        #print(f"{args=}, {kwargs=}")
        data = cml.get_generic_records(record_type=args.record_type[0], limit=args.limit[0], **kwargs)
        return data.get("results", data)

def initialize(init_program) ->  None:
    init_program.register('get_cumulus_records', get_cumulus_records)