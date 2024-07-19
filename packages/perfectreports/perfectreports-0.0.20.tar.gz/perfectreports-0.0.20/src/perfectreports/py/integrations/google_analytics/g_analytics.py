from .g_functions import *
from .g_html import prepare_report
import pandas as pd
import os
import sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

# variables:

mobile_os = ['iOS', 'Android']
web_os = ['Windows', 'Macintosh']
mobile_browsers = ['Safari', 'Chrome']
users_old = 'Active users'
os_version_old = 'Operating system with version'
users = 'Users'
os_version = 'OS Version'
browser_version = 'Browser Version'
browser = 'Browser'
version = 'Browser version'
top_count = 5
recommend = 5
web_recommend = 4
#mobile
mobile_list = [os_version, browser,  browser_version]
mobile_web = []
mobile_web_recommender = []
# web
web = []
web_recommender = []
keys = ["Operating system", "Browser", "Screen resolution"]

def prepare_google_analytics_report(mobile_filename, web_filename, client_logo, devices):
    full_path = os.path.realpath(__file__)
    dirname = os.path.dirname(
        full_path)
    # remove existing html files
    for root, dirnames, filenames in os.walk(dirname):
        for filename in filenames:
            if filename.endswith('.html'):
                os.remove(os.path.join(root, filename))
    report_filename = os.path.join(dirname, 'Google_Analytics.html')

    # mobile web
    df = pd.read_csv(os.path.join(os.getcwd(), mobile_filename),
                    skiprows=6, skip_blank_lines=True, low_memory=False, index_col=False)
    df = df.iloc[1:, :]
    df = df.rename(columns={os_version_old: os_version, users_old: users})
    df[browser_version] = df[browser] + ' ' + df[version]

    for platform in mobile_os:
        for idx, key in enumerate(mobile_list):
            new_df = df[df[os_version].str.startswith(platform, na=False)].groupby([key])[users].sum().reset_index(
            ).sort_values(by=[users], ascending=False).head(top_count)  # top count
            if new_df.columns[0] == os_version:  # remove platform name from OS version
                new_df[os_version] = new_df[os_version].str.replace(
                    platform, '').str.strip()
            new_df["%"] = round((new_df[users] / new_df[users].sum())* 100, 0).astype(int).astype(str) + '%'
            mobile_web.append(create_pie_analytics(new_df, key, key, users))
            new_df = new_df.drop(columns=[users]).reset_index(
                drop=True)  # removing users column
            # need to combine two columns of different df
            if new_df.columns[0] in [os_version, browser]:
                if idx == 0:
                    old_df = new_df.head(recommend)
                else:
                    new_df[~new_df[browser].isin(mobile_browsers)] = "" # remove unsupported browsers
                    while len(new_df) < recommend: #create empty rows to match recommendations
                        new_df.loc[len(new_df)] = ''
                    merged_df = old_df.merge(new_df.head(
                        recommend), left_index=True, right_index=True)
                    merged_df = merged_df.drop(columns=['%_x', '%_y']).reset_index(drop=True)
                    mobile_web_recommender.append(merged_df.to_html(table_id="table",
                                                                    index=False,
                                                                    render_links=False,
                                                                    escape=False,
                                                                    ))



    for idx, key in enumerate(keys):
        start, end, total_rows = getStartEndFromExcel(dirname, web_filename, key)
        df = pd.read_excel(os.path.join(dirname, web_filename), skiprows=start,
                        skipfooter=(total_rows-end), index_col=False)
        new_df = df.groupby(df.columns[0])[df.columns[1]].sum().reset_index(
        ).sort_values(by=[df.columns[1]], ascending=False).head(top_count)
        new_df["%"] = round((new_df[users] / new_df[users].sum())* 100, 0).astype(int).astype(str) + '%'
        web.append(create_pie_analytics(new_df, key, key, df.columns[1]))
        new_df = new_df.drop(columns=[users]).reset_index(
            drop=True)  # removing users column
        if idx == 0:
            one = new_df.head(web_recommend)
        if idx == 1:
            two = new_df.head(web_recommend)
        if idx == 2:
            merged_df = one.merge(new_df.head(
                web_recommend), left_index=True, right_index=True)
            merged_df = two.merge(merged_df.head(
                web_recommend), left_index=True, right_index=True)
            merged_df = merged_df[keys]
            # merged_df = merged_df[merged_df[keys[0]].isin(web_os)] # picks just Web OS
            web_recommender.append(merged_df.to_html(table_id="table",
                                                    index=False,
                                                    render_links=False,
                                                    escape=False,
                                                    ))

    # prepare report
    html = prepare_report(client_logo, mobile_web, web,
                        str(top_count), mobile_web_recommender, web_recommender, devices)
    with open(report_filename, 'w') as f:
        f.write(html)
