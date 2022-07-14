from typing import Union
from tabulate import tabulate

from .helpers.pylot_helpers import PyLOTHelpers


class GetStatus:
    def __init__(self, parser) -> None:
        self.parser = parser

    def get_status(self, argv) -> Union[object, None]:
        if set(argv).isdisjoint(['-h', '--help']):
            cml = PyLOTHelpers().get_cumulus_api_instance()
        args = self.parser.parse_args(argv)
        kwargs = {}
        if args.filter:
            for ele in args.filter:
                temp = ele.split('=')
                kwargs[temp[0]] = temp[1]
        kwargs['fields'] = "name,version,stats"
        data = cml.list_collections(includeStats="true", **kwargs)
        results = data['results']
        headers = ["completed", "running", "failed", "queued", "total"]
        if args.output_format[0] == "json":
            return results
        if args.fields:
            headers = list(set(headers) & set(','.join(args.fields).split(',')))

        tab_data = []
        for indx, ele in enumerate(results):
            tab_data.append([indx + 1, ele["name"], ele["version"], *[ele['stats'].get(key, 0)
                                                                      for key in headers]])

        print(tabulate(tab_data, headers=["#", "name", "version"] + headers, tablefmt="fancy_grid"))
        return None


def initialize(init_program) -> None:
    init_program.register('get_status', GetStatus)
