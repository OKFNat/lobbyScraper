#!/bin/env python3
# -*- coding: utf-8 -*-

"""
This is a scraper for the Austrian Lobbying-Register. It fetches the HTML, saves it locally
and converts the relevant data into a json file.
"""

import re
from datetime import datetime, date
import time
import json
import os
import urllib.request
from bs4 import BeautifulSoup
#import dataset

__author__ = "Stefan Kasberger"
__copyright__ = "Copyright 2015"
__license__ = "MIT"
__version__ = "0.3"
__maintainer__ = "Stefan Kasberger"
__email__ = "mail@stefankasberger.at"
__status__ = "Production" # 'Development', 'Production' or 'Prototype'

###    GLOBAL   ###

ROOT_FOLDER = os.path.dirname(os.getcwd())
FOLDER_RAW_HTML = ROOT_FOLDER + '/data/raw/html/'
FOLDER_RAW_PDF = ROOT_FOLDER + '/data/raw/pdf/'
FOLDER_JSON = ROOT_FOLDER + '/data/json/'
FOLDER_CSV = ROOT_FOLDER + '/data/csv/'
FILENAME_BASE = 'lobbyingregister'
BASE_URL = 'http://www.lobbyreg.justiz.gv.at/edikte/ir/iredi18.nsf'
BASE_URL_ATTACHMENTS = 'http://www.lobbyreg.justiz.gv.at'
QUERY_URL = BASE_URL+'/liste!OpenForm&subf=a'
DELAY_TIME = 2 # in seconds
# TS = datetime.now().strftime('%Y-%m-%d-%H-%M')
TS = '2017-07-13-21-47'

###    FUNCTIONS   ###

def SetupEnvironment():
    """Sets up the folder structure and working environment.
    """
    if not os.path.exists(FOLDER_RAW_HTML):
        os.makedirs(FOLDER_RAW_HTML)
    if not os.path.exists(FOLDER_RAW_PDF):
        os.makedirs(FOLDER_RAW_PDF)
    if not os.path.exists(FOLDER_JSON):
        os.makedirs(FOLDER_JSON)
    if not os.path.exists(FOLDER_CSV):
        os.makedirs(FOLDER_CSV)

def FetchHtml(url):
    """Fetches html from the url
    
    Args:
        url: url to fetch (string).
    
    Returns:
        html: html string
    """
    time.sleep(DELAY_TIME)
    response = urllib.request.urlopen(url)
    html = response.read()
    
    return html

def FetchHtmlOverview(url, folder):
    """Fetches html from the overview list of the lobbyingregister entries and saves it locally.
    
    Args:
        url: url to fetch (string).
        folder: directory to save the html files in.    
    """
    rawHtml = FetchHtml(url)

    if not os.path.exists(folder):
        os.makedirs(folder)
    Save2File(rawHtml.decode(), folder+'/overview-page.html')

def FetchHtmlEntries(entries, folder):
    """Fetches html from an entry in the table and saves it locally with the unique id as postfix.
    
    Args:
        entries: list with sequencial dict() of organisations.
        folder: to save the html in.
    """
    for entry in entries:
        html = FetchHtml(entry['url'])
        Save2File(html.decode(), folder+'/entry-'+str(entry['ID'])+'.html')

def Save2File(data, filename):
    """Saves data on specified place on harddrive.
    
    Args:
        data: string to save.
        filename: string of the filepath.
    """
    try:
        text_file = open(filename, "w")
        text_file.write(data)
        text_file.close()
    except:
        print('Error writing', filename)
        return False

def ReadFile(filename):
    """Reads file and returns the text.
    
    Args:
        filename: name of the file
    
    Returns:
        string: content of file as string
    """
    f = open(filename, 'r')
    string = f.read()

    return string

def ReadEntryFilesInFolder(folder):
    """Reads-in all entry html-files from specified folder.
    
    Args:
        folder: folder where the html-files are stored in.
    
    Returns:
        sortedList: list[] of html texts sorted by file-postfix, which is the unique id of the entry from the table.
    """
    htmlList = []
    sortedList = []

    for filename in os.listdir(folder):
        if filename.find('entry-') >= 0:
            rawHtml = ReadFile(folder+'/'+filename)
            fileIndex = filename.split('.')[0].split('-')[1]
            htmlList.append((int(fileIndex), rawHtml))
    
    # sort list of duppels after first element (the filename postfix) and store to list[]
    htmlList = sorted(htmlList, key=lambda htmlList: htmlList[0])
    for idx, html in htmlList:
        sortedList.append(html)

    return sortedList

