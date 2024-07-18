import sweetviz as sv
import os
from bs4 import BeautifulSoup


def update(client_logo, report_filename, file):
    with open(file) as inf:
        txt = inf.read()
        soup = BeautifulSoup(txt, "html.parser")
        soup.prettify(formatter="minimal")

    # remove summary
    elements = soup.findAll(attrs={'id': ['summary-df']})
    try:
        for element in elements:
            element.decompose()
    except:
        pass

    # remove top section
    for tag in soup.findAll(attrs={'class': ['page-column-main']}):
        tag['style'] = "top: -160px;z-index:-1;"

    for tag in soup.findAll(attrs={'class': ['graph-legend', 'pos-logo-group']}):
        tag.decompose()
    
    heading = """
    <style>
        body {
            height: 0px;
        }
        
        #images {
            background: linear-gradient(to right, #ffb35a70, #E3F3FE, #E3F3FE, #aacfe8 90.33%, #ffb35a70);
            box-shadow: 0 1px 6px rgba(0, 0, 0, 0.12), 0 1px 4px rgba(0, 0, 0, 0.24);
            height: 35px;
            margin: auto;
            display: flex;
            justify-content: center;
            padding: 2px 1px 2px 10px;
            }
    </style>
    <div id="images">
        <img src="https://www.perfecto.io/sites/default/themes/custom/perfecto/logo.svg?height=57&width=200" alt="Perfecto" id="perfecto" class="center">
        <img style="margin-left: 20px;" src='"""+client_logo+"""' alt="logo" id="clientlogo" class="center">
        <a href='./""" + report_filename + """' target="_blank" ><img style="margin-left: 20px;" width="40" height="35" src="https://img.icons8.com/fluency/48/graph-report.png" id="reporticon" alt="analytics-report" /></a>
    </div> """
    with open(file, "w") as outf:
        outf.write(heading)
        outf.write(str(soup))


def generate_advanced_analytics(df, client_logo, report_filename, configpath, filename, internal):
    profile_df = df.copy(deep=False)
    del_cols = [
        col for col in df.columns if 'artifacts' in col or 'selectionCriteriaV2' in col or 'customFields' in col or 'tags' in col or 'videos' in col or 'executionEngine' in col or 'parameters' in col]
    del_cols.extend(["id", "index", "externalId", "df_index", "Duration", 'owner', 'uxDuration', 'month', 'week', 'startDate', "startTime",
                    "endTime", "job/number", "reportURL", "platforms/0/deviceId", 'platforms/0/mobileInfo/imei', 'platforms/0/mobileInfo/distributor', 'platforms/0/mobileInfo/firmware', 'triggerType', 'retry', 'hidden', 'duration', 'uiOptions/strStatus', 'version', 'testExecutionId', 'tracking/createdAt', 'tracking/lastUpdatedAt', 'failureReason/id', 'failureReason/isSystemAssigned', 'errorAnalysis/normalizedCleanException'])
    profile_df.drop(del_cols, axis=1, errors='ignore', inplace=True)
    profile_df.reset_index(drop=True, inplace=True)
    if internal == "true":
        profile_df.rename(columns={'failureReason/name': 'Custom Failure Reasons'})
    else:
         profile_df.rename(columns={'failureReasonName': 'Custom Failure Reasons'})
    profile_df.rename(columns={'name': 'Test Name', 'owner': 'Test Owner', 'message': 'Test Failure Message',
                               'automationFramework': 'Test Automation Framework', 'status': 'Status', 'platforms/0/screenResolution': 'Platform Screen Resolution', 'platforms/0/browserInfo/browserType': 'Browser Type', 'platforms/0/browserInfo/browserVersion': 'Browser Version', 'job/name': 'Job Name', 'job/branch': 'Job Branch', 'platforms/0/osVersion': 'Platform OS Version', 'platforms/0/os': 'Platform OS', 'platforms/0/mobileInfo/phoneNumber': 'Device Phone Number',
                               'model': 'Device Model', "cleanException": 'Failed Steps', 'browserType': 'Browser Type', 'browserVersion': 'Browser Version', 'platforms/0/location': 'Platform Location', 'platforms/0/deviceType': 'Platform DeviceType', 'platforms/0/mobileInfo/manufacturer': 'Device Manufacturer', 'project/version': 'Project Version', 'project/name': 'Project Name', 'platforms/0/mobileInfo/operator': 'Mobile Operator', 'platforms/0/mobileInfo/hasAudio': 'Mobile Device Audio?'}, inplace=True)
    output_file = os.path.join(os.getcwd(),  filename)
    feature_config = sv.FeatureConfig(skip=[])
    my_report = sv.analyze(profile_df, pairwise_analysis='off',
                           feat_cfg=feature_config)
    sv.config_parser.read(os.path.join(configpath, "configs", "Override.ini"))
    my_report.show_html(filepath=output_file,
                        open_browser=False,
                        layout='widescreen',
                        scale=None)
    update(client_logo,report_filename, output_file)
    print("Analytics: file://" + output_file)
