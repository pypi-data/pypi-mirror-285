
def prepare_report(client_logo, mobile_web, web, top_count, mobile_web_recommender, web_recommender, json):
    # https://codepen.io/dp_lewis/pen/WNZQzN
    html = str('''
    <!DOCTYPE html>
    <script src="http://code.jquery.com/jquery-1.11.0.min.js"></script>
    <META http-equiv="Content-Type" content="text/html; charset=UTF-8"> 
    <html>
    <head>
        <style>
        
            #combined {
                display: inline-flex;
                justify-content: center;
                flex-direction: row;
                overflow: scroll;
                justify-content: flex-start;
            }
            
            input[type="radio"] {
                visibility: hidden;
            }
            
            #1,#2,#3 {
                height:1px;
            }
            
            #label {
                background: #444;
                color: #fff;
                transition: transform 400ms ease-out;
                display: inline-grid;
                width: 100vw;
                height: 430px;
                position: relative;
                z-index: 1;
                text-align: center;
                line-height: 4vh;
                margin-top: -5px;
            }

            form {
                position: absolute;
                left: 0;
                right: 0;
                white-space: nowrap;
            }

            input {
                position: absolute;
            }

            input:nth-of-type(1):checked~#label:nth-of-type(1),
            input:nth-of-type(2):checked~#label:nth-of-type(2),
            input:nth-of-type(3):checked~#label:nth-of-type(3) {
                z-index: 0;
            }

            input:nth-of-type(1):checked~#label {
                transform: translate3d(0, 0, 0);
            }

            input:nth-of-type(2):checked~#label {
                transform: translate3d(-100%, 0, 0);
            }

            input:nth-of-type(3):checked~#label {
                transform: translate3d(-200%, 0, 0);
            }

            #label {
                background: rgba(232, 255, 227, 0.58);
                background-size: cover;
                font-size: 1rem;
            }

            #label:before,
            #label:after {
                color: white;
                display: block;
                background: rgba(22, 34, 73, 0.27);
                position: absolute;
                padding: 1rem;
                font-size: 2rem;
                height: 9rem;
                vertical-align: middle;
                line-height: 9rem;
                top: 52%;
                transform: translate3d(0, -50%, 0);
                cursor: pointer;
            }

            #label:before {
                content: ">";
                right: 100%;
                border-top-left-radius: 50%;
                border-bottom-left-radius: 50%;
            }

            #label:after {
                content: "<";
                left: 100%;
                border-top-right-radius: 50%;
                border-bottom-right-radius: 50%;
            }
        
            html {
                display:inline-grid;
            }
            
            body {
                font-family: sans-serif;
                font-size: 11px;
                margin: 0px;
                background: #f0f7f7bf;
                overflow: hidden;
            }

            table, th, td {
                border: 0px solid black;
                border-collapse: collapse;
                font-size: 11px;
            }


            table.center {
                margin-left: auto;
                margin-right: auto;
            }

            th,
            td {
                padding: 2px;
                font-weight: 100;
            }

            th {
                border-radius: 5px 5px 0px 0px;
                text-align: left;
                box-sizing: border-box;
                border: 2px solid #366e9936;
                font-size: 12px;
                background: #5e90d8;
                font-weight: 600;
                color: white;
                line-height: 150%;
                vertical-align: middle;
            }

            td {
                box-sizing: border-box;
                border: 2px solid #366e9936;
                position: relative;
                color: #200302;
                background: #ffffff;
                vertical-align: middle;
                font-size: 11px;
                line-height: 140%;
                text-align: left;
                border-radius: 10px 0px 10px 0px;
            }

            img {
                display: inline-flex;
                height: 100%;
            }

            #summary {
                text-align: center;
                background: #f0ffff;
            }

            #piechart,
            #browserChart {
                background-color: rgba(238, 240, 223, 0.68);
                display: block;
                width: 300px;
                height: 240px;
                margin: 5px;
                box-shadow: 0 0 60px rgb(80 130 50 / 33%);
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

            #clientlogo {
                width: 100px;
                padding-left: 20px;
            }

            #perfecto {
                width: 100px;
            }

            #table {
                box-shadow: 0 10px 10px rgb(80 130 50 / 33%);
                overflow-y: scroll;
                word-wrap: break-word;
                margin-top: 0px;
                max-height: 533px;
                border: 2px solid #90cfe27d;
                border-radius: 6px;
                width: 100%;
            }

            #slide {
                display: inline-block;
                flex-direction: row;
                overflow: scroll;
                align-items: self-start;
                justify-content: flex-start;
                margin-top: 8px;
            }

            a {
                color: #04192d;
            }

            #heading {
                font-size: small;
                display: flex;
                flex-direction: row;
                align-items: center;
                justify-content: center;
                font-weight: bold;
                width: 100%;
                padding: 5px 0;
                text-align: center;
                cursor: pointer;
                color: white;
                background: #002e5dd1;
                height: 15px;
                border-radius: 5px 5px 0px 0px;
            }

            svg {
                overflow: scroll;
            }

            #box {
                box-shadow: 0 -4px 18px 0 rgba(60, 118, 191, 0.55);
                margin-right: 2px;
                margin-left: 2px;
                margin-top: 3px;
                margin-bottom: -2px;
                border: 1px solid #89def77d;
                width: 100%;
                object-fit: cover;
                border-radius: 6px;
            }

            #rect {
                border: 5px solid #12303947;
                border-radius: 10px;
                margin: 3px;
                display: inline-block;
                vertical-align:middle;
                background: #add8e6b8;
            }
            #jsoneditor {
                margin-top: 430px !important;
                width: 800px;
                height: 760px;  
                overflow: auto;
            }
            .jse-hidden-input-label{
              height: 0px  !important;
            }
        </style>
        </head>
        <title>PerfectReports - Analytics</title>

        <body>
            <div id="images">
                <img src='https://www.perfecto.io/sites/default/themes/custom/perfecto/logo.svg?height=57&width=200'
                    alt="Perfecto" id="perfecto" class="center">
                <img src="''' + client_logo + '''" alt="logo" id="clientlogo" class="center">
                <img src="https://fibbl.com/wp-content/uploads/2023/10/6322e2479751c370b289db18_Logo_Google_Analytics.svg.png" alt="google_logo" id="clientlogo" class="center">
            </div>
            
            <div id="summary">
            <form>
                <input type="radio" name="fancy" autofocus value="1" id="1" />
                <input type="radio" name="fancy" value="2" id="2" />
                <input type="radio" name="fancy" value="3" id="3" />
                <label id="label" for="1">
                    <div id="slide">
                        <div id="box">
                            <div id="heading">Web - Top ''' + top_count + '''</div>
                            <div id="combined">
                                <div id="rect">''' + web[0] + '''</div>
                                <div id="rect">''' + web[1] + '''</div>
                                <div id="rect">''' + web[2] + '''</div>
                               <div id="rect"><div id="heading">PS Recommendation</div>''' + web_recommender[0] + '''</div>
                            </div>
                        </div>
                    </div>
                </label>
                <label id="label" for="2">
                    <div id="slide">
                        <div id="box">
                            <div id="heading">iOS - Top ''' + str(top_count) + '''</div>
                            <div id="combined">
                                <div id="rect">''' + mobile_web[0] + '''</div>
                                <div id="rect">''' + mobile_web[1] + '''</div>
                                <div id="rect">''' + mobile_web[2] + '''</div>
                                <div id="rect"><div id="heading">PS Recommendation</div>''' + mobile_web_recommender[0] + '''</div>
                            </div>
                        </div>
                    </div>
                </label>
                <label id="label" for="3">
                    <div id="slide">
                        <div id="box">
                            <div id="heading">Android - Top ''' + top_count + '''</div>
                            <div id="combined">
                                <div id="rect">''' + mobile_web[3] + '''</div>
                                <div id="rect">''' + mobile_web[4] + '''</div>
                                <div id="rect">''' + mobile_web[5] + '''</div>
                                <div id="rect"><div id="heading">PS Recommendation</div>''' + mobile_web_recommender[1] + '''</div>
                            </div>
                        </div>
                    </div>
                </label>
            </form>
            </div>
            <div style="display: flex;justify-content: center;background: lightcyan;">
                <div id="jsoneditor"></div>
            </div>
            <script type="module">
                import { JSONEditor } from 'https://cdn.jsdelivr.net/npm/vanilla-jsoneditor/standalone.js'

                let content = {
                    text: undefined,
                    json: ''' + str(json) + '''
                    }

                    const editor = new JSONEditor({
                        target: document.getElementById('jsoneditor'),
                        props: {
                        content,
                        onChange: (updatedContent, previousContent, { contentErrors, patchResult }) => {
                            // content is an object { json: unknown } | { text: string }
                            console.log('onChange', { updatedContent, previousContent, contentErrors, patchResult })
                            content = updatedContent
                        }
                        }
                    })

                    // use methods get, set, update, and onChange to get data in or out of the editor.
                    // Use updateProps to update properties.
                    </script>
        </body>
        </html>
            ''')
    return html