def ParseTable(html):
    """Parses the needed facts out of the overview table.
    
    Args:
        html: html (string) to parse. 
    
    Returns:
        list[] of dict() of entries.
            'ID': serial number created from scraper when parsing through the table rows.
            'entryDescription': description of the entry.
            'lobbyingOrgaType': type of lobbying organisation (A1, A2, B, C, D).
            'url': url of the detail page.
            'lastUpdate': last update of detail page.
            'registryNumber': number of company in lobbying-register.
    """
    lobbyList = []
    counter = 1

    soup = BeautifulSoup(html, 'html.parser')
    
    # loop over table rows
    for tr in soup.tbody.find_all('tr'):
        tds = tr.find_all('td')

        # assign variables from html table to dict
        entry = {}
        entry['ID'] =  str(counter)
        entry['entryDescription'] =  tds[1].string
        entry['lobbyingOrgaType'] =  tds[3].string
        entry['url'] =  BASE_URL+'/'+tds[2].a['href']
        entry['lastUpdate'] = str(datetime.strptime(tds[5].string, '%d.%m.%Y'))
        entry['registryNumber'] = tds[2].string
        
        lobbyList.append(entry)
        counter += 1

    return lobbyList

def ParseEntries(htmlList, entries):
    """Parses the needed facts out of the organisation html.
    
    Args:
        htmlList: list() of html strings.
        entries: list() of dict() of entries.
    
    Returns:
        list[] of dict() of entries.
            'ID': serial number created from scraper when parsing through the table rows.
            'entryDescription': description of the entry.
            'lobbyingOrgaType': type of lobbying organisation (A1, A2, B, C, D).
            'url': url of the detail page.
            'lastUpdate': last update of detail page.
            'registryNumber': number of company in lobbying-register.
            'orgaName': name of organisation.
            'companyRegisterNumber': number of the national company register.
            'businessActivities': area in which the organisation is active in business.
            'postalAddress': postal address.
            'registeredOffice': Place, where the company is officially registered.
            'businessYearStart': Day, when the business year starts.
            'legalFoundation': 
            'codeOfConduct': Code of conduct.
            'website': url of the website
            'lobbyists': list of lobbyists.
            'lobbyingRevenue': Revenue from lobbying.
            'lobbyingRequests': Number of lobbying requests.
            'numLobbyists': Number of lobbyists.
            'lobbyingCostsGreater100000': 
            'lobbyingCosts': Costs of lobbying.
            'suborganisations': List of suborganisations.
            'attachmentUrls': url to an attachment.
            'comment': comment to precise other fields.
    """
    entriesList = []

    for entry in entries:
        soup = BeautifulSoup(htmlList[int(entry['ID'])-1], "html.parser")
        html = str(soup)
       
        # regex testing type of registry department: B, C 
        regDepartment = re.findall(r'Registerabteilung:</strong></dt>\n<dd><strong>(.*)</strong></dd></dl>', html)
        if regDepartment:
            if entry['lobbyingOrgaType'] != regDepartment[0]:
                print('ERROR: lobbying organisation type differs!')

        # regex testing register number: B, C
        regNum = re.findall(r'Registerzahl:</strong></dt>\n<dd><strong>(.*)</strong></dd></dl>', html)
        if regNum:
            if entry['registryNumber'] != regNum[0]:
                print('ERROR: company register number differs!')

        # regex name: A1, B, C
        name = re.findall(r'Name.*:</strong></dt>\n<dd><strong>(.*)</strong></dd></dl>', html)
        if name:
            entry['orgaName'] = name[0]

        # regex date announced: A1, C
        announceDate = re.findall(r'Bekannt gemacht am:</dt>\n<dd>(.*)</dd>', html)
        if announceDate:
            entry['dateAnnounced'] = str(datetime.strptime(announceDate[0], '%d.%m.%Y'))

        # regex testing last update: A1, B, C
        lastUpdate = re.findall(r'Letzte .*nderung:</dt>\n<dd>(.*)</dd>', html)
        if lastUpdate:
            if entry['lastUpdate'] != str(datetime.strptime(lastUpdate[0], '%d.%m.%Y')):
                print("ERROR: register last update differs!")

        # regex corporate-number: A1, B
        corporateNumber = re.findall(r'Firmenbuchnummer:</dt>\n<dd>(.*)</dd>', html)
        if corporateNumber:
            entry['companyRegisterNumber'] = corporateNumber[0]

        # regex registered office address: A1, C, D
        regOfficeAddress = re.findall(r'itz:</dt>\n<dd>(.*)</dd></dl>', html)
        if regOfficeAddress:
            entry['registeredOffice'] = regOfficeAddress[0]

        # regex mail address: A1, C, D
        postalAddress = re.findall(r'nschrift:</dt>\n<dd>(.*)</dd></dl>', html)
        if postalAddress:
            entry['postalAddress'] = postalAddress[0]

        # regex start business year: A1, B
        startBusinessYear = re.findall(r'ftsjahres:</dt>\n<dd>(.*)</dd></dl>', html)
        if startBusinessYear:
            entry['businessYearStart'] = startBusinessYear[0]

        # regex legal foundation: C
        legalFoundation = re.findall(r'Gesetzliche Grundlage:</dt>\n<dd>(.*)</dd></dl>', html)
        if legalFoundation:
            entry['legalFoundation'] = legalFoundation[0]

        # regex area of activities: A1, B, D
        areaActivities = re.findall(r'bereich:</dt>\n<dd>(.*)</dd></dl>', html)
        if areaActivities:
            entry['businessActivities'] = areaActivities[0]

        # regex codex: A1, B
        codex = re.findall(r'Verhaltenskodex:</dt>\n<dd>(.*)</dd></dl>', html)
        if codex:
            entry['codeOfConduct'] = codex[0]

        # regex website: A1, B, C, D
        website = re.findall(r'Homepage:</dt>\n<dd><a href="(.*)" target="_blank">.*</a></dd></dl>', html)
        if website:
            entry['website'] = website[0]

        # regex lobbyists: A1
        lobbyists = re.findall(r'obbyist.*:</dt>\n<dd>(.*)</dd></dl>', html)
        if lobbyists:
            entry['lobbyists'] = lobbyists[0].split('<br/>')

        # regex lobbying revenue: A1, B
        lobbyingRevenue = re.findall(r'Lobbying-Umsatz:</dt>\n<dd>(.*)</dd></dl>', html)
        if lobbyingRevenue:
            entry['lobbyingRevenue'] = lobbyingRevenue[0]

        # regex lobbying request: A1
        lobbyingRequest = re.findall(r'<dt title="Anzahl der bearbeiteten Lobbying-Auftr.*ge:</dt>\n<dd>(.*)</dd></dl>', html)
        if lobbyingRequest:
            entry['lobbyingRequests'] = lobbyingRequest[0]

        # regex number of lobbyists: C, D
        numLobbyists = re.findall(r'Anzahl Interessenvertreter:</dt>\n<dd>(.*)</dd>', html)
        if numLobbyists:
            entry['numLobbyists'] = numLobbyists[0]

        # regex costs lobbying: B
        costsB = re.findall(r'Lobbying-Aufwand > EUR 100.000:</dt>\n<dd>(.*)</dd>', html)
        if costsB:
            if costsB[0] == 'Ja':
                entry['lobbyingCostsGreater100000'] = True
            if costsB[0] == 'Nein':
                entry['lobbyingCostsGreater100000'] = False
        # regex costs lobbying: C, D
        costsC = re.findall(r'Kosten der Interessenvertretung:</dt>\n<dd>(.*)</dd>', html)
        if costsC:
            entry['lobbyingCosts'] = costsC[0]

        # regex atttachments: C
        attDiv = soup.find(id='UplDL')
        if attDiv:
            entry['attachmentUrlss'] = []
            for link in attDiv.find_all('a'):
                entry['attachmentUrlss'].append(BASE_URL_ATTACHMENTS + link.get('href'))

        # regex subentries: C, D
        subOrganisations = re.findall(r'<dt>Unterorganisation.*</dt>\n<dd>(.*)</dd></dl>', html)
        if subOrganisations:
            entry['suborganisations'] = subOrganisations[0]

        # regex comment: C, D
        comment = re.findall(r'<dt>Kommentar:</dt>\n<dd>(.*)</dd></dl>', html)
        if comment:
            entry['comment'] = comment[0]

        entriesList.append(entry)

    return entriesList

