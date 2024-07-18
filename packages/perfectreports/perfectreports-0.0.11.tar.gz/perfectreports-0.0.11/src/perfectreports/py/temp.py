import functions

json = {
    "desktopDevices": [
        {
            "os": "Mac",
            "resolutions": [
                "800x600",
                "1024x768",
                "1280x720",
                "1280x1024",
                "1440x900",
                "1680x1050",
                "1920x1080",
                "2560x1600",
                "3840x2160"
            ],
            "osVersions": [
                {
                    "osVersion": "macOS Big Sur",
                    "locations": [
                        "NA-US-BOS"
                    ],
                    "browsers": [
                        {
                            "browser": "Chrome",
                            "browserVersions": [
                                "beta",
                                "122",
                                "121",
                                "120",
                                "119",
                                "118",
                                "117",
                                "116",
                                "115",
                                "114",
                                "113"
                            ]
                        },
                        {
                            "browser": "Firefox",
                            "browserVersions": [
                                "beta",
                                "123",
                                "122",
                                "121",
                                "120",
                                "119",
                                "118",
                                "117",
                                "116",
                                "115",
                                "114"
                            ]
                        },
                        {
                            "browser": "Safari",
                            "browserVersions": [
                                "14"
                            ]
                        }
                    ]
                }
            ]
        },
        {
            "os": "Windows",
            "resolutions": [
                "1024x768",
                "1280x1024",
                "1366x768",
                "1440x900",
                "1600x1200",
                "1920x1080",
                "2560x1440"
            ],
            "osVersions": [
                {
                    "osVersion": "11",
                    "locations": [
                        "AP Sydney",
                        "EU Frankfurt",
                        "US East"
                    ],
                    "browsers": [
                        {
                            "browser": "Chrome",
                            "browserVersions": [
                                "beta",
                                "122",
                                "121",
                                "120",
                                "119",
                                "118",
                                "117",
                                "116",
                                "115",
                                "114",
                                "113"
                            ]
                        },
                        {
                            "browser": "Edge",
                            "browserVersions": [
                                "beta",
                                "122",
                                "121",
                                "120",
                                "119",
                                "118",
                                "117",
                                "116",
                                "115",
                                "114",
                                "113"
                            ]
                        },
                        {
                            "browser": "Firefox",
                            "browserVersions": [
                                "beta",
                                "123",
                                "122",
                                "121",
                                "120",
                                "119",
                                "118",
                                "117",
                                "116",
                                "115",
                                "114"
                            ]
                        }
                    ]
                },
                {
                    "osVersion": "10",
                    "locations": [
                        "AP Sydney",
                        "EU Frankfurt",
                        "US East"
                    ],
                    "browsers": [
                        {
                            "browser": "Chrome",
                            "browserVersions": [
                                "beta",
                                "122",
                                "121",
                                "120",
                                "119",
                                "118",
                                "117",
                                "116",
                                "115",
                                "114",
                                "113"
                            ]
                        },
                        {
                            "browser": "Edge",
                            "browserVersions": [
                                "beta",
                                "122",
                                "121",
                                "120",
                                "119",
                                "118",
                                "117",
                                "116",
                                "115",
                                "114",
                                "113"
                            ]
                        },
                        {
                            "browser": "Firefox",
                            "browserVersions": [
                                "beta",
                                "123",
                                "122",
                                "121",
                                "120",
                                "119",
                                "118",
                                "117",
                                "116",
                                "115",
                                "114"
                            ]
                        }
                    ]
                }
            ]
        }
    ],
    "info": {
        "date": "Mon Feb 26 09:03:38 UTC 2024",
        "modelVersion": "1.0",
        "systemTime": "1708938218772"
    }
}

import pandas 

# df = pandas.DataFrame([functions.flatten_json(x) for x in json['desktopDevices']])
df =  pandas.DataFrame(json['desktopDevices'])
print(df)