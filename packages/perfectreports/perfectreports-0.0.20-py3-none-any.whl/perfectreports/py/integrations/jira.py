from datetime import datetime
import requests
from requests.auth import HTTPBasicAuth
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json


def create_jira_session():
    # Headers
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    # Setup retry strategy
    retry_strategy = Retry(
        total=5,  # Total number of retries
        # Retry on these HTTP status codes
        status_forcelist=[429, 500, 502, 503, 504],
        # Retry for these HTTP methods
        allowed_methods=["HEAD", "GET", "OPTIONS"],
        backoff_factor=1  # Exponential backoff factor
    )

    # Setup the adapter with the retry strategy
    adapter = HTTPAdapter(max_retries=retry_strategy)

    # Create a session and mount the adapter
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return headers, session


def get_jira_issues(JIRA_BASE_URL, JIRA_API_TOKEN, JIRA_USERNAME, JIRA_JQL_QUERY):
    headers, session = create_jira_session()
    URL = f'{JIRA_BASE_URL}/rest/api/2/search'
    print(URL)
    # Parameters
    max_results = 100
    start_at = 0
    total_issues = []
    is_last = False
    while not is_last:
        params = {
            'jql': JIRA_JQL_QUERY,
            'maxResults': max_results,
            'startAt': start_at
        }

    # Perform the request with retries and a timeout of 2 minutes
        try:
            response = session.get(
                URL,
                headers=headers,
                params=params,
                auth=HTTPBasicAuth(JIRA_USERNAME, JIRA_API_TOKEN),
                timeout=(120, 120)  # Connection timeout, Read timeout
            )

            # Check for successful response
            if response.status_code == 200:
                data = response.json()
                issues = data.get('issues', [])
                total_issues.extend(issues)
                start_at += max_results
                is_last = start_at >= data.get('total', 0)
            else:
                print("Failed to query JIRA URL: " + URL + ", " +
                      str(response.status_code) + " : " + str(response.text))
                break
        except requests.exceptions.RequestException as e:
            print("Request failed: " + str(e))
            break
    return total_issues


def create_jira_bug(JIRA_BASE_URL, JIRA_API_TOKEN, JIRA_USERNAME, PROJECT_KEY, LABELS, ASSIGNEE, SUMMARY, DESCRIPTION):
    issue_key = ''
    headers, session = create_jira_session()
    URL = f'{JIRA_BASE_URL}/rest/api/2/issue'
    # Issue data
    issue_data = {
        "fields": {
            "project": {
                "key": PROJECT_KEY
            },
            "summary": SUMMARY,
            "description": DESCRIPTION,
            "issuetype": {
                "name": "Bug"
            },
            "assignee": {
                "accountId": ASSIGNEE
            },
            "priority": {
                "name": "Medium"
            },
            "labels": LABELS
        }
    }
    try:
        response = session.post(
            URL,
            headers=headers,
            data=json.dumps(issue_data),
            auth=HTTPBasicAuth(JIRA_USERNAME, JIRA_API_TOKEN),
            timeout=(120, 120)  # Connection timeout, Read timeout
        )

        # Check for successful response
        if response.status_code == 201:
            issue_key = response.json().get('key')
            print("Successfully created issue: " + issue_key)
        else:
            print("Failed to create JIRA bug. URL: " + URL + ", " +
                  str(response.status_code) + " : " + str(response.text))

    except requests.exceptions.RequestException as e:
        print("Request failed: " + str(e))
    return issue_key


def update_bug_links(JIRA_BASE_URL, JIRA_API_TOKEN, JIRA_USERNAME, RELATE_TYPE, BUG_KEY, TEST_KEYS):
    headers, session = create_jira_session()
    URL = f'{JIRA_BASE_URL}/rest/api/2/issueLink'
    for TEST_KEY in TEST_KEYS:
        link_data = {
            "type": {
                "name": RELATE_TYPE
            },
            "inwardIssue": {
                "key": TEST_KEY
            },
            "outwardIssue": {
                "key": BUG_KEY
            }
        }

        try:
            response = session.post(
                URL,
                headers=headers,
                data=json.dumps(link_data),
                auth=HTTPBasicAuth(JIRA_USERNAME, JIRA_API_TOKEN),
                timeout=(120, 120)  # Connection timeout, Read timeout
            )

            if response.status_code == 201:
                print("Successfully linked bug: " +
                      BUG_KEY + " to test " + TEST_KEY)
            else:
                print("Failed to update JIRA bug. URL: " + URL + ", " +
                      str(response.status_code) + " : " + str(response.text))
        except requests.exceptions.RequestException as e:
            print("Request failed: " + str(e))


