import base64
import json
import sys
import numpy as np
import matplotlib.pyplot as plt
import datetime
import io
import base64
import os
from time import time
import pandas
import requests
import plotly.graph_objects as go
from base64 import b64encode


def hyperlink(df, url, from_col, to_col, first_df, first_item=False):
    videoURLS = []
    for ind in df.index:
        if first_item:
            videoURLS.append(
                first_df.loc[first_df[to_col] ==
                             df[to_col][ind], from_col].iloc[0]
            )
        else:
            videoURLS.append(df[from_col][ind])
    df[url] = videoURLS
    df[url] = df[url].apply(
        lambda x: "{0}".format(x)
    )
    for ind in df.index:
        df.loc[df[to_col].index == ind, to_col] = (
            '<a target="_blank" href="'
            + df[url][ind]
            + '">'
            + df[to_col][ind]
            + "</a>"
        )
    df = df.drop(url, axis=1)
    return df


async def topFailedTC(total, failed_df):
    failed_df = failed_df[~failed_df['name'].str.contains(
        "Interactive session")]
    # top failed TCs
    topfailedTCNames = (
        failed_df.groupby(["name"])
        .size()
        .reset_index(name="#Failed")
        .sort_values("#Failed", ascending=False)
        .head(10)
    )
    topfailedTCNames['%'] = round(topfailedTCNames["#Failed"].div(
        total).mul(100).astype(float), 1).astype(str) + '%'
    topfailedTCNames = hyperlink(
        topfailedTCNames, "Result", "reportURL", "name", failed_df, first_item=True)
    topfailedTCNames.columns = ["Failed Tests", "Total", "✓%↑"]
    topfailedtable = {}
    topfailedtable = topfailedTCNames.to_html(
        table_id="topfailedtests",
        index=False,
        render_links=True,
        escape=False,
    )
    return topfailedtable


async def topFailedReasons(total, failed_df):
    # top failed reasons
    topfailedTCNames = (
        failed_df.groupby(["Failure Message"])
        .size()
        .reset_index(name="#Failed")
        .sort_values("#Failed", ascending=False)
        .head(10)
    )
    topfailedTCNames['%'] = round(topfailedTCNames["#Failed"].div(
        total).mul(100).astype(float), 1).astype(str) + '%'
    topfailedTCNames = hyperlink(
        topfailedTCNames, "Result", "reportURL", "Failure Message", failed_df, first_item=True)
    topfailedTCNames.columns = ["Failure Messages", "Total", "✓%↑"]
    topfailedtable = {}
    topfailedtable = topfailedTCNames.to_html(
        table_id="topfailedmessages",
        index=False,
        render_links=True,
        escape=False,
    )
    return topfailedtable


def get_report_details(item, temp, name, criteria):
    if name + "=" in item:
        temp = str(item).split("=", 1)[1]
    return str(temp), criteria


def get_key_details(item, temp, name):
    if name + "=" in item:
        temp = str(item).split("=", 1)[1]
    return str(temp)


def fig_to_base64(fig):
    img = io.BytesIO()
    fig.savefig(img, format='png',
                bbox_inches='tight')
    img.seek(0)

    return base64.b64encode(img.getvalue())


async def create_summary_pie(df, title, column, value_column):
    status_df = df[column].value_counts().sort_index().reindex(
        ["BLOCKED", "FAILED", "PASSED", "UNKNOWN"], fill_value=0).rename_axis(column).to_frame()
    layout = go.Layout(
        autosize=True,
        showlegend=False,
        title_text=title,
        title_x=0.5,
        title_y=0.97,
    )
    PASSED = '#33d633fa'
    FAILED = '#ff5f41d6'
    BLOCKED = '#ffa50091'
    UNKNOWN = '#F2EBEF'
    colors = [BLOCKED, FAILED, PASSED, UNKNOWN]
    fig = go.Figure(data=[go.Pie(labels=status_df.index.tolist(),
                    values=status_df[value_column].values.tolist(), pull=[0, 0.05, 0.1, 0],
                    hole=.3, texttemplate="%{label}: %{value} <br>(%{percent})", insidetextorientation='horizontal', sort=True)], layout=layout)
    fig.update_traces(marker=dict(
        colors=colors, line=dict(color='white', width=3)))
    fig.update_layout(font=dict(family="sans-serif",
                      size=22, color="black"))
    img = fig.to_image(format="png", engine="kaleido")

    summary = '<img alt="execution summary" id="box" style="height: 200px;width: 240px !important;" src="data:image/png;base64, {}"'.format(
        b64encode(img).decode("utf-8"))
    return summary


