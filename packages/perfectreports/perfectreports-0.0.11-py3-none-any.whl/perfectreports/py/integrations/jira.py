import requests
from requests.auth import HTTPBasicAuth
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
    print(JIRA_JQL_QUERY)
    headers, session = create_jira_session()
    URL = f'{JIRA_BASE_URL}/rest/api/2/search'

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
                print("Failed to query JIRA URL: " + URL + ", "+ response.status_code + " : " + response.text)
                break
        except requests.exceptions.RequestException as e:
            print(f'Request failed: {e}')
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
            logger.info(f'Successfully created issue: {issue_key}')
        else:
            logger.error(f'Failed to create issue: {
                         response.status_code} - {response.text}')
    except requests.exceptions.RequestException as e:
        logger.error(f'Request failed: {e}')
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
                print(f'Successfully linked bug {BUG_KEY} to test {TEST_KEY}')
            else:
                print(f'Failed to link issues: {
                    response.status_code} - {response.text}')
        except requests.exceptions.RequestException as e:
            logger.error(f'Request failed: {e}')


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
            logger.info(f'Successfully deleted issue: {ISSUE_KEY}')
        else:
            logger.error(f'Failed to delete issue: {
                response.status_code} - {response.text}')
    except requests.exceptions.RequestException as e:
        logger.error(f'Request failed: {e}')


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
            print(f"Labels for issue {ISSUE_KEY}: {labels}")
        else:
            print(f"Failed to retrieve issue: {
                response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f'Request failed: {e}')
    return labels


def get_test_keys(JIRA_BASE_URL, JIRA_API_TOKEN, JIRA_USERNAME, PROJECT_KEY, XRAY_TEST_TYPE, SUMMARIES):
    TEST_KEYS = []
    for SUMMARY in SUMMARIES:
        # escape hypen to avoid jql issues
        SUMMARY = SUMMARY.replace(' -', r' \\-')
        JQL_JUST_SUMMARY = 'project = "' + PROJECT_KEY + \
            '" AND type = "' + XRAY_TEST_TYPE + '" AND summary ~ "' + SUMMARY + '"'
        total_issues = get_jira_issues(
            JIRA_BASE_URL, JIRA_API_TOKEN, JIRA_USERNAME, JQL_JUST_SUMMARY)
    # list xray test
        print(f'Found {len(total_issues)} issue with summary: ' + SUMMARY)
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
    key = "XS-41"
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


def raise_bug(JIRA_BASE_URL, JIRA_API_TOKEN, JIRA_USERNAME, PROJECT_KEY, EXEC_KEY, RELATE_TYPE, ASSIGNEE, LABELS, SUMMARY, XRAY_TEST_TYPE, SUMMARIES, JQL_BUG_LABEL, JQL_BUG_SUMMARY):
    # get test keys
    TEST_KEYS = get_test_keys(JIRA_BASE_URL, JIRA_API_TOKEN,
                              JIRA_USERNAME, PROJECT_KEY, XRAY_TEST_TYPE, SUMMARIES)

    if (len(TEST_KEYS) > 0):
        total_issues = get_jira_issues(
            JIRA_BASE_URL, JIRA_API_TOKEN, JIRA_USERNAME, JQL_BUG_LABEL)
        # Remove old bugs
        print(f'Found {len(total_issues)} issues with JQL: ' + JQL_BUG_LABEL)
        if (len(total_issues)) > 0:
            for issue in total_issues:
                print(f'- {issue["key"]}:{issue["fields"]["summary"]}')
                delete_jira_bug(JIRA_BASE_URL, JIRA_API_TOKEN,
                                JIRA_USERNAME, issue["key"])

        # Checks for existing issues with different statuses except To Do and don't create a bug if exists.
        total_issues = get_jira_issues(
            JIRA_BASE_URL, JIRA_API_TOKEN, JIRA_USERNAME, JQL_BUG_SUMMARY)
        print(f'Found {len(total_issues)
                       } issues with JQL: ' + JQL_BUG_SUMMARY)
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
                if(EXEC_KEY != ""):
                    TEST_KEYS.append(EXEC_KEY)
                update_bug_links(JIRA_BASE_URL, JIRA_API_TOKEN,
                                 JIRA_USERNAME, RELATE_TYPE, BUG_KEY, TEST_KEYS)
                return BUG_KEY
            else:
                return 'NA'
        else:
            return ",".join([item.get('key') for item in total_issues if item.get('key') is not None])
    return 'JIRA Summary not found!'