def delete_jira_bug(JIRA_BASE_URL, JIRA_API_TOKEN, JIRA_USERNAME, ISSUE_KEY):
    headers, session = create_jira_session()
    URL = f'{JIRA_BASE_URL}/rest/api/2/issue/{ISSUE_KEY}'

    try:
        response = session.delete(
            URL,
            headers=headers,
            auth=HTTPBasicAuth(JIRA_USERNAME, JIRA_API_TOKEN),
            timeout=(120, 120)  # Connection timeout, Read timeout
        )

        # Check for successful response
        if response.status_code == 204:
            print("Successfully deleted issue: " + ISSUE_KEY)
        else:
            print("Failed to delete JIRA bug. URL: " + URL + ", " +
                  str(response.status_code) + " : " + str(response.text))
    except requests.exceptions.RequestException as e:
        print("Request failed: " + str(e))


def get_jira_labels(JIRA_BASE_URL, JIRA_API_TOKEN, JIRA_USERNAME, ISSUE_KEY):
    labels = []
    headers, session = create_jira_session()
    URL = f'{JIRA_BASE_URL}/rest/api/2/issue/{ISSUE_KEY}'

    try:
        response = session.get(
            URL,
            headers=headers,
            auth=HTTPBasicAuth(JIRA_USERNAME, JIRA_API_TOKEN),
            timeout=(120, 120)  # Connection timeout, Read timeout
        )

        # Check for successful response
        if response.status_code == 200:
            issue_data = response.json()
            labels = issue_data.get('fields', {}).get('labels', [])
            print("Labels for issue " + str(ISSUE_KEY) + ": " + ", ".join(labels))
        else:
            print("Failed to retrieve issue. URL: " + URL + ", " +
                  str(response.status_code) + " : " + str(response.text))
    except requests.exceptions.RequestException as e:
        print("Request failed: " + str(e))
    return labels


def jira_bug(row, JIRA_BASE_URL, JIRA_API_TOKEN, JIRA_USERNAME, PROJECT_KEY, EXEC_KEY, RELATE_TYPE, XRAY_TEST_TYPE, ASSIGNEE, DEFAULT_STATUS, BUG_LABEL):
    SUMMARIES = row['name']
    if (JIRA_BASE_URL != ""):
        if (JIRA_API_TOKEN != ""):
            if (PROJECT_KEY != ""):
                if (EXEC_KEY != ""):
                    LABELS = [BUG_LABEL, "automation", "perfecto"]
                    SUMMARY = EXEC_KEY + ":" + row['message']
                    JQL_BUG_SUMMARY = "project = '" + PROJECT_KEY + \
                        "' AND type = Bug AND status != '" + DEFAULT_STATUS + "' AND labels = '" + \
                        BUG_LABEL + "' AND summary ~ '" + \
                        escapeSpecialChars(SUMMARY) + "'"
                    return raise_bug(JIRA_BASE_URL, JIRA_API_TOKEN, JIRA_USERNAME, PROJECT_KEY, EXEC_KEY, RELATE_TYPE,
                                     ASSIGNEE, LABELS, SUMMARY, XRAY_TEST_TYPE, SUMMARIES, JQL_BUG_SUMMARY)
                else:
                    return 'No Execution key found'
            else:
                return 'No Project key found'
        else:
            return 'No JIRA Token!'
    else:
        return 'No JIRA URL!'


def escapeSpecialChars(summary):
    return summary.replace(' -', r' \\-').replace("'", r"''").replace('"', r'\\"').replace('@', r'\\@').replace('[', r'\\[').replace(']', r'\\]').replace('*', r'\\*')