def create_pie(df, title, column, value_column, style="height: 240px;width: 300px;"):
    status_df = df[column].value_counts(
    ).sort_index().rename_axis(column).to_frame()
    layout = go.Layout(
        autosize=True,
        showlegend=False,
        title_text=title,
        title_x=0.5,
        title_y=0.97,
    )
    fig = go.Figure(data=[go.Pie(labels=status_df.index.tolist(),
                    values=status_df[value_column].values.tolist(), pull=[0.1, 0.05, 0.02, 0],
                    hole=.3, texttemplate="%{label}: %{value} <br>(%{percent})", insidetextorientation='horizontal', sort=True)], layout=layout)
    fig.update_traces(marker=dict(line=dict(color='white', width=3)))
    fig.update_layout(font=dict(family="sans-serif",
                      size=22, color="black"))
    img = fig.to_image(format="png", engine="kaleido")

    summary = '<img alt="execution summary" id="box" style="'+style+'" src="data:image/png;base64, {}" >'.format(
        b64encode(img).decode("utf-8"))
    return summary


def create_top_pie(df, title, column, value_column, top, style="height: 240px;width: 300px;"):
    status_df = df[column].value_counts().reset_index(
        name=value_column).sort_values(value_column, ascending=False).head(top)
    layout = go.Layout(
        autosize=True,
        showlegend=False,
        title_text=title,
        title_x=0.5,
        title_y=0.97,
    )
    labels = []
    if column not in status_df.columns:
        labels = status_df['index'].tolist()
    else:
        labels = status_df[column].tolist()
    fig = go.Figure(data=[go.Pie(labels=labels,
                    values=status_df[value_column].values.tolist(), pull=[0.1, 0.05, 0.02, 0],
                    hole=.3, texttemplate="%{label}: %{value} <br>(%{percent})", insidetextorientation='horizontal', sort=True)], layout=layout)
    fig.update_traces(marker=dict(line=dict(color='white', width=3)))
    fig.update_layout(font=dict(family="sans-serif",
                      size=22, color="black"))
    img = fig.to_image(format="png", engine="kaleido")

    summary = '<img alt="execution summary" id="box" style="'+style+'" src="data:image/png;base64, {}" >'.format(
        b64encode(img).decode("utf-8"))
    return summary


"""
    Dictionary
"""


class my_dictionary(dict):
    def __init__(self):
        self = dict()

    def add(self, key, value):
        self[key] = value


"""
    flattens the json
"""


def flatten_json(nested_json, exclude=[""]):
    """Flatten json object with nested keys into a single level.
        Args:
            nested_json: A nested json object.
            exclude: Keys to exclude from output.
        Returns:
            The flattened json object if successful, None otherwise.
    """
    out = {}

    def flatten(x, name="", exclude=exclude):
        if type(x) is dict:
            for a in x:
                if a not in exclude:
                    flatten(x[a], name + a + "/")
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + "/")
                i += 1
        else:
            out[name[:-1]] = x
    flatten(nested_json)
    return out


