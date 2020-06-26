from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from time import sleep
import re
import json

import time

from bs4 import BeautifulSoup

class Game:
    def __init__(self, name, odds):
        self.name = name
        self.s00 = odds[0]
        self.s10 = odds[1]
        self.s11 = odds[2] 
        self.s01 = odds[3] 
        self.s20 = odds[4] 
        self.s21 = odds[5] 
        self.s22 = odds[6] 
        self.s12 = odds[7] 
        self.s02 = odds[8] 
        self.s30 = odds[9] 
        self.s31 = odds[10] 
        self.s32 = odds[11] 
        self.s33 = odds[12] 
        self.s23 = odds[13] 
        self.s13 = odds[14] 
        self.s03 = odds[15] 

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

def parseMatch(url, driver, logs=False):
    if logs:
        print("Going  to Match URL")
    url = "https://spinsportsmga.spinpalace.com" + url
    game_name = url.rsplit("/", 2)[-2]
    driver.get(url)
    if logs:
        print("Sleeping 4 seconds")
    sleep(4)
    attempt_counter = 0
    failure_counter = 0
    while True:
        try:
            soup = BeautifulSoup(driver.page_source, features="html.parser")
            if logs:
                print("Converted to bs4")
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
                if logs:
                    print("5 failures, aborting this match")
                return None
            attempt_counter += 1
            if attempt_counter > 5:
                if logs:
                    print("5 attempts, aborting this match")
                return None
            else:
                failure_counter += 1
                continue

def getMatchUrls(url, driver):
    url_list = []
    driver.get(url)
    sleep(4)

    driver.find_elements_by_class_name("page-header-dropdown-text")[1].click()
    driver.find_element_by_id("odd_style_1").click()
    
    #Click to go to the page of all games next 24 hours
    elements = driver.find_elements_by_tag_name("li")
    for element in elements:
        if element.text == "Upcoming":
            element.click()
            sleep(1)
            break
    dropdown = driver.find_elements_by_class_name("filter-htmldropdown-placeholder")[1]
    dropdown.click()
    sleep(1)
    selection = driver.find_elements_by_xpath("//*[contains(text(), 'Next 24 Hours')]")[0]
    selection.click()
    sleep(1)
    soup = BeautifulSoup(driver.page_source, features="html.parser")
    sleep(1)
    for game in soup.find_all("a", class_="event-details event-details-upcomming"):
        url = game["href"]
        if "/en/sports/soccer/" in url and url not in url_list:
            url_list.append(url)
    return url_list

if __name__ == "__main__":

    url = "/en/sports/soccer/germany-1-bundesliga/20200224/eintracht-frankfurt-vs-union-berlin/"
    match_url = "https://spinsportsmga.spinpalace.com/en/sports/soccer/"
    browse_url = "https://spinsportsmga.spinpalace.com/en/sports/"

    driver = webdriver.Chrome("bin/chromedriver")



    while True:
        url_list = getMatchUrls(browse_url, driver)[:40]
        #url_list = url_list[::-1]
        json_s = "["
        for url in url_list:
            game = parseMatch(url, driver)
            if game != None:
                json_s += game.toJSON()
        json_s = json_s.replace("}{", "},{")
        json_s += "]"

        with open("ss_output.json", "w") as file:
            file.write(json_s)

        sleep(5*60)    





