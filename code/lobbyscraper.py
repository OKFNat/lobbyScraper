#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
This is a scraper for the Austrian Lobbying-Register. It fetches the HTML, saves it locally
and converts the relevant data into a json file.
"""

import scraperwiki
import lxml.html
import re
from datetime import datetime, date, time
import json
import os

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
FILENAME_HTML = 'lobbyingregister.htm'
FILENAME_JSON = 'lobbyingregister.json'

###    FUNCTIONS   ###

def FetchHtmlList(url, folder, filename):
    """Fetches html from the overview list of the lobbyingregister entries and saves it locally.
    
    Args:
        url: url to fetch
        folder: to save the html
        filename: filename for the html file
    
    Returns:
        html string
    """
    rawHtml = scraperwiki.scrape(url)
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
        rawHtml = scraperwiki.scrape(organisation['url'])
        Save2File(rawHtml, folder+'/'+str(id)+'.htm')
        html[id] = rawHtml
    return html

def Save2File(data, filename):
    """Saves file locally
    
    Args:
        data: string to save
        filename: name of the file
    
    Returns:
        na
    """
    text_file = open(filename, "w")
    text_file.write(data)
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

def ParseList(html, timestamp):
    """Parses the needed facts out of the overview list html.
    
    Args:
        html: html string 
        timestamp: time when the html download was started.
    
    Returns:
        dict() of sequencial id's of organisations as key and dict() with facts as value.
    """
    lobbyList = {}
    counter = 0

    root = lxml.html.fromstring(html)

    # loop over table rows
    for tr in root.cssselect("tbody tr"):
        tds = tr.cssselect("td")
        
        # assign variables from html table to dict
        organisation = {}
        organisation['description'] =  tds[1].text_content()          # organisation
        organisation['registry-department'] =  tds[3].text_content()        # register department
        organisation['url'] =  BASE_URL+'/'+tds[2][0].get('href') # register number url
        organisation['last-update'] = str(datetime.strptime(tds[5].text_content(), '%d.%m.%Y')) # last update
        organisation['register-number'] = tds[2].text_content()
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
        # root = lxml.html.fromstring(html, encoding='unicode')
        root = lxml.html.fromstring(htmlList[id])
        html = lxml.etree.tostring(root)

        # regex type of registry department: B, C 
        regDepartment = re.findall(r'Registerabteilung:</strong></dt>\n<dd><strong>(.*)</strong></dd></dl>', html)
        if regDepartment:
            if organisations[id]['registry-department'] != regDepartment[0]:
                print "ERROR: register department differs!"

        # regex register number: B, C
        regNum = re.findall(r'Registerzahl:</strong></dt>\n<dd><strong>(.*)</strong></dd></dl>', html)
        if regNum:
            if organisations[id]['register-number'] != regNum[0]:
                print "ERROR: register number differs!"

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
                print "ERROR: register last update differs!"

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
            organisations[id]['mail-address'] = mailAddress[0]

        # regex start business year: A1
        startBusinessYear = re.findall(r'Beginn des Geschäftsjahres:</dt>\n<dd>(.*)</dd></dl>', html)
        if startBusinessYear:
            organisations[id]['start-business-year'] = str(datetime.strptime(startBusinessYear[0], '%d.%m'))

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
    ts = datetime.now().strftime('%Y-%m-%d-%H-%M')
    # ts = '2015-05-04-16-11'
    htmlList = FetchHtmlList(QUERY_URL, ROOT_FOLDER+'/data/raw/'+ts, FILENAME_HTML) # list(html as text)
    htmlList = ReadFile(ROOT_FOLDER+'/data/raw/'+ts+'/'+FILENAME_HTML) # list(html as text)
    lobbyList = ParseList(htmlList, ts) # dict(registry-number: dict(url, type, description, etc))
    Save2File(json.dumps(lobbyList, indent=2), ROOT_FOLDER+'/data/json/'+ts+'_'+FILENAME_JSON)
    htmlOrgas = FetchHtmlOrganisations(lobbyList, ROOT_FOLDER+'/data/raw/'+ts) # dict(registry-number: html)
    htmlOrgas = ReadOrganisations(ROOT_FOLDER+'/data/raw/'+ts) # dict(registry-number: html)
    lobbyOrgas = ParseOrganisations(htmlOrgas, lobbyList)
    Save2File(json.dumps(lobbyOrgas, indent=2), ROOT_FOLDER+'/data/json/'+ts+'_'+FILENAME_JSON)
    # scraperwiki.sqlite.save(unique_keys=['', ''], data=data)