def df_formatter(df, jobName, jobNumber):
    if len(df) < 1:
        raise Exception("Unable to find any matching executions!")
    try:
        df["startTime"] = pandas.to_datetime(df["startTime"], unit="ms")
        df["startTime"] = (
            df["startTime"].dt.tz_localize(
                "utc").dt.tz_convert(None)
        )
        df["startTime"] = df["startTime"].dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        pass
    try:
        df.loc[df["endTime"] < 1, "endTime"] = int(round(time() * 1000))
        df["endTime"] = pandas.to_datetime(df["endTime"], unit="ms")
        df["endTime"] = (
            df["endTime"].dt.tz_localize(
                "utc").dt.tz_convert(None)
        )
        df["endTime"] = df["endTime"].dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        pass
    if "month" not in df.columns:
        df["month"] = pandas.to_datetime(
            df["startTime"], format="%Y-%m-%d %H:%M:%S"
        ).dt.to_period("M")
    if "startDate" not in df.columns:
        df["startDate"] = pandas.to_datetime(
            pandas.to_datetime(df["startTime"], format="%Y-%m-%d %H:%M:%S")
            .dt.to_period("D")
            .astype(str)
        )
    if "week" not in df.columns:
        df["week"] = pandas.to_datetime(df["startDate"].dt.strftime("%Y/%m/%d")) - df[
            "startDate"
        ].dt.weekday.astype("timedelta64[D]")
    if "Duration" not in df.columns:
        df["Duration"] = pandas.to_datetime(
            df["endTime"], format='mixed') - pandas.to_datetime(df["startTime"], format='mixed')
        df["Duration"] = df["Duration"].dt.seconds
        df["Duration"] = pandas.to_datetime(df["Duration"], unit="s").dt.strftime(
            "%H:%M:%S"
        )
    if "failureReasonName" not in df.columns:
        df["failureReasonName"] = ""
    # Filter only job and job number if dates are parameterized as well but show full histogram
    if jobNumber != "" and jobName != "":
        if ";" in jobNumber:
            df = df[df["job/number"].isin(jobNumber.split(";"))]
        else:
            df = df[df["job/number"].astype(str) == jobNumber]
    return df


def payloadJobAll(reportTags, oldmilliSecs, current_time_millis, jobName, jobNumber, page, internal, boolean):
    payload = my_dictionary()
    if oldmilliSecs != 0:
        payload.add("startExecutionTime[0]", oldmilliSecs)
    if reportTags != "":
        for i, reportTaging in enumerate(reportTags.split(";")):
            if internal == "false":
                payload.add("tags[" + str(i) + "]", reportTaging)
            else:
                payload.add("tags", reportTaging)
    if current_time_millis != 0:
        payload.add("endExecutionTime[0]", current_time_millis)
    if internal == "false":
        payload.add("_page", page)
    if jobName != "":
        if jobName != "All Jobs":
            if jobName != "Perfecto Integrations":
                for i, job in enumerate(jobName.split(";")):
                    if internal == "false":
                        payload.add("jobName[" + str(i) + "]", job)
                    else:
                        payload.add("jobName", job)
    if jobNumber != "" and boolean:
        for i, jobNumber in enumerate(jobNumber.split(";")):
            if internal == "false":
                payload.add("jobNumber[" + str(i) + "]", jobNumber)
            else:
                payload.add("jobNumber", int(jobNumber))
    print(str(payload))
    return payload

def pastDateToMS(startDate, daysOlder):
    dt_obj = datetime.datetime.strptime(
        startDate + " 00:00:00,00", "%Y-%m-%d %H:%M:%S,%f"
    ) - datetime.timedelta(days=daysOlder)
    millisec = dt_obj.timestamp() * 1000
    oldmilliSecs = round(int(millisec))
    return oldmilliSecs