def create_jira_link(jira_key, JIRA_BASE_URL):
    return f'<a href="{JIRA_BASE_URL}/browse/{jira_key}">{jira_key}</a>'


def get_test_keys(JIRA_BASE_URL, JIRA_API_TOKEN, JIRA_USERNAME, PROJECT_KEY, XRAY_TEST_TYPE, SUMMARIES):
    TEST_KEYS = []
    for SUMMARY in SUMMARIES:
        # escape sp chars to avoid jql issues
        SUMMARY = escapeSpecialChars(SUMMARY)
        JQL_JUST_SUMMARY = "project = '" + PROJECT_KEY + \
            "' AND type = '" + XRAY_TEST_TYPE + "' AND summary ~ '" + SUMMARY + "'"
        total_issues = get_jira_issues(
            JIRA_BASE_URL, JIRA_API_TOKEN, JIRA_USERNAME, JQL_JUST_SUMMARY)
        # list xray test
        print("Found " + str(len(total_issues)) +
              " issue with summary: " + SUMMARY)
        if (len(total_issues)) > 0:
            for issue in total_issues:
                TEST_KEY = issue.get("key", "")
                if (TEST_KEY != ""):
                    TEST_KEYS.append(TEST_KEY)
    return TEST_KEYS


def getTestExecutionsList():
    # TODO: create xray header
    url = "https://xray.cloud.getxray.app/api/v2/graphql"
    start = 0
    limit = 1
    total = 0
    test_list = []
    test_list_str = ""
    EXEC_KEY = "XS-41"
    while True:
        payload = json.dumps({
            "query": "{step1: getTestExecutions(jql:\"key=" + EXEC_KEY + "\", limit: 1) {    total    start    limit    results {      issueId      jira(fields: [\"key\"])      projectId      tests(start: " + str(start) + ", limit: " + str(limit) + ") {        total        start        limit        results { issueId         jira(fields: [\"key\"]) testType{ name }        }      }    }  }}",
            "variables": {}
        })
        headers = {

            'Authorization': 'Bearer <TOKEN>',
            'Content-Type': 'application/json'
        }
        try:
            response = requests.request(
                "POST", url, headers=headers, data=payload)
            if (response.status_code == 200):
                mapper = response.json()
                step = mapper.get("data", {}).get("step1", {})
                tests = step.get("results", [{}])[0].get("tests", {})
                results = tests.get("results", [])

                for execution in results:
                    test_type = execution.get("testType", {}).get("name")
                    if test_type:
                        if test_type.lower() == "cucumber":
                            key = execution.get("jira", {}).get("key", "")
                            if key:
                                test_list.append(key)

                # Convert test_list to a comma-separated string
                test_list_str = ",".join(test_list)

                # Get total and increment start by limit (assuming limit is defined somewhere)
                total = tests.get("total", 0)
                # Increment start for the next iteration
                start += limit
                print("Total:", total)
                print("Start:", start)
                # Check if start is less than total for the next iteration
                if start == total:
                    break
            else:
                print("Xray Get Executions Error:", response.reason)
        except Exception as e:
            print(e)
    return test_list_str


