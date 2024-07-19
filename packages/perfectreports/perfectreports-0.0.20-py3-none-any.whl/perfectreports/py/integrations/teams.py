
def read_report(file):
    from bs4 import BeautifulSoup
    status = []
    topfailedmessages = []
    # read report
    with open(file) as inf:
        txt = inf.read()
        soup = BeautifulSoup(txt, "html.parser")
        soup.prettify(formatter="minimal")
    # fetch status
    for div in soup.findAll('h2', {'class': 'option2'}):
        text = div.text
        if ':' not in text:
            status.append(text.replace("\n", ' ').replace("  ", " ").strip())
    # fetch top 3 failure messages
    i = 0
    if len(soup.find_all('table', {'id': 'topfailedmessages'})) > 0:
        for tr in soup.find_all('table', {'id': 'topfailedmessages'})[0].findAll('tr'):
            text = tr.text
            if 'Failure' not in text:
                topfailedmessages.append(
                    text[:-1].strip().replace('\n', '::: ').replace(text[:1], '').replace(text[:1], ''))
                i = i+1
                if (i == 3):
                    break
    return status, topfailedmessages


def send_teams_message(ms_webhook, direct_link, result_file, criteria):
    import pymsteams
    import os
    fails = []
    # get status and top 3 failure messages
    status, topfailedmessages = read_report(result_file)
    # card title
    myTeamsMessage = pymsteams.connectorcard(ms_webhook)
    if (criteria.startswith("START")):
        # get date
        criteria = criteria.split(",")[0].split("START:")[1].strip()
    myTeamsMessage.text(
        "".join(["**", os.environ["cloudName"].upper(), " Automation Reports Summary of ", criteria.strip(), "** "]))
    # prepare failure messages
    for item in topfailedmessages:
        fails.append(
            "".join(["- ", item.split(":::")[0].strip(), " -> _", item.split(":::")[2].strip(), "_", " \r"]))

    myMessageSection = pymsteams.cardsection()
    myMessageSection.addFact("Status:", ', '.join(status))
    if len(fails) > 0:
        myMessageSection.addFact("Top 3 Failure insights:", "".join(fails))
    myTeamsMessage.addSection(myMessageSection)
    # create direct azure report link if needed.
    if direct_link != "":
        myTeamsMessage.addLinkButton(
            "View Report", direct_link.replace(r' ', '%20'))
    myTeamsMessage.send()
