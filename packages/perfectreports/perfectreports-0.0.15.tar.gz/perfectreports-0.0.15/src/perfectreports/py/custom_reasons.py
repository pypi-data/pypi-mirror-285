import requests
import json
import pandas
import os


def get_meta_data():
    url = "https://"+os.environ["cloudName"] + \
        ".app.perfectomobile.com/test-execution-management-webapp/rest/v1/metadata"

    payload = {}
    headers = {
        'Perfecto-Authorization': os.environ['securityToken'],
        'perfecto-tenantid': os.environ["cloudName"] + '-perfectomobile-com'
    }
    response = requests.request("GET", url, headers=headers, data=payload, timeout=30)
    result = json.loads(response.content)
    return result


def get_failure_reason_name_category(result):
    try:
        resultList = result["failureReasons"]
    except TypeError:
        print(result)
    if (len(resultList) > 0):
        return pandas.DataFrame(resultList, columns=['name', 'category'])
    else:
        return pandas.DataFrame()


async def get_failure_reason_category_table(df, total):
    # get category df
    result = get_meta_data()
    category_df = get_failure_reason_name_category(result)
    category_df.rename(
        columns={'name': 'Custom Failure Reasons', 'category': 'Category'}, inplace=True)
    df = category_df.merge(df, how="inner", on="Custom Failure Reasons").pivot_table(
        index=['Status', 'Category', 'Custom Failure Reasons'], aggfunc='size')
    df = pandas.DataFrame(df).sort_values(by=0, ascending=False).sort_values(
        by="Status", ascending=False).head(10).rename(columns={0: "Total"})
    df['✓%↑'] = round(df["Total"].div(
        total).mul(100).astype(float), 1).astype(str) + '%'
    failurecategorytable = {}


    failurecategorytable = df.to_html(
        table_id="category",
        index=True,
        render_links=True,
        escape=False,
    )
    return failurecategorytable
