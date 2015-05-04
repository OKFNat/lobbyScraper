Scraper Lobbyingregister AT
==============================

This repository is a python script to scrape the [Austrian Lobbyingregister](http://www.lobbyreg.justiz.gv.at). The scraper was written as part of the [Gute Taten für gute Daten](http://okfn.at/gutedaten/) project from [Open Knowledge Austria](http://okfn.at) and is licensed under [MIT](http://opensource.org/licenses/MIT).

This repository provides the [issue tracker](https://github.com/GSA/data.gov/issues) for all code, bugs, and feature requests related to this project.

## DOCUMENTATION
Some information about the Austrian Lobbyingregister. 

### Lobbyingregister
**Types of lobbying organisations**
A1 			Lobbying-corporations or lobbyisten (Lobbying-Unternehmen bzw. Lobbyisten)
A2 			Areas of activity of lobbying corporations (not public) (Aufgabenbereiche der Lobbying-Unternehmen (nicht öffentlich))
B 			Corporations or company-/(In-House-)lobbyists (Unternehmen bzw. Unternehmens-/(In-House-)Lobbyisten)
C 			self-governing bodies (Selbstverwaltungskörper)
D 			Interest groups (Interessenverbände)

- The 'Registerzahl' is no unique ID and is taken several times for different organisations, i. e. LIVR-00303 for [Österreichischer Apothekerverband](http://www.lobbyreg.justiz.gv.at/edikte/ir/iredi18.nsf/alldoc/2371c20cd6f70fa8c1257bad002ee3a1!OpenDocument) and [Aktienforum - Österreichischer Verband für Aktien-Emittenten und -Investoren](http://www.lobbyreg.justiz.gv.at/edikte/ir/iredi18.nsf/alldoc/a61a8fdfd0122b8cc1257bad002edfd6!OpenDocument)

### Scraper
- Python with scraperwiki and [lxml](http://lxml.de/lxmlhtml.html) modules.

To run the [python script](code/lobbyscraper.py), just enter this in the terminal when you are in the root folder of the repository. 
```
cd code
python lobbyscraper.py
```
To ease the server, you should download the html files just once and then work locally. To do this, just uncomment in the main section the lines with the ```FetchHtmlList()``` and ```FetchHtmlOrganisations()``` call and change the ts variable to the name of the directory with the downloaded html-files.

**computational chain**
1. Fetch the website and store the html locally
	- pack files after download into tar-ball and delete html-files.
2. Extract facts from html and store it in a json-file 
2. Compare actual data with past one data
3. update past one to the new state

## Contribution
In the spirit of free software, everyone is encouraged to help improve this project.

Here are some ways you can contribute:

- by reporting bugs
- by suggesting new features
- by translating to a new language
- by writing or editing documentation
- by visualizing the data
- by writing code (**no pull request is too small**: fix typos in the user interface, add code comments, clean up inconsistent whitespace)
- by refactoring code
- by closing issues
- by reviewing pull requests
- by enriching the data with other data sources

When you are ready, submit a [pull request](https://github.com/okfnat/scraper_lobbyingregister/pulls).

##Submitting an Issue

We use the [GitHub issue tracker](https://github.com/okfnat/scraper_lobbyingregister/issues) to track bugs and features. Before submitting a bug report or feature request, check to make sure it hasn't already been submitted. When submitting a bug report, please try to provide a screenshot that demonstrates the problem. 

## License

This program is free software: you can redistribute it and/or modify it under the terms of the MIT License.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

Visit http://opensource.org/licenses/MIT to learn more about the MIT License.

## STRUCTURE
- [README.md](README.md): Overview of repository

## STRUCTURE
- [python script](code/lobbyscraper.py)
- [html-example](html-example.md)
- [CHANGELOG](CHANGELOG.md)
- [LICENSE](LICENSE)
