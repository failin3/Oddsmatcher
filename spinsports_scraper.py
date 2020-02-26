from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from time import sleep
import re
import json

import time

from bs4 import BeautifulSoup

start_time = time.time()

class Game:
    def __init__(self, name, odds):
        self.name = name
        self.odds = odds
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

def sortOdds(odds, scores):
    odds_sorted = [None]*16
    for odd, score  in zip(odds, scores):
        if score == "0:0":
            odds_sorted[0] = odd
        if score == "1:0":
            odds_sorted[1] = odd
        if score == "1:1":
            odds_sorted[2] = odd
        if score == "0:1":
            odds_sorted[3] = odd
        if score == "2:0":
            odds_sorted[4] = odd
        if score == "2:1":
            odds_sorted[5] = odd
        if score == "2:2":
            odds_sorted[6] = odd
        if score == "1:2":
            odds_sorted[7] = odd
        if score == "0:2":
            odds_sorted[8] = odd
        if score == "3:0":
            odds_sorted[9] = odd
        if score == "3:1":
            odds_sorted[10] = odd
        if score == "3:2":
            odds_sorted[11] = odd
        if score == "3:3":
            odds_sorted[12] = odd
        if score == "2:3":
            odds_sorted[13] = odd
        if score == "1:3":
            odds_sorted[14] = odd
        if score == "0:3":
            odds_sorted[15] = odd
    return odds_sorted

def parseMatch(url, driver):
    url = "https://spinsportsmga.spinpalace.com" + url
    game_name = url.rsplit("/", 2)[-2]
    driver.get(url)
    sleep(4)
    attempt_counter = 0
    failure_counter = 0
    while True:
        try:
            soup = BeautifulSoup(driver.page_source, features="html.parser")
            for element in soup.find_all("li", class_="hoverable-event-container"):
                span_class = element.find_all("span", class_="toggleableHeadline-text")[0]
                market = span_class.text
                if "Exact Score" == market:
                    score_list = []
                    odds_list = []
                    for button in element.find_all("button"):
                        score = button.text[:3]
                        odds = button.text[3:]
                        if int(score[0]) < 4 and int(score[2]) < 4:
                            score_list.append(score)
                            odds_list.append(odds)
                    game = Game(game_name, sortOdds(odds_list, score_list))
                    failure_counter = 0
                    attempt_counter = 0
            return game
        except (AttributeError, UnboundLocalError, IndexError):
            sleep(1)
            #Give 5 attempts to find the buttons, if this fails 5 times stop giving these tries and immediately fail
            if failure_counter > 5:
                return None
            attempt_counter += 1
            if attempt_counter > 5:
                return None
            else:
                failure_counter += 1
                continue

def getMatchUrls(url, driver):
    url_list = []
    driver.get(url)
    sleep(4)
    soup = BeautifulSoup(driver.page_source, features="html.parser")
    for game in soup.find_all("a", class_="event-details event-details-upcomming"):
        url = game["href"]
        if "/en/sports/soccer/" in url and url not in url_list:
            url_list.append(url)
    return url_list



url = "/en/sports/soccer/germany-1-bundesliga/20200224/eintracht-frankfurt-vs-union-berlin/"
match_url = "https://spinsportsmga.spinpalace.com/en/sports/soccer/"

driver = webdriver.Chrome("bin/chromedriver")

url_list = getMatchUrls(match_url, driver)

json_s = "["
for url in url_list:
    game = parseMatch(url, driver)
    if game != None:
        json_s += game.toJSON()
json_s = json_s.replace("}{", "},{")
json_s += "]"

with open("ss_output.json", "w") as file:
    file.write(json_s)

print("--- %s seconds ---" % (time.time() - start_time))





