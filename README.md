# Oddsmatcher

Matching odds of betting exchanges (currently only Betfair) and bookmakers. 

This project mostly focusses on bookmakers that are interesting for Dutch matched betters. 

### Structure

The backend is written in python, while the frontend uses AJAX, thus making use of javascript and PHP. 

The information collected by the backend is inserted into a MYSQL database. All odds matching is done on the back end, such that the results load quickly when accessing the frontend.

### Running the project

The project is written for python 3.7, uncertain if betfairlightweight, or matchbook module work on higher python versions.

Add a file betfair_api_credentials.txt into the root directory like:

```
APPLICATION_KEY
BETFAIR_USERNAME
BETFAIR_PASSWORD
```

Create a bin folder and add the chromedirver binary here, named "chromedriver".

Run `./run.sh` on linux, on windows make sure you are in the home directory and run `py -3.7 src/main.py`

### Testing
As the backend is mostly a scraping job, unit tests don't help much. 

Bookmakers can change their website, or there might be a weird situation with football matches resulting in weird behaviour. 

To test parts of the software individually, the single scrapers can be ran on their own, by running `py -3.7 src/scraper_neobet.py` for example. 

A more robust testing solution should be implemented however, to make the process of finding bugs easier. 

