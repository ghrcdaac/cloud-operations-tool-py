# How To

## Basic usage
```
pylot -h
usage: <positional_argument> -h to access help for each plugin. 

PyLOT command line utility.

positional arguments:
  {cumulus_api,opensearch}
    cumulus_api         This plugin provides a commandline interface to the cumulus api endpoints.
    opensearch          This plugin is used to submit queries directly to OpenSearch bypassing the cumulus API.

optional arguments:
  -h, --help            show this help message and exit

```
The left-hand column of the help text is the action, and the right and list is the possible target. When entering the 
command the action and target are seperated by a space:
```shell
pylot cumulus_api list collections
```

The positional arguments are the options currently supported by PyLOT. If you want to get help for a positional argument run
```
pylot cumulus_api -h
Provides commandline access to the cumulus api. To see available arguments check the cumulus documentation here: https://nasa.github.io/cumulus-api/#cumulus-api
Every argument is a positional argument with a string value so it can just be supplied after the command: 
 Examples: 
 - list collection fields="name,version": would only return the name and version of the first 10 collections
 - update granule data='{"collectionId": "nalmaraw___1", "granuleId": "LA_NALMA_firetower_220706_063000.dat", "status": "completed"}'

positional arguments:
  {apply,associate,bulk,create,delete,get,granules,list,move,recover,refresh,reindex,reingest,remove,replay,run,search,serve,update}
    apply               [workflow_to_granule]
    associate           [execution]
    bulk                [delete, reingest]
    create              [collection, execution, granule, provider, reconciliation_report, rule]
    delete              [collection, execution, granule, pdr, provider, reconciliation_report, rule, token]
    get                 [async_operation, collection, elasticsearch_index, elasticsearch_indices_info, elasticsearch_reindex_status, execution, execution_status, generic_records, granule, granules_csv, instance_metadata, log, pdr, provider, reconciliation_report, rule, schema, stats_aggregate, stats_summary, version, workflow]
    granules            [bulk_op]
    list                [async_operations, collections, collections_with_active_granules, executions, granules, logs, orca_recovery_status, pdrs, providers, reconciliation_reports, rules, workflows]
    move                [granule]
    recover             [cumulus_messages]
    refresh             [token]
    reindex             [elasticsearch, elasticsearh_from_database]
    reingest            [granule]
    remove              [granule_from_cmr]
    replay              [ingest_notification]
    run                 [migration_count, rule]
    search              [executions_by_granules, workflows_by_granules]
    serve               [dashboard_from_bucket]
    update              [collection, elasticsearch_index, execution, granule, provider, rule]

optional arguments:
  -h, --help            show this help message and exit

```

### Basic usage of cumulus_api
The cumulus_api functions as a commandline interface to all the available cumulus endpoints and functions like the 
api documentation here: https://nasa.github.io/cumulus-api/#cumulus-api

For example, if I would like to list granules and only show the granuleId and collectionId while limiting the results
I can do the following:
```shell
pylot cumulus_api list granules fields="granuleId,collectionId" limit=1
{
  "meta": {
    "count": 360255,
    "limit": 1,
    "name": "cumulus-api",
    "page": 1,
    "stack": "ghrcsit",
    "table": "granule"
  },
  "results": [
    {
      "collectionId": "nalmaraw___1",
      "granuleId": "LA_NALMA_firetower_220706_063000.dat"
    }
  ]
}

```

To update a record specify the record type and provide a json string for the update:
```shell
pylot cumulus_api update granule data='{"collectionId": "nalmaraw___1", "granuleId": "LA_NALMA_firetower_220706_063000.dat", "status": "completed"}'
{
  "message": "Successfully updated granule with Granule Id: LA_NALMA_firetower_220706_063000.dat, Collection Id: nalmaraw___1"
}
```

# Adding Plugins
To add a custom plugin to pylot create a new directory in ```./pylot/plugins``` and create a .py file with 
the same name as this directory. 
An example: `````./pylot/plugins/fake_plugin/fake_plugin.py`````
There are two required methods to have in the fake_plugin.py file: ```main(args, **kwargs)``` and ```return_parser(subparsers)```.  
`````./pylot/cumulus_cli.py````` will attempt to add a subparser for each module encountered in this directory by
passing an action object that will allow you to add an argparser parser via the add_parser() member function.

If your plugin is passed in as a commandline argument, its main method will be what cumulus_cli attempts to call. Exceptions will be 
thrown if either of these functions are not present. There should be no other requirements on plugin package structure.


