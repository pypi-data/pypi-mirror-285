
def prepare_html(client_logo, criteria, total, passed, failed, unknown, blocked, execution_summary,
                 tags_base64, failure_items, custom_failure_items, version_items, tags_df_table, failedTable, topfailedtc_table, analytics_html, failurecategorytable):
    html = str('''
<!DOCTYPE html>
<script src="http://code.jquery.com/jquery-1.11.0.min.js"></script>
<META http-equiv="Content-Type" content="text/html; charset=UTF-8"> 
<html>
<header>
    <link href="https://cdn.datatables.net/1.11.5/css/jquery.dataTables.min.css" rel="stylesheet">
</header>
<head>
    <style>
    
        html {
            display:inline-grid;
        }
        
        body {
            font-family: sans-serif;
            font-size: 11px;
            margin: 0px;
            background: #f0f7f7bf;
        }

        .option2 {
            text-indent: 15px;
            display: inline-block;
            padding-right: 28px;
            text-align: right;
            margin: -4px;
            border-radius: 1em;
        }

        .stuckHead {
            position: sticky;
            top: 0;
            z-index: 1;
        }

        #tagsheading {
            border: 2px solid #90cfe27d;
        }
        table,
        th,
        td {
            border: 0px solid black;
            border-collapse: collapse;
            font-size: 11px;
        }

        .options2 {
            opacity: .8;
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
            text-align: center;
            box-sizing: border-box;
            border: 2px solid #366e9936;
            font-size: 12px;
            background: #5e90d8;
            font-weight: 600;
            color: white;
            text-align: center;
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
        }

        img {
            display: inline-flex;
            height: 100%;
        }

        #summary {
            text-align: center;
            background: #f0ffff;
        }

        ::-webkit-scrollbar {
            -webkit-appearance: none;
            width: 5px;
            height: 5px;
        }

        ::-webkit-scrollbar-thumb {
            border-radius: 2px;
            background-color: rgba(0, 0, 0, .5);
            box-shadow: 0 0 1px rgba(255, 255, 255, .5);
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

        .dataTables_wrapper .dataTables_filter input {
            padding: 3px;
        }
        
        #table tr td:nth-child(1), table.dataTable th:nth-child(1) {
          width: 50px;
          max-width: 50px;
        }
        #table tr td:nth-child(2), table.dataTable th:nth-child(2) {
            width: 80px;
            max-width: 80px;
        }
        
        #table tr td:nth-child(3), table.dataTable th:nth-child(3) {
            width:450px;
            max-width:450px;
        }

        #table tr td:nth-child(4), table.dataTable th:nth-child(4){
            width: 90px;
            max-width: 90px;
        } 
        
        #table tr td:nth-child(5), table.dataTable th:nth-child(5){
            max-width: 100px;
            width: 100px;
        }
        
        #table tr td:nth-child(6), table.dataTable th:nth-child(6) {
          max-width: 190px;
          width:190px;
        }

        table.dataTable th:nth-child(7) {
          width:35px;
          max-width:35px;
        }
      
        table.dataTable thead th, table.dataTable thead td {
          padding: 8px 0px;
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

        #criteria-legend {
            box-shadow: 0 1px 6px rgba(0, 0, 0, 0.12), 0 1px 4px rgba(0, 0, 0, 0.24);
            background: #78d9e891;
            background-image: linear-gradient(#78d9e891, #d9f0f491, #ffffffc2);
            padding: 5px;
            display: flex;
            justify-content: center;
            padding-top: 9px;
        }

        #summary-legend {
            box-shadow: 0 1px 6px rgba(0, 0, 0, 0.12), 0 1px 4px rgba(0, 0, 0, 0.24);
            background: #ffb35a70;
            padding: 5px;
        }

        #table, #tableDiv {
            box-shadow: 0 10px 10px rgb(80 130 50 / 33%);
            overflow-y: scroll;
            word-wrap: break-word;
            margin-top: 0px;
            max-height: 533px;
            width: 770px;
            border: 2px solid #90cfe27d;
        }

        #moduleheading {
            overflow: scroll;
            height: 210px;
            max-width: 400px;
        }

        #hie {
            display: flex;
            flex-wrap: wrap;
            flex-direction: column;
            align-content: center;
        }

        .option2 {
            font-size: small;
        }
        
        #vidlink {
            background-image: url(https://img.icons8.com/office/16/link.png);
            background-position: 2px 0px;
            background-repeat: no-repeat;
            height: 16px;
            width: 18px;
        }

        #tags, #category,
        #topfailedtests, #topfailedmessages {
            overflow-y: scroll;
            word-wrap: break-word;
            display: inline-block;
            border-collapse: collapse;
            table-layout: fixed;
            max-height: 128px;
            width: 100%;
        }

        #tags tbody tr th, #category tbody tr th,
        #topfailedtests tbody tr th, #topfailedtests tbody tr th, #topfailedtests tbody tr,
        #topfailedmessages tbody tr th, #topfailedmessages tbody tr th, #topfailedmessages tbody tr {
            text-align: left;
            background: #fffaf2;
            color: black;
            font-weight: 100;
            font-size: 10px;
        }

        #category tbody tr th {
            width: 100%;
        }
        #topfailedtests tbody tr th,
        #topfailedmessages tbody tr th {
            width: 200px !important;
        }

        #topfailedtests tbody tr td:nth-child(1),
        #topfailedmessages tbody tr td:nth-child(1) {
            min-width: 385px;
            max-width: 385px; 
            width: 100%;
        }
        
        #tags tbody tr th:nth-child(3) {
            width: 100%;
        }

        #category tbody tr th:nth-child(3){
            min-width: 220px;
        }
        #tags thead tr:nth-child(1), #category thead tr:nth-child(1) {
            display: none;
        }
        
        #tags thead tr:nth-child(2) th:nth-child(4):before, #category thead tr:nth-child(2) th:nth-child(4):before  {
            content: "Total";
        }
        
        #tags thead tr:nth-child(2) th:nth-child(5):before, #category thead tr:nth-child(2) th:nth-child(5):before{
            content: "✓%↑";
        }

        #slide {
            display: inline-flex;
            background: #f8ffff;
            flex-direction: row;
            overflow: scroll;
            align-items: self-start;
            justify-content: flex-start;
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
        }

        svg {
            overflow: scroll;
        }

        #box {
            box-shadow: 0 -4px 18px 0 rgba(60, 118, 191, 0.55);
            margin-right: 2px;
            margin-left: 2px;
            margin-top: 3px;
            border: 1px solid #89def77d;
        }

        #topfailbox {
            margin: 3px;
            max-height: 310px;
            width: 380px;
            overflow: scroll;
            display: inline-table;
        }
        
        #reporticon {
            padding-left: 20px;   
        }
    </style>
</head>
<title>PerfectReports</title>

<body>
    <div id="images">
        <img src='https://www.perfecto.io/sites/default/themes/custom/perfecto/logo.svg?height=57&width=200'
            alt="Perfecto" id="perfecto" class="center">
        <img src="''' + client_logo + '''" alt="logo" id="clientlogo" class="center">
        <a href="./''' + analytics_html + '''" target="_blank" ><img width="40" height="35" src="https://img.icons8.com/external-smashingstocks-thin-outline-color-smashing-stocks/67/external-Data-Analytics-industrial-production-smashingstocks-thin-outline-color-smashing-stocks-2.png" id="reporticon"
      alt="graph-report" /></a>
    </div>
    <div id="criteria-legend">
        <h2 class="option2" style="background-color:#ffd7aed4;">''' + str(criteria) + '''</h2>
        <h2 class="option2" style="background-color:lightgoldenrodyellow;">''' + str(total) + ''' \nTESTS</h2>
        <h2 class="option2" style="background-color:#33d63391;">''' + str(passed) + ''' \nPASSED</h2>
        <h2 class="option2" style="background-color:#ff5f41b5;">''' + str(failed) + ''' \nFAILED</h2>
        <h2 class="option2" style="background-color:#f2ebeb;">''' + str(unknown) + ''' \nUNKNOWNS</h2>
        <h2 class="option2" style="background-color:#ffa50091">''' + str(blocked) + ''' \nBLOCKED</h2>
    </div>
    <div id="summary">
        <div id="slide">
            <div id="box"><div id="heading">Overall Status</div>''' + execution_summary + '''</div></div>
            <div id="box"><div id="heading">Module-wise Status</div><div id="moduleheading">''' + tags_base64 + '''</div></div>
            ''' + version_items + ''' 
            <div id="box"><div id="heading">Top 5 Custom Failure Reasons</div><div>''' + custom_failure_items + '''</div></div>
        </div>
    </div>
    <div id="summary">
        <div id="slide">
            <div id="topfailbox">
                <div id="heading">Top 10</div>
                <div id="tagsheading">''' + failure_items + '''</div>
                <div id="tagsheading">''' + failurecategorytable + '''</div>
                <div id="tagsheading">''' + tags_df_table + '''</div>
                <div id="tagsheading">''' + topfailedtc_table + '''</div>
            </div>
            <div id="box">
                <div id="heading">Failed Tests Summary</div>
                <div id="tableDiv">''' + failedTable + '''</div>
            </div>
        </div>
    </div>
</body>
</script>
<script src="https://code.jquery.com/jquery-3.6.0.slim.min.js" integrity="sha256-u7e5khyithlIdTpu22PHhENmPcRdFiHRjhAuHcs05RI=" crossorigin="anonymous"></script>
<script type="text/javascript" src="https://cdn.datatables.net/1.11.5/js/jquery.dataTables.min.js"></script>
<script>
    $(document).ready( function () {
        $('#table').DataTable({
            paging: true,
            searching: true,
            responsive: true,
            "autoWidth": false,
            "pageLength": 4
        });
    });
</script>
</html>
        ''')
    return html