def retrieve_tests_executions(daysOlder, jobName, jobNumber, page, startDate, endDate, reportTag, skip, pageSize, internal):
    current_time_millis = 0
    oldmilliSecs = 0
    if endDate != "":
        if "-" not in endDate:
            current_time_millis = endDate
        else:
            endTime = datetime.datetime.strptime(
                str(endDate) + " 23:59:59,999", "%Y-%m-%d %H:%M:%S,%f"
            )
            millisec = endTime.timestamp() * 1000
            current_time_millis = round(int(millisec))
    if startDate != "":
        if "-" not in startDate:
            oldmilliSecs = startDate
        else:
            oldmilliSecs = pastDateToMS(startDate, daysOlder)
    if jobNumber != "" and jobName != "" and startDate != "" and endDate != "":
        fields = payloadJobAll(
            reportTag, oldmilliSecs, current_time_millis, jobName, jobNumber, page, internal, False
        )
    else:
        fields = payloadJobAll(
            reportTag, oldmilliSecs, current_time_millis, jobName, jobNumber, page, internal, True
        )

    if internal == "true":
        payload = {
            "filter": {
                "fieldNameToSearchFilter": {},
                "fields": fields,
                "excludedFields": {}
            },
            "layout": [
                "job",
                "id",
                "reportUrl",
                "version",
                "name",
                "status",
                "startTime",
                "failureReason",
                "endTime",
                "platforms",
                "tags",
                "failureReason",
                "automationFramework",
                "cleanException",
                "message",
                "errorAnalysis"
            ],
            "skip": skip,
            "pageSize": pageSize
        }
        url = "https://" + os.environ["cloudName"] + \
            ".app.perfectomobile.com"
        api_url = url + "/test-execution-management-webapp/rest/v1/test-execution-management/search"

        # creates http get request with the url, given parameters (payload) and header (for authentication)
        r = requests.request("POST",
                             api_url, data=json.dumps(payload), headers={
                                 "PERFECTO_AUTHORIZATION": os.environ["securityToken"],
                                 "content-type": "application/json",
                                 "perfecto-tenantId": os.environ["cloudName"] + "-perfectomobile-com"})
    else:
        url = "https://" + os.environ["cloudName"] + \
            ".reporting.perfectomobile.com"
        api_url = url + "/export/api/v1/test-executions"

        # creates http get request with the url, given parameters (payload) and header (for authentication)
        r = requests.get(
            api_url, params=fields, headers={
                "PERFECTO_AUTHORIZATION": os.environ["securityToken"],
                "Content-Type": "application/json",
                "Perfecto-TenantId": os.environ["cloudName"] + "-perfectomobile-com"}
        )
    print(str(r.url))  # debug
    return r.content

def prepare_device_coverage(df):
    if 'model' not in df.columns:
        df['model'] = np.NaN
    if 'browserType' not in df.columns:
        df['browserType'] = np.NaN
    if 'browserVersion' not in df.columns:
        df['browserVersion'] = np.NaN
        # append version to device/browser version columns and combine them
    df.loc[df['browserType'].notna(), 'browserType'] = df.loc[df['browserType'].notna(
    ), 'browserType'].astype(str)+'-v'
    df['browser'] = df["browserType"] + df["browserVersion"].astype(str)
    df.loc[df['model'].notna(), 'model'] = df.loc[df['model'].notna(),
                                                  'model'].astype(str)+'-v'
    df['mobile'] = df['model'].astype(
        str).replace("-v", '') + df['Version'].astype(str)
    df['osCoverage'] = df[['browser', 'mobile']
                          ].stack().groupby(level=0).agg(''.join)
    df['osCoverage'] = df['osCoverage'].str.replace(
        r'nan.*', '', regex=True).astype('str')
    df = df.drop(df[df['osCoverage'] == 'nan'].index)
    if (len(df['osCoverage'].value_counts()) > 0):
        version_items = create_top_pie(
            df, "", "osCoverage", "Total", 5, "height: 200px;width: 290px;")
        version_items = '<div id="box"><div id="heading">Top 5 Browsers / Devices</div><div>' + \
            version_items + ' </div></div>'
    else:
        version_items = ""
    return df, version_items


