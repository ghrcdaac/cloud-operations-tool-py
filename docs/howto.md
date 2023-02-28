# How To

## Basic usage
`pylot -h`
```shell
usage: <plugin> -h to access help for each plugin. 

PyLOT command line utility.

optional arguments:
  -h, --help            show this help message and exit

plugins:
  {cumulus_api,opensearch}
    cumulus_api         This plugin provides a commandline interface to the cumulus api endpoints.
    opensearch          This plugin is used to submit queries directly to OpenSearch bypassing the cumulus API.

```
The initial help text will display the top level help text for the PyLOT command line functionality. The positional 
arguments are plugins that can be accessed by passing the name as an argument and -h to access available help text 
for the plugin:  
`pylot cumulus_api -h`
```shell
usage: <action> -h to see help for each action.

Provides commandline access to the cumulus api. To see available arguments check the cumulus documentation here: https://nasa.github.io/cumulus-api/#cumulus-api
If more than 10 records are needed to be returned use the limit keyword argument: limit=XX
Examples: 
 - pylot cumulus_api list collections fields="name,version"
 - pylot cumulus_api list collections fields="name,version" limit=12 name__in="msuttp,msutls"
 - pylot cumulus_api update granule '{"collectionId": "nalmaraw___1", "granuleId": "LA_NALMA_firetower_220706_063000.dat", "status": "completed"}' 
 - pylot cumulus_api update granule update.json

optional arguments:
  -h, --help            show this help message and exit

actions:
  {apply,associate,bulk,create,delete,get,granules,list,move,recover,refresh,reindex,reingest,remove,replay,run,search,serve,update}
    apply               apply action for the cumulus API
    associate           associate action for the cumulus API
    bulk                bulk action for the cumulus API
    create              create action for the cumulus API
    delete              delete action for the cumulus API
    get                 get action for the cumulus API
    granules            granules action for the cumulus API
    list                list action for the cumulus API
    move                move action for the cumulus API
    recover             recover action for the cumulus API
    refresh             refresh action for the cumulus API
    reindex             reindex action for the cumulus API
    reingest            reingest action for the cumulus API
    remove              remove action for the cumulus API
    replay              replay action for the cumulus API
    run                 run action for the cumulus API
    search              search action for the cumulus API
    serve               serve action for the cumulus API
    update              update action for the cumulus API
```
The left-hand column represents any cumulus action. To see the 
targets for an action provider ```-h``` with the action.
When entering the command the action and target are separated by a space:  
`pylot cumulus_api list collections`

### Basic usage of cumulus_api
The cumulus_api functions as a commandline interface to all the available cumulus endpoints and functions like the 
api documentation here: https://nasa.github.io/cumulus-api/#cumulus-api  
Arguments are passed to the request using keywords. Using https://nasa.github.io/cumulus-api/#retrieve-granule
as an example:  
`pylot cumulus_api get granule LA_NALMA_firetower_220706_060000.dat`
```json
{
  "collectionId": "nalmaraw___1",
  "createdAt": 1667249913685,
  "duration": 65.675,
  "error": {
    "Cause": "None",
    "Error": "Unknown Error"
  },
  "execution": "some_execution",
  "files": [
    {
      "bucket": "a-bucket",
      "fileName": "LA_NALMA_firetower_220706_060000.dat",
      "key": "nalmaraw__1/LA_NALMA_firetower_220706_060000.dat",
      "size": 4338858,
      "source": "lma/nalma/raw/short_test/LA_NALMA_firetower_220706_060000.dat",
      "type": ""
    }
  ],
  "granuleId": "LA_NALMA_firetower_220706_060000.dat",
  "processingEndDateTime": "2022-10-31T20:59:27.936Z",
  "processingStartDateTime": "2022-10-31T20:58:30.375Z",
  "productVolume": "4338858",
  "provider": "a_provider",
  "published": false,
  "status": "completed",
  "timeToArchive": 2.794,
  "timeToPreprocess": 0.562,
  "timestamp": 1667249975894,
  "updatedAt": 1667249975894
}
```
The endpoint looks as follows ```/granules/{granuleId}``` and any endpoint that has braced values ```"{someValue}"``` 
will require a positional argument. In the above example `LA_NALMA_firetower_220706_060000.dat` was the granuleId.

Some endpoints allow for query strings to be passed. These can just be added to the command with the same format.
For example, the following is a more complicated command:  
` pylot cumulus_api list granules limit=2 fields="collectionId,granuleId" sort_by=granuleId order=asc`
```json
[
  {
    "collectionId": "globalir___1",
    "granuleId": "20200526_1600.wrld-ir4km-mrest"
  },
  {
    "collectionId": "globalir___1",
    "granuleId": "20200526_1640.wrld-ir4km-mrest"
  }
]
```

If an endpoint requires a data argument it can be provided as a json string: 
```json 
'{"collectionId": "nalmaraw___1", "granuleId": "LA_NALMA_firetower_220706_063000.dat", "status": "completed"}'
```

The following is an example of updating a granule:
```shell
pylot cumulus_api update granule '{"collectionId": "nalmaraw___1", "granuleId": "LA_NALMA_firetower_220706_063000.dat", "status": "completed"}'
```
```json
{
  "message": "Successfully updated granule with Granule Id: LA_NALMA_firetower_220706_063000.dat, Collection Id: nalmaraw___1"
}
```
There are a few exceptions to this format:  
 - apply_workflow_to_granule  
 - move_granule  
 - remove_granule_from_cmr  
 - run_rule

Each of these calls takes keyword arguments for the values expected in the data string.
For example `apply_workflow_to_granule` takes two keyword arguments `granule_id` and `workflow_name`.
```shell
 pylot cumulus_api apply workflow_to_granule granule_id="LA_NALMA_firetower_220706_060000.dat" workflow_name="DiscoverGranules"
```
```json
{
  "action": "applyWorkflow DiscoverGranules",
  "granuleId": "LA_NALMA_firetower_220706_060000.dat",
  "status": "SUCCESS"
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


