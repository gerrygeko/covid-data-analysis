# 4.0.11
#### Updated
* Data update according to the new standards of data providers

# 4.0.10
#### Updated
* Introduce performance improvements that speed up the loading of the page

#### Changed
* Http traffic is always redirect to Https from now on

# 4.0.9
#### Updated
* Python has been upgraded from version 3.7 to version 3.10 bringing in updates and security fixes

#### Changed
* Changed name of the application from "SARS-CoV-2-Gellex" to "Coronavirus Data" to describe better the purpose of the website

#### Added
* Added support for MacOS, Android and Windows platforms. Option to save the link from the browser to your home screen, now gives an app-like experience when accessed
* It is possible to check the number of unique visitors to the platform. The new text is located at the footer of the webpage

# 4.0.8
#### Fixed
* The chart of administrations by age is back online
#### Changed
* Changed the calculation of the target of 90% of possible vaccinations. 
The number of days needed to reach the desired information, in line with current government target, is made by the division between the number of doses remaining to be administered and 
the average number (7-day rolling average) of first, second, single-dose, and prior infections each day
#### Updated
* Updated the information of total of vaccinated people and percentage cards
#### Added
* Added more infos on administration chart about administrated vaccines grouped by suppliers

# 4.0.7
#### Added
* Additional doses group chart (grouped by age)
#### Changed
* Calculation of the series shown in the administrated vaccines chart
* Target of Italian vaccination campain is now focused on 90% of vaccinable population 
*N.B.The vaccinable Italian population is represented by the over 12s. The audience (~ 54 million people) is based on 
the data of the holders of health cards or health certificates such as the "foreigners temporarily present" card 
recognized to irregular migrants*

# 4.0.6
#### Added
* "Buy Me a coffee" button- Support the project :)

# 4.0.5
#### Changed
* Updated the italian population according to the latest ISTAT updates

# 4.0.4
#### Fixed
* Removed field "categories" from vaccines charts since is not contained anymore in the open data used for this project

# 4.0.3
#### Changed
* Updated categories showed in the vaccines charts (grouped by age)

#### Fixed
* Fixed a bug showing an incorrect herd immunity prediction

# 4.0.2
#### Changed
* Changed the strategy to predict Herd Immunity Date; now the calculation takes into account the daily administrations and not exclusively the number of second doses

# 4.0.1
#### Fixed
* Fixed a bug in the italian cards which not show the correct color control for Pressure ICU and Positive/Swabs Ratio

#### Added
* "#datiBeneComune" references in the Credits section
* Copyright

# 4.0.0
#### Added
* Italy Vaccines Tab: the web application now shows italian data about Vaccination Campaign report.
    * Data Cards Italy: administered doses, delivered doses, total people vaccinated, percentage vaccinated population
    * Daily vaccinated people (presumed date of attainment of herd immunity)
    * Daily administrations
    * Administrations by age
    * Regional Data

# 3.0.6
#### Fixed
* Update of URL World Data repository to make a correct loading of the data starting from January 1, 2021

# 3.0.5
#### Fixed
* Replaced "googletrans" lib with "pygoogletranslation" to resolve issues caused by some changes on the 
  Google Translation API

# 3.0.4
#### Added
* Introduced card that shows the pressure in the ICU also in the regional tab

#### Fixed
* Fixed a bug in the translation library that was preventing the website to be available

# 3.0.3
#### Added
* Italy Tab: 2 new cards are now available:
    * ratio new positives / new swabs
    * ICU pressure

# 3.0.2
#### Fixed
* Fixed a bug that in specific cases, did not perform a correct association of nations to available population

# 3.0.1
#### Added
* DataHub references in the Credits section.

#### Changed
* Last update label now shows also the source of data

# 3.0.0
#### Added
* Worldwide Tab: the web application now shows worldwide data from all 188 countries that release Covid-19 related reports
    the following components show the updated data through the selection of the data of interest to the user:
    * Total Data Cards: show the official total world data;
    * Data Line Chart: shows the trend of the selected data;
    * Data Table: shows, in order of value importance, the ranking of countries;
    * Multiple Line Chart: allows you to compare the trend of the selected data from different countries;
    * Country Data Cards: show the official data released by the various countries of the world;
#### Changed 
* Italy Tab is now in line with World Tab layout

# 2.0.2
#### Changed
* Improvement of application layout
* Update of Italian Population Data by ISTAT (last official update 01/01/2020)

# 2.0.1
#### Fixed
* Fixed a bug that in specific cases, did not perform a correct translation

# 2.0.0
#### Added
* Localization is now available and the following languages are supported:
    * Italian
    * English
    * French
    * German
    * Spanish
    * Dutch
    * Portoguese 
#### Fixed
* Improved (mobile) navigation while scrolling through the different graphs 

# 1.1.2
#### Changed
* Display details of regions in the bar graphs with better format
* Hovering on any point of the main graph, will display information collected in the same window 
for all the regions selected instead of just displaying information of a single region
#### Added
* ICU and Swabs National Data Cards
#### Fixed
* Updates for new data showed in the graphs is more reliable

# 1.1.1
#### Changed
* National Data Cards has been removed from tabs component and the layout has been optimized for mobile view
* Italian map now shows the different brackets in different shades of blue
#### Fixed
* The data visualization of Max/Average Regional Cards has been made clearer

# 1.1.0
#### Changed
* The layout has been streamlined and optimized
* The second tab component has been converted to shows Regional data analysis
#### Added
##### National data analysis Tab
* Table to show data details for each region 
##### Regional data analysis Tab
* Data Cards for each region
* Mean and Max New positives Cards
* Active Cases Graph by region

# 1.0.7
#### Changed
* Bar Graph shows the raw data updated to the current day, no longer the rate calculated on the population
* The position of the map and bar chart has been reversed to optimize understanding of data in mobile view

# 1.0.6
#### Added
* National data cards and map now support Italian data format
#### Changed
* "Nuovi Positivi" is now the default data for data selection 
* Multi-region selection shows the "Nuovi Positivi" Top 3 Regions
* All components depend now on the same data selection

# 1.0.5
#### Fixed
* News feed time is now displayed in CET format timezone instead of UTC

# 1.0.4
#### Changed
* Color control on the four national data cards now only acts on the variation data text

# 1.0.3
#### Added
* Color control on the four national data cards, based on the trend of the last update (green for positive data trends,
red for negatives)

# 1.0.2
#### Fixed
* P.A. Bolzano and P.A. Trento are showed as Trentino-Alto Adige from now on map and bar graph in order to conform with 
the source of data used by this project 

# 1.0.1
#### Fixed
* Fix visualization bug in Contatti frame on mobile versions
#### Added
* New icons, in Contatti frame, that redirect the user to LinkedIn profile and to the personal email

# 1.0.0
* Release version