def get_resources(truncated, reportTag, page, daysOlder, resources, jobName, jobNumber, startDate, endDate, internal):
    skip, pageSize = 0, 200
    # executionList = {'executionList': '1'} # workaround for turncated issue
    # while len(executionList) > 0: # workaround for turncated issue
    while truncated == True:
        executions = retrieve_tests_executions(
            daysOlder, jobName, jobNumber, page, startDate, endDate, reportTag, skip, pageSize, internal)
        # Loads JSON string into JSON object
        executions = json.loads(executions)
        if "{'userMessage': 'Failed decoding the offline token:" in str(executions):
            raise Exception(
                "please change the offline token for your cloud")
        if "userMessage': 'Missing Perfecto-TenantId header" in str(executions):
            raise Exception("Check the cloud name and security tokens")
        if "userMessage': 'Time period is not in supported range" in str(executions):
            raise Exception(
                "Time period is not in supported range. Check your startDate parameter")
        try:
            if internal == "true":
                executionList = executions["items"]
            else:
                executionList = executions["resources"]
        except TypeError:
            print(executions)
            raise Exception(
                "Unable to find matching records for: "
                + str(sys.argv[2], sys.argv[3])
                + ", error:"
                + str(executions["userMessage"])
            )
            sys.exit(-1)
        if len(executionList) == 0:
            return resources
        else:
            if internal == "true":
                resources.extend(executionList)
                skip += pageSize
            else:
                metadata = executions["metadata"]
                truncated = metadata["truncated"]
                if page >= 1:
                    resources.extend(executionList)
                else:
                    resources.append(executionList)
            print('page: ' + str(page) + ', page count: ' +str(len(executionList)))
            page += 1
    return resources

async def prepare_custom_failure_graph(failed_df):
    if (len(failed_df) > 0):
        return create_top_pie(
            failed_df, "", "Custom Failure Reasons", "count", 5, "height: 200px;width: 300px;")
    else:
        return ""


