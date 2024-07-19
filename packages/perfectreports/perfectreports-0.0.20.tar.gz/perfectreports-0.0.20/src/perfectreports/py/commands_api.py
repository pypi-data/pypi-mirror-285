import pandas
import requests
import os
import json
from functions import *

def get_test_execution_commands(test_id):
    url = "https://" + os.environ["cloudName"] + \
        ".app.perfectomobile.com"
    api_url = url + "/export/api/v3/test-executions/" + test_id + "/commands"
    payload = {}
    headers = {
        'Perfecto-Authorization': os.environ['securityToken'],
        'Content-Type': 'application/json',
        'Perfecto-TenantId': os.environ["cloudName"] + '-perfectomobile-com'
    }

    response = requests.request("GET", api_url, headers=headers, data=payload)
    return response.content

def get_test_steps_info(test_id):
    result = get_test_execution_commands(test_id)
    result = json.loads(result)

    try:
        resultList = result["resources"]
    except TypeError:
        print(result)

    if (len(resultList) > 0):
        df = pandas.DataFrame([flatten_json(x) for x in resultList])
        # last screenshot API URL
        df.loc[:, df.columns.str.endswith(
            "screenshots/0")].iloc[-1:, -1:].values[0][0]
        steps = "\n".join(df['name'].to_list())
        return steps


def get_devices_list():
    os.environ["cloudName"]= 'mas'
    os.environ["securityToken"] = os.environ["MAS_TOKEN"]
    url = "https://" +  os.environ["cloudName"]  + \
        ".app.perfectomobile.com/api/v1/device-management/devices"
    payload = json.dumps({
        "device": {}
    })
    headers = {
        'Perfecto-Authorization': os.environ['securityToken'],
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    try:
        response = json.loads(response.text)
        resultList = response["handsets"]['handset']
    except TypeError:
        print(response)

    if (len(resultList) > 0):
        df = pandas.DataFrame([flatten_json(x) for x in resultList])
        # df = df[['model', 'available', 'osVersion', 'deviceId', 'manufacturer', 'resolution']]
        # print(df)
        # return df
    return json.loads(json.dumps(response))

# print(get_test_steps_info(test_id))
