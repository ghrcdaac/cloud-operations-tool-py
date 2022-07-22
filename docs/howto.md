# How To

## Basic usage
```
pylot -h
 ____        _     ___ _____
|  _ \ _   _| |   / _ \_   _|
| |_) | | | | |  | | | || |
|  __/| |_| | |__| |_| || |
|_|    \__, |_____\___/ |_|
       |___/

usage: pylot [-h] {get_status,get_cumulus_records}

Python cLoud operations Tool (PyLOT)

positional arguments:
  {get_status,get_cumulus_records}

optional arguments:
  -h, --help            show this help message and exit
```
The positional arguments are the options currently supported by PyLOT. If you want to get help for a positional argument run
```
pylot get_cumulus_records -h
 ____        _     ___ _____
|  _ \ _   _| |   / _ \_   _|
| |_) | | | | |  | | | || |
|  __/| |_| | |__| |_| || |
|_|    \__, |_____\___/ |_|
       |___/

usage: get_cumulus_records [-h] -t, {collections,granules,providers,rules} [-f, FILTER [FILTER ...]]
                           [-s, FIELDS [FIELDS ...]] [-l, LIMIT] [-c, {true,false}]

optional arguments:
  -h, --help            show this help message and exit
  -t, {collections,granules,providers,rules}, --type {collections,granules,providers,rules}
                        Record type (Granule| Granules|Collections)
  -f, FILTER [FILTER ...], --filter FILTER [FILTER ...]
                        Filter the returned data (where x = y)
  -s, FIELDS [FIELDS ...], --select FIELDS [FIELDS ...]
                        Select some fields from the requested data
  -l, LIMIT, --limit LIMIT
                        Limit the requested data (default to 10)
  -c, {true,false}, --count {true,false}
                        Get ONLY the count of the result
```
## Basic usage
Detailed usage will be provided as examples (coming soon)


### Basic usage of get_cumulus_records
If I want to limit the result to 1 to get a granuleId its status and wither it is published 
or not of a collectionID=nalmaraw___1. I should run
```shell
pylot get_cumulus_records -t granules -f collectionId=nalmaraw___1 status=failed -s granuleId files.bucket files.source -l 1
[
    {
        "granuleId": "LE_NALMA_mtsano_220712_071000.dat",
        "files": [
            {
                "bucket": "ghrcdaac-protected",
                "source": "lma/nalma/raw/2207/LE_NALMA_mtsano_220712_071000.dat"
            }
        ]
    }
]
```
### Basic usage of get_status
If I want to get the status of a collection nalmaraw (version 1) (to see how many files are completed, queued...)
```shell
pylot get_status -f name=nalmaraw version=1
╒═════╤══════════╤═══════════╤═════════════╤═══════════╤══════════╤══════════╤═════════╕
│   # │ name     │   version │   completed │   running │   failed │   queued │   total │
╞═════╪══════════╪═══════════╪═════════════╪═══════════╪══════════╪══════════╪═════════╡
│   1 │ nalmaraw │         1 │     1945578 │         0 │    54541 │       87 │ 2000206 │
╘═════╧══════════╧═══════════╧═════════════╧═══════════╧══════════╧══════════╧═════════╛
```


### Basic usage for modifying Cumulus records (collections, providers, granules)
The syntax is identical for each operation. 
```shell
$ pylot update_provider -h
 ____        _     ___ _____ 
|  _ \ _   _| |   / _ \_   _|
| |_) | | | | |  | | | || |  
|  __/| |_| | |__| |_| || |  
|_|    \__, |_____\___/ |_|  
       |___/                 

usage: update_provider [-h] -d, PROVIDER_DATA

optional arguments:
  -h, --help            show this help message and exit
  -d, PROVIDER_DATA, --data PROVIDER_DATA
                        JSON file containing provider definition
```
```create_<record_type>``` or ```update_<record_type>``` only take one argument ```-d/--data``` which is the name of
a json file containing a newly defined record or fields to be modified in an existing record. Collection and
 provider definitions will replace the entire existing definition while updating a granule will only update
updated fields. 

```shell
$ pylot update_granule -d granule.json 
{
    "message": "Successfully updated granule with Granule Id: f16_20220123v7.gz, Collection Id: rssmif16d___7"
}
```




