import json

import boto3


def simple():
    client = boto3.client('lambda')
    rsp = client.invoke(
        FunctionName='',
        Payload=''
    )

    ret_dict = json.loads(rsp.get('Payload').read().decode('utf-8'))
