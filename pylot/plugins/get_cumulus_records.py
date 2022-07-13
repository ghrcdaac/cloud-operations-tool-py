
from .helpers.pylot_helpers import PyLOTHelpers


class GetCumulusRecords():
    def __init__(self,parser) -> None:
        self.parser = parser

    def get_cumulus_records(self, argv):
        if set(argv).isdisjoint(['-h', '--help']):
            cml = PyLOTHelpers().get_cumulus_api_instance()
        args = self.parser.parse_args(argv)
        kwargs = {}
        if args.filter:
            for ele in args.filter:
                temp = ele.split('=')
                kwargs[temp[0]] = temp[1]
        if args.fields:
            kwargs['fields'] = ','.join(args.fields)
        data = cml.get_generic_records(record_type=args.record_type[0], limit=args.limit[0], **kwargs)
        if args.count[0] == "true":
            data_meta = data.get("meta", data)
            return {args.record_type[0]: {'count': data_meta.get('count', 0)}}

        return data.get("results", data)


def initialize(init_program) ->  None:
    init_program.register('get_cumulus_records', GetCumulusRecords)