def Save2CSV(entries, filename):
    """Exports the dict into a csv file.
    
    Args:
        entries: list of dict() with all the lobbying register entries.
        filename: name of the file with folder.
    """
    csvString = '"ID","entryDescription","orgaName","businessActivities","lobbyingOrgaType","lobbyists","lobbyingRevenue","lobbyingRequests","numLobbyists","lobbyingCostsGreater100000","lobbyingCosts","registryNumber","companyRegisterNumber","suborganisations","legalFoundation","codeOfConduct","registeredOffice","website","postalAddress","lastUpdate","dateAnnounced","businessYearStart","url","attachmentUrls","comment"\n'

    # iterate over each entry
    for entry in entries:
        uniqueId = '""'
        entryDescription = '""'
        orgaName = '""'
        busActivities = '""'
        lobOrgaType = '""'
        lobbyists = '""'
        lobbyingRevenue = '""'
        lobbyingRequest = '""'
        numLobbyists = '""'
        costsB = '""'
        costsC = '""'
        regNum = '""'
        compRegNumber = '""'
        subOrganisations = '""'
        legalFoundation = '""'
        codex = '""'
        regOfficeAddress = '""'
        lastUpdate = '""'
        website = '""'
        postalAddress = '""'
        lastUpdate = '""'
        announceDate = '""'
        startBusinessYear = '""'
        url = '""'
        attachments = '""'
        comment = '""'

        # read out each attribute
        for elem in list(entry.keys()):
            val = entry[elem]
            if elem == 'ID':
                uniqueId = '"'+val+'"'
            if elem == 'entryDescription':
                entryDescription = '"'+val+'"'
            if elem == 'orgaName':
                orgaName = '"'+val+'"'
            if elem == 'businessActivities':
                busActivities = '"'+val.replace('"', '').replace('\n', '').replace('\r', '')+'"'
            if elem == 'lobbyingOrgaType':
                lobOrgaType = '"'+val+'"'
            if elem == 'lobbyists':
                lobbyists = '"'
                for lob in val:
                    lobbyists += lob+', '
                lobbyists = lobbyists[:-1]
                lobbyists += '"'
            if elem == 'lobbyingRevenue':
                lobbyingRevenue = '"'+val+'"'
            if elem == 'lobbyingRequests':
                lobbyingRequest = '"'+val+'"'
            if elem == 'numLobbyists':
                numLobbyists = '"'+val+'"'
            if elem == 'lobbyingCostsGreater100000':
                costsB = '"'+val+'"'
            if elem == 'lobbyingCosts':
                costsC = '"'+val+'"'
            if elem == 'registryNumber':
                regNum = '"'+val+'"'
            if elem == 'companyRegisterNumber':
                compRegNumber = '"'+val+'"'
            if elem == 'suborganisations':
                subOrganisations = '"'+val+'"'
            if elem == 'legalFoundation':
                legalFoundation = '"'+val+'"'
            if elem == 'codeOfConduct':
                codex = '"'+val.replace('"', '').replace('\n', '').replace('\r', '')+'"'
            if elem == 'registeredOffice':
                regOfficeAddress = '"'+val+'"'
            if elem == 'website':
                website = '"'+val+'"'
            if elem == 'postalAddress':
                postalAddress = '"'+val+'"'
            if elem == 'lastUpdate':
                lastUpdate = '"'+val+'"'
            if elem == 'dateAnnounced':
                announceDate = '"'+val+'"'
            if elem == 'businessYearStart':
                startBusinessYear = '"'+val+'"'
            if elem == 'url':
                url = '"'+val+'"'
            if elem == 'attachmentUrlss':
                attachments = '"'
                for att in val:
                    attachments += att+', '
                attachments +='"'
            if elem == 'comment':
                comment = '"'+val+'"'

        csvString += uniqueId+','+entryDescription+','+orgaName+','+busActivities+','+lobOrgaType+','+lobbyists+','+lobbyingRevenue+','+lobbyingRequest+','+numLobbyists+','+costsB+','+costsC+','+regNum+','+compRegNumber+','+subOrganisations+','+legalFoundation+','+codex+','+regOfficeAddress+','+website+','+postalAddress+','+lastUpdate+','+announceDate+','+startBusinessYear+','+url+','+attachments+','+comment+'\n'

    Save2File(csvString, filename)
    print('Lobbying data exported as CSV:',filename)

