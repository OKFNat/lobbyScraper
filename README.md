Austrian Lobbyregister Scraper
=============================================================

The scraper extracts data from the [Austrian Lobbying Register](http://www.lobbyreg.justiz.gv.at), which must be reported since 2013. The data are stored in CSV and JSON files to make the further usage as easy as possible.

This repository provides the code and documentation and [keeps track of bugs as well as feature requests](https://github.com/OKFNat/lobbyScraper/issues).

- [Data Source](http://www.lobbyreg.justiz.gv.at/edikte/ir/iredi18.nsf/liste!OpenForm&subf=a)
- Team: [Gute Taten für gute Daten](http://okfn.at/gutedaten/) Project (Open Knowledge Austria)
- Status: Production
- Documentation: English
- License:
	- Content: [Creative Commons Attribution 4.0](http://creativecommons.org/licenses/by/4.0/)
	- Software: [MIT License](http://opensource.org/licenses/MIT) 

**Used software**

The sourcecode is written in Python 2. It was created with use of [iPython](http://ipython.org/), [BeautifulSoup4](http://www.crummy.com/software/BeautifulSoup/) and [urllib2](https://docs.python.org/2/library/urllib2.html).

## SCRAPER

**Description**

The scraper fetches the overview page with the table and parses out the data with beautifulsoup4. Then the scraper goes into every lobbying register entry via the Registerzahl-link, stores the html and parses out the rest of the data available via regular expressions. At the end, the data is stored as JSON and CSV files for easy usage later on.

**Run scraper**

Go into the root folder of this repository and execute following commands in your terminal:
```
cd code
python lobbyscraper.py
```

### How the scraper works

**Configure the Scraper**

There are two global variables in [lobbyscraper.py](code/lobbyscraper.py) you may want to change to your needs.

- DELAY_TIME: To not overload the server or may get blocked because of too many request, you should set the delay time to fetch to 1-5 seconds, not less.
- TS: The timestamp as a string can be set to the last download. So you can use downloaded data over and over again and must not do it everytime. When you do it first time, you can set the value to ```datetime.now().strftime('%Y-%m-%d-%H-%M')```, so it is the timestamp when the scraper starts.

**Download raw html**

Here all the html raw data gets downloaded, stored locally and the basic data gets parsed.

- Download the overview page with the tables (html).
- Open the downloaded file.
- Parse out the basic information about each lobbying register entry from the overview table. This is necessary here, because the download of the lobbying register entry page needs the link from the Registerzahl field.
- Store the parsed data as JSON file.
- Download all lobbying register entry pages (html) with the unique id as postfix.

**Parse html**

Here the description of the project gets added to the data.

- Open the overview page.
- Parse out the basic information about each lobbying register entry from the overview table. This is necessary here, because the download of the lobbying register entry page needs the link from the Registerzahl field.
- Open all lobbying register entry pages (html).
- Parse out the additional information from all lobbying register pages.
- Store updated data as JSON file.

The lobbying register does not publish the A2 entries, so the scraper never got tested with this and some A2 specific data entries are not part of the parser.

**Download attachments**

Here all attachments linked in the entry pages are stored locally.
- open JSON file.
- Download all attachments.

**Export CSV**

Here the data gets exported as a CSV file.
- Open the data (JSON).
- Save the serialized data as CSV file.

## DATA INPUT

The raw data is from the [Lobbying- und Interessenvertretungs-Register](http://www.lobbyreg.justiz.gv.at/edikte/ir/iredi18.nsf/liste!OpenForm&subf=a) of the austrian justice ministry. The data consists of all lobbying activities of
- lobbying companies
- corporations, who employ lobbyists in-house
- self-governing bodies and
- interest groups
since January 1st of 2013. 

More details about the register and it's data can be found [here](http://www.lobbyreg.justiz.gv.at/edikte/ex/edparm3.nsf/h/IR_Hinweise) und [hier](http://www.lobbyreg.justiz.gv.at/edikte/ex/edparm3.nsf/h/ir_Leitfaden/$file/Leitfaden.pdf).

### The Table

The table is the basic data, where most of the data is parsed out. The data is published in the following structure (e. g. first project).

**Example**

| Nr | Bezeichnung/Firma | Registerzahl | Registerabteilung | Details | Letzte Änderung |
|----|-------------------|--------------|-------------------|---------|-----------------|
| 2  | AbbVie GmbH, Wien, (378955m) | [LIVR-00054](http://www.lobbyreg.justiz.gv.at/edikte/ir/iredi18.nsf/alldoc/edea53b6f0f5a4b3c1257b3900548209!OpenDocument) | B | Mag. Thomas Haslinger<br/>Mag. Bettina Theresia Kölbl-Resl | 09.11.2015 |

**Attributes**
- Nr: sequential number for each row which is not connected directly with the entry itself.
- Bezeichnung/Firma (Description/Corporation): Name, company or description of company.
- Registerzahl (registry number): the 'Registerzahl' is no unique ID and is taken several times for different organisations, i. e. LIVR-00303 for [Österreichischer Apothekerverband](http://www.lobbyreg.justiz.gv.at/edikte/ir/iredi18.nsf/alldoc/2371c20cd6f70fa8c1257bad002ee3a1!OpenDocument) and [Aktienforum - Österreichischer Verband für Aktien-Emittenten und -Investoren](http://www.lobbyreg.justiz.gv.at/edikte/ir/iredi18.nsf/alldoc/a61a8fdfd0122b8cc1257bad002edfd6!OpenDocument) lobbying entry.
- Registerabteilung (type of lobbying organisations):
	- A1: Lobbying-Unternehmen bzw. Lobbyisten (Lobbying-corporations or lobbyists)  
	- A2: Aufgabenbereiche der Lobbying-Unternehmen (nicht öffentlich) (areas of activity of lobbying corporations (non-public))  
	- B: Unternehmen bzw. Unternehmens-/(In-House-)Lobbyisten (companies or company-/(in-house-)lobbyists)  
	- C: Selbstverwaltungskörper (self-governing bodies)  
	- D: Interessenverbände (interest groups)  
- Details: name(s) of lobbyist(s) if available.
- Letzte Änderung (last update)

### The lobbying entry pages
Additionally the scraper also takes data from the more detailed pages of each lobbying-register entry, depending on the register type listed at the end.

**Attributes**
- Bekannt gemacht am (announced at): we guess it is the date, when (A1, C)
- Name/Firma (name/company): (A1, B, C)
- Firmenbuchnummer (company register number): only valid austrian company register numbers. (A1, B)
- Firmensitz (register office): place of the register office (A1, C, D)
- Geschäftsanschrift (postal address): address for postal activities. (A1, C, D)
- Beginn des Geschäftsjahres (start of business year): in form of DD.MM. (A1, B)
- Gesetzliche Grundlage (legal foundation): legal foundation for founding of the self-governing body. (C)
- Tätigkeitsbereich (area of activity): short description of professional or business activities and/or the contractual or statuatory area of activity. (A1, B, D)
- Verhaltenskodex (code of conduct): (A1, B)
- Homepage (A1, B, C, D)
- Unternehmenslobbyist/en (corporate lobbyist/s): Lobbyists and/or in-house lobbyists with name (first name familyname) and birthday. One each line. (A1, B)
- Lobbying-Umsatz (lobbying revenue): revenue made through lobbying activities last business year. (A1)
- Anzahl der bearbeiteten Lobbying-Aufträge (number of lobbying orders): number of lobbying orders from last year. (A1) 
- Anzahl Interessenvertreter (number of lobbyists): full number of persons who where mostly lobbying in the last year. (C, D)
- Lobbying-Aufwand > EUR 100.000 (lobbying costs > 100.000€): were the expenses for the last business year were more than 100.000€. (B)
- Kosten der Interessenvertretung (costs of lobbying): from accountant or other statuatory or legal controll body confirmed costs from lobbying. (C, D)
- PDF-Anhänge (pdf attachments): link(s) to submited pdf-attachments. (C)
- Unterorganisationen (sub-organisations): one each line (C, D)
- Kommentar (comment): more detailed information for aggregated data entries. (C, D)

### Soundness
So far, we can not say much about the data quality (completeness, accuracy, etc.), but there are also no reasons to doubt the entries.

The lobbying register does not publish the A2 entries.

**Data errors found**
- Looks like the register number is sometimes wrong, cause it normally should be a unique number. (i. e. LIVR-00303 for [Österreichischer Apothekerverband](http://www.lobbyreg.justiz.gv.at/edikte/ir/iredi18.nsf/alldoc/2371c20cd6f70fa8c1257bad002ee3a1!OpenDocument) and [Aktienforum - Österreichischer Verband für Aktien-Emittenten und -Investoren](http://www.lobbyreg.justiz.gv.at/edikte/ir/iredi18.nsf/alldoc/a61a8fdfd0122b8cc1257bad002edfd6!OpenDocument))

## DATA OUTPUT

**raw html**

The scraper downloads all raw html of each lobbying register entry and the overview page.

**lobbying data JSON**

The parsed data is stored in an easy-to-read JSON file for further usage.
```
[
	{
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
	},
]
```

**lobbying data csv**

The parsed data is stored in a human-readable CSV file for further usage.

columns (see attribute description above):
- ID
- entryDescription
- orgaName
- businessActivities
- lobbyingOrgaType
- lobbyists
- lobbyingRevenue
- lobbyingRequests
- numLobbyists
- lobbyingCostsGreater100000
- lobbyingCosts
- registryNumber
- companyRegisterNumber
- suborganisations
- legalFoundation
- codeOfConduct
- registeredOffice
- website
- postalAddress
- lastUpdate
- dateAnnounced
- businessYearStart
- url
- attachmentUrls
- comment

row: one lobbying register entry each row.

## CONTRIBUTION
In the spirit of free software, everyone is encouraged to help improve this project.

Here are some ways you can contribute:

- by reporting bugs
- by suggesting new features
- by translating to a new language
- by writing or editing documentation
- by analyzing the data
- by visualizing the data
- by writing code (**no pull request is too small**: fix typos in the user interface, add code comments, clean up inconsistent whitespace)
- by refactoring code
- by closing issues
- by reviewing pull requests
- by enriching the data with other data sources

When you are ready, submit a [pull request](https://github.com/OKFNat/lobbyscraper/pulls).

### Submitting an Issue

We use the [GitHub issue tracker](https://github.com/OKFNat/lobbyscraper/issues) to track bugs and features. Before submitting a bug report or feature request, check to make sure it hasn't already been submitted. When submitting a bug report, please try to provide a screenshot that demonstrates the problem. 

## COPYRIGHT
All content is openly licensed under the [Creative Commons Attribution 4.0](http://creativecommons.org/licenses/by/4.0/) license, unless otherwisely stated.

All sourcecode is free software: you can redistribute it and/or modify it under the terms of the MIT License.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

Visit [http://opensource.org/licenses/MIT](http://opensource.org/licenses/MIT) to learn more about the MIT License.

## SOURCES

**Gute Taten für gute Daten**
- [Gute Taten für gute Daten](http://okfn.at/gutedaten/)

**Lobbying**
- [Transparency International Austria](https://www.ti-austria.at/): Austrian Chapter of Transparency International.
- [Lobbying in Austria](https://www.ti-austria.at/wp-content/uploads/2016/01/Lobbying-in-Austria.pdf): Publikation von Transparency International Austria

**Documentation**
- [Original Data Source](http://www.lobbyreg.justiz.gv.at/edikte/ir/iredi18.nsf/liste!OpenForm&subf=a)
- [Hinweise zum Lobbyisten und Interessenvertretungsregister](http://www.lobbyreg.justiz.gv.at/edikte/ex/edparm3.nsf/h/IR_Hinweise)
- [Leitfaden Lobbying- und Interessenvertretungsregister Erfassungsanwendung](http://www.lobbyreg.justiz.gv.at/edikte/ex/edparm3.nsf/h/ir_Leitfaden/$file/Leitfaden.pdf).

## REPOSITORY
- [README.md](README.md): Overview of repository
- [lobbyscraper.py](code/lobbyscraper.py): the scraper
- [CHANGELOG.md](CHANGELOG.md)
- [LICENSE](LICENSE)

## CHANGELOG
See the [whole history](CHANGELOG.md). Next the actual version.

### Version 0.2: 2016-04-26
- update documentation: commenting code, update README.md
- add csv export
- re-factor code
- add attachment download
- add SQLite export



