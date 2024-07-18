import pandas
import requests
import json
import os
import sys
from functions import *
from commands_api import *
osVersions = []
from integrations.google_analytics.g_analytics import *

mobile_filename = 'web-portal-30-days-mobile-os.csv'
web_filename = "web-portal-last-12-months-tech copy.xlsx"
client_logo = "https://www.medanswering.com/images/MAS_web.png"
devices = get_devices_list()
prepare_google_analytics_report(mobile_filename, web_filename, client_logo, devices)



# osVersions = get_os_versions_list(devices)
# osVersions_major = get_os_version_major(osVersions)
# print(osVersions_major)

# print(find_nearest_decimal(13.7, osVersions_major))