def FetchAttachments(entries, folder):
    """Fetches all attachments from the lobbying-register entries.
    
    Args:
        entries: list[] of dict() with all the lobbying-register data.
        folder: directory, where the files are stored in.
    """
    for entry in entries:
        if 'attachmentUrls' in list(entry.keys()):
            for url in entry['attachmentUrls']:
                DownloadFile(url, folder+'/attachment-'+entry['ID']+'_'+url.split('/')[-1])

def DownloadFile(url, filename):
    """Downloads and stores an attachment.
    
    Args:
        url: url of the attachment (string).
        filename: full filepath for the saving.
    """
    if not os.path.exists(os.path.dirname(os.path.abspath(filename))):
        os.makedirs(os.path.dirname(os.path.abspath(filename)))
    response = urllib.request.urlopen(url)
    file = open(filename, 'w')
    file.write(response.read())
    file.close()
    time.sleep(DELAY_TIME)

#def Save2SQLite(lobbyEntries):
    """Saves the lobbing register entries in a SQLite database. This is not working, because of key-value issues of the dicts().
    
    Args:
        lobbyEntries: list[] of dicts() with lobbying register entries.
    """
    #db = dataset.connect('sqlite:///:memory:')
    #table = db['lobbyRegisterAT']
    #for entry in lobbyEntries:
    #    print entry
    #    table.insert(entry)

    # Wien = table.find_one(registeredOffice='Wien')
    # print Wien

