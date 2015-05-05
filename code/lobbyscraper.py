#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
This is a scraper for the Austrian Lobbying-Register. It fetches the HTML, saves it locally
and converts the relevant data into a json file.
"""

import re
from datetime import datetime
import json
import os
from bs4 import BeautifulSoup
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

__author__ = "Stefan Kasberger"
__copyright__ = "Copyright 2015"
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Stefan Kasberger"
__email__ = "mail@stefankasberger.at"
__status__ = "Development" # 'Development', 'Production' or 'Prototype'

###    GLOBAL   ###

BASE_URL = 'http://www.lobbyreg.justiz.gv.at/edikte/ir/iredi18.nsf'
QUERY_URL = BASE_URL+'/liste!OpenForm&subf=a'
ROOT_FOLDER = os.path.dirname(os.getcwd())
FOLDER_HTML = ROOT_FOLDER + '/data/raw/'
FOLDER_JSON = ROOT_FOLDER + '/data/json/'
FILENAME_HTML = 'lobbyingregister.htm'
FILENAME_JSON = 'lobbyingregister.json'

###    FUNCTIONS   ###

def SetupEnvironment():
    if not os.path.exists(FOLDER_HTML):
        os.makedirs(FOLDER_HTML)
    if not os.path.exists(FOLDER_JSON):
        os.makedirs(FOLDER_JSON)

def FetchHtml(url):
    """Fetches html url via urllib().

    Args:
        url: url to fetch

    Returns:
        html string as unicode
    """
    response = urllib2.urlopen(url)
    rawHtml = response.read().decode('utf-8')
    return rawHtml

def FetchHtmlList(url, folder, filename):
    """Fetches html from the overview list of the lobbyingregister entries and saves it locally.

    Args:
        url: url to fetch
        folder: to save the html
        filename: filename for the html file

    Returns:
        html string
    """
    rawHtml = FetchHtml(url)
    if not os.path.exists(folder):
        os.makedirs(folder)
    Save2File(rawHtml, folder+'/'+filename)
    return rawHtml

def FetchHtmlOrganisations(organisations, folder):
    """Fetches html from a lobbying-organisation and saves it locally.

    Args:
        organisations: dict with sequencial id's of organisations as keys.
        folder: to save the html

    Returns:
        dict() of sequencial id's of organisations as key and html as value.
    """
    html = {}
    for id in organisations.keys():
        organisation = organisations[id]
        html[id] = FetchHtml(organisation['url'])
        Save2File(html[id], folder+'/'+str(id)+'.htm')
    return html

def Save2File(data, filename):
    """Saves file locally

    Args:
        data: string to save
        filename: name of the file

    Returns:
        na
    """
    text_file = open(filename, "wb")
    text_file.write(data.encode('utf-8'))
    text_file.close()

def ReadFile(filename):
    """Reads file and returns the html.

    Args:
        filename: name of the file

    Returns:
        html from the file.
    """
    f = open(filename, 'r')
    html = f.read()
    return html

def ReadOrganisations(folder):
    """Reads in all html-files from the organisations folder.

    Args:
        folder: folder where the organisation html-files are stored.

    Returns:
        dict() of sequencial id's of organisations as key and html as value.
    """
    html = {}
    for filename in os.listdir(folder):
        rawHtml = ReadFile(folder+'/'+filename)
        if not filename in FILENAME_HTML:
            html[int(filename.split('.')[0])] = rawHtml
    return html

def ParseList(html):
    """Parses the needed facts out of the overview list html.

    Args:
        html: html string
        timestamp: time when the html download was started.

    Returns:
        dict() of sequencial id's of organisations as key and dict() with facts as value.
    """
    lobbyList = {}
    counter = 0
    # root = lxml.html.fromstring(html)
    soup = BeautifulSoup(html)

    # loop over table rows
    for tr in soup.tbody.find_all('tr'):
        tds = tr.find_all('td')

        # assign variables from html table to dict
        organisation = {}
        try:
            organisation['description'] = unicode(tds[1].string) # organisation
        except NameError:
            organisation['description'] = tds[1].string # organisation
        organisation['registry-department'] =  tds[3].string # register department
        organisation['url'] =  BASE_URL+'/'+tds[2].a['href'] # register number url
        organisation['last-update'] = str(datetime.strptime(tds[5].string, '%d.%m.%Y')) # last update
        organisation['register-number'] = tds[2].string
        # organisation['details'] =  lxml.html.tostring(tds[4], encoding='unicode')[4:-4].split('<br>')[:-1] # details

        lobbyList[counter] = organisation
        counter += 1
    return lobbyList

def ParseOrganisations(htmlList, organisations):
    """Parses the needed facts out of the organisation html.

    Args:
        htmlList: list() of html strings.
        organisations: dict() of sequencial id's of organisations as key and dict() with facts as value.

    Returns:
        dict() of sequencial id's of organisations as key and dict() with facts as value.
    """

    for id in organisations.keys():
        soup = BeautifulSoup(htmlList[id])
        try:
            html = unicode(soup)
        except NameError:
            html = str(soup)

        # regex type of registry department: B, C
        regDepartment = re.findall(r'Registerabteilung:</strong></dt>\n<dd><strong>(.*)</strong></dd></dl>', html)
        if regDepartment:
            if organisations[id]['registry-department'] != regDepartment[0]:
                print("ERROR: register department differs!")

        # regex register number: B, C
        regNum = re.findall(r'Registerzahl:</strong></dt>\n<dd><strong>(.*)</strong></dd></dl>', html)
        if regNum:
            if organisations[id]['register-number'] != regNum[0]:
                print("ERROR: register number differs!")

        # regex name: A1, B, C
        name = re.findall(r'Name.*:</strong></dt>\n<dd><strong>(.*)</strong></dd></dl>', html)
        if name:
            organisations[id]['name'] = name[0]

        # regex date announced: A1, C
        announceDate = re.findall(r'Bekannt gemacht am:</dt>\n<dd>(.*)</dd>', html)
        if announceDate:
            organisations[id]['date-announced'] = str(datetime.strptime(announceDate[0], '%d.%m.%Y'))

        # regex last update: A1, B, C
        lastUpdate = re.findall(r'Letzte .*nderung:</dt>\n<dd>(.*)</dd>', html)
        if lastUpdate:
            if organisations[id]['last-update'] != str(datetime.strptime(lastUpdate[0], '%d.%m.%Y')):
                print("ERROR: register last update differs!")

        # regex corporate-number: A1
        corporateNumber = re.findall(r'Firmenbuchnummer:</dt>\n<dd>(.*)</dd>', html)
        if corporateNumber:
            organisations[id]['corporate-number'] = corporateNumber[0]

        # regex registered office address: A1, C, D
        regOfficeAddress = re.findall(r'itz:</dt>\n<dd>(.*)</dd></dl>', html)
        if regOfficeAddress:
            organisations[id]['registered-office-address'] = regOfficeAddress[0]

        # regex mail address: A1, C, D
        mailAddress = re.findall(r'nschrift:</dt>\n<dd>(.*)</dd></dl>', html)
        if mailAddress:
            organisations[id]['mailing-address'] = mailAddress[0]

        # regex start business year: A1
        startBusinessYear = re.findall(r'ftsjahres:</dt>\n<dd>(.*)</dd></dl>', html)
        if startBusinessYear:
            organisations[id]['start-business-year'] = str(datetime.strptime(startBusinessYear[0], '%d.%m.'))

        # regex legal foundation: C
        legalFoundation = re.findall(r'Gesetzliche Grundlage:</dt>\n<dd>(.*)</dd></dl>', html)
        if legalFoundation:
            organisations[id]['legal-foundation'] = legalFoundation[0]

        # regex area of activities: A1, B, C, D
        areaActivities = re.findall(r'bereich:</dt>\n<dd>(.*)</dd></dl>', html)
        if areaActivities:
            organisations[id]['activities'] = areaActivities[0]

        # regex codex: A1
        codex = re.findall(r'Verhaltenskodex:</dt>\n<dd>(.*)</dd></dl>', html)
        if codex:
            organisations[id]['codex'] = codex[0]

        # regex website: A1, B, C, D
        website = re.findall(r'Homepage:</dt>\n<dd><a href="(.*)" target="_blank">.*</a></dd></dl>', html)
        if website:
            organisations[id]['website'] = website[0]

        # regex lobbyists: A1
        lobbyists = re.findall(r'obbyist:</dt>\n<dd>(.*)</dd></dl>', html)
        if lobbyists:
            organisations[id]['lobbyists'] = lobbyists[0].split('<br/>')

        # regex lobbying revenue: A1
        lobbyingRevenue = re.findall(r'Lobbying-Umsatz:</dt>\n<dd>(.*)</dd></dl>', html)
        if lobbyingRevenue:
            organisations[id]['lobbying-revenue'] = lobbyingRevenue[0]

        # regex lobbying request: A1
        lobbyingRequest = re.findall(r'<dt title="Anzahl der bearbeiteten Lobbying-Auftr.*ge:</dt>\n<dd>(.*)</dd></dl>', html)
        if lobbyingRequest:
            organisations[id]['lobbying-request'] = lobbyingRequest[0]

        # regex number of lobbyists: C, D
        numLobbyists = re.findall(r'Anzahl Interessenvertreter:</dt>\n<dd>(.*)</dd>', html)
        if numLobbyists:
            organisations[id]['number-lobbyists'] = numLobbyists[0]

        # regex costs lobbying: B, C
        costsB = re.findall(r'Lobbying-Aufwand > EUR 100.000:</dt>\n<dd>(.*)</dd>', html)
        costsC = re.findall(r'Kosten der Interessenvertretung:</dt>\n<dd>(.*)</dd>', html)
        if costsB:
            if costsB[0] == 'Ja':
                organisations[id]['costs-lobbying-greater-100000'] = True
            if costsB[0] == 'Nein':
                organisations[id]['costs-lobbying-greater-100000'] = False
        if costsC:
            organisations[id]['costs-lobbying'] = costsC[0]

        # regex atttachments: C
        attachment = re.findall(r'nge:</dt>\n<dd><a href="(.*)" .* target=_new>.*</a></dd>', html)
        if attachment:
            organisations[id]['pdf-attachment'] = BASE_URL + attachment[0]

        # regex suborganisations: C
        subOrganisations = re.findall(r'<dt>Unterorganisation.*</dt>\n<dd>(.*)</dd></dl>', html)
        if subOrganisations:
            organisations[id]['sub-organisations'] = subOrganisations[0]

    return organisations

###    MAIN   ###

if __name__ == '__main__':
    SetupEnvironment()
    ts = datetime.now().strftime('%Y-%m-%d-%H-%M')
    print(ts)
    # ts = '2015-05-05-00-14'
    htmlList = FetchHtmlList(QUERY_URL, ROOT_FOLDER+'/data/raw/'+ts, FILENAME_HTML) # list(html as text)
    htmlList = ReadFile(FOLDER_HTML+ts+'/'+FILENAME_HTML) # list(html as text)
    lobbyList = ParseList(htmlList) # dict(registry-number: dict(url, type, description, etc))
    Save2File(json.dumps(lobbyList, indent=2, ensure_ascii=False), FOLDER_JSON+ts+'_'+FILENAME_JSON)
    htmlOrgas = FetchHtmlOrganisations(lobbyList, ROOT_FOLDER+'/data/raw/'+ts) # dict(registry-number: html)
    htmlOrgas = ReadOrganisations(FOLDER_HTML+ts) # dict(registry-number: html)
    lobbyOrgas = ParseOrganisations(htmlOrgas, lobbyList)
    Save2File(json.dumps(lobbyOrgas, indent=2, ensure_ascii=False), FOLDER_JSON+ts+'_'+FILENAME_JSON)
    # scraperwiki.sqlite.save(unique_keys=['', ''], data=data)