def raise_bug(JIRA_BASE_URL, JIRA_API_TOKEN, JIRA_USERNAME, PROJECT_KEY, EXEC_KEY, RELATE_TYPE, ASSIGNEE, LABELS, SUMMARY, XRAY_TEST_TYPE, SUMMARIES, JQL_BUG_SUMMARY):
    # get test keys
    TEST_KEYS = get_test_keys(JIRA_BASE_URL, JIRA_API_TOKEN,
                              JIRA_USERNAME, PROJECT_KEY, XRAY_TEST_TYPE, SUMMARIES)

    if (len(TEST_KEYS) > 0):
        # Checks for existing issues with different statuses except To Do and don't create a bug if exists.
        total_issues = get_jira_issues(
            JIRA_BASE_URL, JIRA_API_TOKEN, JIRA_USERNAME, JQL_BUG_SUMMARY)
        print("Found " + str(len(total_issues)) +
              " issues with JQL: " + JQL_BUG_SUMMARY)
        if (len(total_issues)) == 0:
            # fetch labels of xray test
            labels = get_jira_labels(JIRA_BASE_URL, JIRA_API_TOKEN,
                                     JIRA_USERNAME, TEST_KEYS[0])
            # create bug with that labels
            labels = labels + LABELS + TEST_KEYS
            description = "Impacted Xray Tests: \n" + "\n".join(TEST_KEYS)
            BUG_KEY = create_jira_bug(JIRA_BASE_URL, JIRA_API_TOKEN,
                                      JIRA_USERNAME, PROJECT_KEY, labels, ASSIGNEE, SUMMARY, description)
            if (len(BUG_KEY)) > 0:
                if (EXEC_KEY != ""):
                    TEST_KEYS.append(EXEC_KEY)
                update_bug_links(JIRA_BASE_URL, JIRA_API_TOKEN,
                                 JIRA_USERNAME, RELATE_TYPE, BUG_KEY, TEST_KEYS)
                return BUG_KEY
            else:
                return 'NA'
        else:
            return ",".join([item.get('key') for item in total_issues if item.get('key') is not None])
    return 'JIRA Summary not found!'


def getFailedNames(issues_df):
    mostfailedNames = []
    for name in issues_df['name'].unique():
        trends = (issues_df[issues_df["name"] == name]
                  ['Status'].value_counts(normalize=True) * 100).round(2)
        if ('FAILED' in trends.index):
            mostfailedNames.append(name)
    latest = issues_df
    lst = [issues_df]
    del issues_df
    del lst
    return latest, mostfailedNames