async def prepare_module_graph(df):
    # https://towardsdatascience.com/100-stacked-charts-in-python-6ca3e1962d2b
    df = df[~df['Module'].isin(['-'])]
    cross_tab = pandas.crosstab(index=df['Module'],
                                columns=df['Status'])
    cross_tab_prop = pandas.crosstab(index=df['Module'],
                                     columns=df['Status'],
                                     normalize="index")
    ax = cross_tab_prop.sort_values('Module', ascending=False).plot(kind='barh',
                                                                    stacked=True,
                                                                    color={'PASSED': '#33d633fa',
                                                                           'FAILED': '#ff5f41b5',
                                                                           'BLOCKED': '#ffa50091',
                                                                           'UNKNOWN': '#F2EBEF'},
                                                                    )  # figure size figsize=(4, 2.5)
    ax.spines['bottom'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.axes.get_xaxis().set_visible(False)
    ax.xaxis.set_tick_params(labelsize=10)
    ax.yaxis.set_tick_params(
        labelsize=9, labelcolor="black", direction='out', which='major')
    ax.get_legend().remove()
    # plt.rcParams["font.weight"] = "bold"
    plt.xlabel("")
    plt.ylabel("")
    plt.tight_layout()
    F = plt.gcf()
    Size = F.get_size_inches()
    F.set_size_inches(Size[0]*.95, Size[1]*.7, forward=True)
    for n, x in enumerate([*cross_tab.sort_values('Module', ascending=False).index.values]):
        for (proportion, count, y_loc) in zip(cross_tab_prop.loc[x],
                                              cross_tab.loc[x],
                                              cross_tab_prop.loc[x].cumsum()):
            # time.sleep(.7)
            plt.text(x=(y_loc - proportion) + (proportion / 2),
                     y=n - 0.11,
                     s=f'{count}\n({np.round(proportion * 100, 1)}%)',
                     color="#36220e",
                     fontsize=9)
    fig = 'tags.png'
    plt.savefig(fig, bbox_inches='tight')
    with open(fig, "rb") as fig:
        encoded = base64.b64encode(fig.read())
        tags_base64 = '<img src="data:image/png;base64, {}">'.format(
            encoded.decode('utf-8'))

    return tags_base64


async def prepare_tags_table(total, failed_df):
    tags_df = failed_df.pivot_table(
        index=['Owner', 'Module', 'Failed Steps'], aggfunc='size')
    tags_df = pandas.DataFrame(tags_df)
    tags_df = tags_df.sort_values([0]).tail(10)
    tags_df = tags_df.rename(
        columns={
            0: "Count",
        })
    tags_df.sort_values(['Count'],
                        ascending=[False], inplace=True)
    tags_df['%'] = round(tags_df["Count"].div(
        total).mul(100).astype(float), 1).astype(str) + '%'
    tags_df_table = tags_df.to_html(
        table_id="tags",
        render_links=True,
        escape=False,
    )

    return tags_df_table


async def prepare_failed_table(failed_df, internal):
    failed_df["Video"] = '<img id="vidlink"/>'
    if internal == "false":
        failed_df = hyperlink(failed_df, "vidResult",
                              "videos/0/downloadUrl", "Video", "", False)
        failed_df = failed_df[["Owner", "Module", "name", "Custom Failure Reasons",
                               "Failure Message", "Failed Steps", "Video"]]
    else:
        failed_df = failed_df[["Owner", "Module", "name", "Custom Failure Reasons",
                               "Failure Message", "Failed Steps"]]
    failed_df = failed_df.rename(
        columns={
            "name": "Failed Test"
        }
    )
    failedTable = failed_df.to_html(
        table_id="table",
        index=False,
        render_links=False,
        escape=False,
    )

    return failedTable


def format_df(df, jobName, jobNumber, automation_owners, internal):
    df = df_formatter(df, jobName, jobNumber)
    df["platforms/0/deviceType"] = df["platforms/0/deviceType"].fillna(
        "Others")
    df["platforms/0/os"] = df["platforms/0/os"].fillna("Others")
    if "failureReasonName" not in df.columns:
        df["failureReasonName"] = ""
    if internal == "true":
        df = df.rename(
            columns={"failureReason/name": "Custom Failure Reasons"})
    else:
        df = df.rename(
            columns={"failureReasonName": "Custom Failure Reasons"})
    df = df.rename(
        columns={
            "platforms/0/deviceType": "Platform",
            "platforms/0/os": "OS",
            "status": "Status",
            "errorAnalysis/cleanException": "cleanException",
            "platforms/0/osVersion": "Version",
            "tags/0": "Module",
            "platforms/0/browserInfo/browserVersion": "browserVersion",
            "platforms/0/browserInfo/browserType": "browserType",
            "platforms/0/mobileInfo/model": "model"
        }
    )
    del_cols = ["externalId", 'platforms/0/mobileInfo/imei',
                'platforms/0/mobileInfo/distributor', 'platforms/0/mobileInfo/firmware', 'triggerType',
                'failureReason/id', 'failureReason/isSystemAssigned', 'errorAnalysis/normalizedCleanException']
    df.drop(del_cols, axis=1, errors='ignore', inplace=True)
    df.reset_index(drop=True, inplace=True)
    # update owners
    if 'Module' not in df.columns:
        df['Module'] = '-'
    df["Owner"] = "-"
    df['Module'] = df['Module'].fillna("-")
    try:
        data = json.loads(str(automation_owners))
        for i in data:
            for j in data[i]:
                df.loc[df['Module'] == j, "Owner"] = i
    except Exception as e:
        pass

    # sort properly
    df.sort_values(['Owner', 'Module', 'name'],
                   ascending=[True, True, True], inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


def generateExcel(df):
    df.to_csv("output.csv", index=False)


def get_os_versions_list(devices):
    osVersions = []
    for device in devices['handsets']['handset']:
        osVersions.append(str(device['osVersion']))
    return list(set(osVersions))


def find_nearest_decimal(decimal, array_list):
    whole_number = int(decimal)
    nearest_decimal = None
    min_difference = float('inf')

    for number in array_list:
        integer_part = int(float(number))
        difference = abs(float(integer_part) - float(whole_number))
        if difference < min_difference:
            min_difference = difference
            nearest_decimal = number
    return nearest_decimal


def get_os_version_major(osVersions):
    return ['.'.join(version.split(".")[:2]) for version in osVersions]