###    MAIN   ###

if __name__ == '__main__':
    
    # setup
    startTime = datetime.now()
    print('start:', startTime)
    SetupEnvironment()
    DOWNLOAD_FILES = False
    PARSE_FILES = False
    DOWNLOAD_ATTACHMENTS = False
    EXPORT_DATA = True
 
    if DOWNLOAD_FILES:
        FetchHtmlOverview(QUERY_URL, FOLDER_RAW_HTML+TS) 
        htmlOverview = ReadFile(FOLDER_RAW_HTML+TS+'/overview-page.html')
        lobbyList = ParseTable(htmlOverview) 
        Save2File(json.dumps(lobbyList, indent=2, sort_keys=True), FOLDER_JSON+TS+'_'+FILENAME_BASE+'.json')
        FetchHtmlEntries(lobbyList, FOLDER_RAW_HTML+TS) 
 
    if PARSE_FILES:
        htmlOverview = ReadFile(FOLDER_RAW_HTML+TS+'/overview-page.html')
        lobbyList = ParseTable(htmlOverview) 
        #lobbyList = lobbyList[:4]
        htmlEntries = ReadEntryFilesInFolder(FOLDER_RAW_HTML+TS) 
        #htmlEntries = htmlEntries[:4]
        lobbyEntries = ParseEntries(htmlEntries, lobbyList)
        Save2File(json.dumps(lobbyEntries, indent=2, sort_keys=True), FOLDER_JSON+TS+'_'+FILENAME_BASE+'.json')
    
    if DOWNLOAD_ATTACHMENTS:    
        lobbyEntries = ReadFile(FOLDER_JSON+TS+'_'+FILENAME_BASE+'.json')
        FetchAttachments(lobbyEntries, FOLDER_RAW_PDF+TS)
 
    if EXPORT_DATA:
        lobbyEntries = json.loads(ReadFile(FOLDER_JSON+TS+'_'+FILENAME_BASE+'.json'))
        Save2CSV(lobbyEntries, FOLDER_CSV+TS+'_'+FILENAME_BASE+'.csv')
        # Save2SQLite(lobbyEntries) # does not run!

    print('runtime:', (datetime.now() - startTime))