def bug_analysis(JIRA_BASE_URL, JIRA_API_TOKEN, JIRA_USERNAME, PROJECT_KEY, EXEC_KEY, RELATE_TYPE, XRAY_TEST_TYPE, ASSIGNEE, DEFAULT_STATUS, BRANCH, VERSION, latest, mostfailedNames, failed_df):
    # drops duplicate test names
    latest.index = latest['name']
    latest = latest[latest.index.isin(mostfailedNames)]
    latest = latest.drop_duplicates('name', keep='first')
    if (len(latest)) > 0:
        latest = latest.groupby('message')['name'].apply(
            lambda x: list(x.index)).reset_index()

    BUG_LABEL = EXEC_KEY + "-bug"
    remove_old_bugs(JIRA_BASE_URL, JIRA_API_TOKEN,
                    JIRA_USERNAME, PROJECT_KEY, BUG_LABEL, DEFAULT_STATUS)

    if (len(failed_df) > 0):
        latest['JIRA KEY'] = latest.apply(
            lambda row: jira_bug(row, JIRA_BASE_URL, JIRA_API_TOKEN, JIRA_USERNAME, PROJECT_KEY, EXEC_KEY, RELATE_TYPE, XRAY_TEST_TYPE, ASSIGNEE, DEFAULT_STATUS, BUG_LABEL), axis=1)
        print(latest)
        # Apply the function to the 'JIRA KEY' column
        latest['JIRA KEY'] = latest['JIRA KEY'].apply(
            lambda x: create_jira_link(x, JIRA_BASE_URL))
        latest['name'] = latest['name'].apply(lambda x: '<br>'.join(x))
    else:
        latest['JIRA KEY'] = ''
        latest['message'] = ''
        latest['name'] = ''
    latest.rename(columns={'message': 'Actual Error',
                           'name': 'Impacted Xray Test Summaries', 'cleanException': 'Failed Step'}, inplace=True)
    latest = latest[['JIRA KEY', 'Actual Error',
                     'Impacted Xray Test Summaries']]
    branchVersionInfo = ""
    if len(BRANCH) > 0:
        branchVersionInfo = """<table border="1" class="dataframe center table table-hover"><tbody><tr>
                <th>TeraScript-Branch</th><th>""" + BRANCH + """</th><td>Java-Version</td><td>""" + VERSION + """ </td > </tr> </tbody></table><br>"""

    from datetime import datetime
    style = """
            <style >
                body {
                    font-family: sans-serif;
                    font-size: 11px;
                    margin: 0px;
                    background:  #f0ffff;
                }
                table {
                    font-family: sans-serif;
                    font-size: 11px;
                    border-collapse: collapse;
                }
                th, td {
                    padding: 5px;
                    text-align: left;
                    border: 2.6px solid #16151778;
                }
                td {
                    background-color: seashell;
                    color: darkslategrey;
                }
                th {
                    background-color: #bc655e;
                    color: white;
                    text-align: center;
                }
                tr:nth-child(even) {
                    background-color:  #f9f9f9;
                }
                tr:hover {
                    background-color:  #f1f1f1;
                }
                .center {
                    margin-left: auto;
                    margin-right: auto;
                }
                #perfecto {
                    width: 100px;
                }
                img {
                    display: inline-flex;
                    height: 100% ;
                }
                #images {
                    background: linear-gradient(to right,  #ffb35a70, #E3F3FE, #E3F3FE, #aacfe8 90.33%, #ffb35a70);
                    box-shadow: 0 1px 6px rgba(0, 0, 0, 0.12), 0 1px 4px rgba(0, 0, 0, 0.24);
                    height: 35px;
                    margin: auto;
                    display: flex;
                    justify-content: center;
                    padding: 2px 1px 2px 10px;
                    align-items: center;
                }
                #criteria-legend {
                    background:  #78d9e891;
                    background-image: linear-gradient(#78d9e891, #d9f0f491, #ffffffc2);
                    display: flex;
                    justify-content: center;
                    padding-top: 9px;
                }
            </style>
            <body>
            <div id = "images">
                <img src = "https://www.perfecto.io/sites/default/themes/custom/perfecto/logo.svg?height=57&amp;width=200" alt = "Perfecto" id = "perfecto" class = "center">
                <h3 style="border: 4.6px solid #3d908178;padding: 10px;border-radius: 10px;"> """ + create_jira_link(EXEC_KEY, JIRA_BASE_URL) + """ BUG REPORT: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """ </h3>
                <img src = "https://www.medanswering.com/images/MAS_web.png" alt = "logo" id = "clientlogo" class = "center">
            </div> <div id = "criteria-legend" > </div > <br>
            """ + branchVersionInfo
    html_string = style + latest.to_html(classes='center table table-hover',  # Adding CSS classes
                                         border=1,  # Adding border
                                         index=False,  # Hiding the index
                                         escape=False,
                                         # Formatting the 'JIRA#' column
                                         formatters={
                                             'JIRA#': '{:03d}'.format}
                                         )
    lst = [latest]
    del latest
    del lst
    from pathlib import Path
    BUG_REPORT_FILENAME = str(Path.cwd()) + '/Bug_Report.html'
    import os
    try:
        if os.path.exists(BUG_REPORT_FILENAME):
            os.unlink(BUG_REPORT_FILENAME)
    except Exception as e:
        print("Error: " + str(e))
    with open(BUG_REPORT_FILENAME, 'w') as f:
        f.write(html_string)
    print("\n================================\nBug report: " +
          str(BUG_REPORT_FILENAME))


def remove_old_bugs(JIRA_BASE_URL, JIRA_API_TOKEN, JIRA_USERNAME, PROJECT_KEY, BUG_LABEL, DEFAULT_STATUS):
    if (JIRA_BASE_URL != ""):
        JQL_BUG_LABEL = 'project = ' + PROJECT_KEY + \
            ' AND type = Bug AND status = "' + DEFAULT_STATUS + '" AND labels = ' + BUG_LABEL
        total_issues = get_jira_issues(
            JIRA_BASE_URL, JIRA_API_TOKEN, JIRA_USERNAME, JQL_BUG_LABEL)
        # Remove old bugs
        print("Found " + str(len(total_issues)) +
              " issues with JQL: " + JQL_BUG_LABEL)
        if (len(total_issues)) > 0:
            for issue in total_issues:
                delete_jira_bug(JIRA_BASE_URL, JIRA_API_TOKEN,
                                JIRA_USERNAME, issue["key"])
    else:
        print("No JIRA URL specified!")
