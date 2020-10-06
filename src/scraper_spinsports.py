from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.expected_conditions import _find_element
import re

from logger_manager import *

url = "https://spinsportsmga.spinpalace.com/en/sports/soccer/"


class OutrightGame:
    def __init__(self, name, r1, rX, r2):
        self.name = name
        self.r1 = r1
        self.rX = rX
        self.r2 = r2

def makePageLoad(driver, nr_of_tries):
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "rj-ev-list__ev-card__team-1-name")))
    return True

def classExists(game_to_check, game_list):
    for game in game_list:
        if game_to_check.name == game.name:
            return True
    return False

def getMatchesOnPage(driver):
    soup = BeautifulSoup(driver.page_source, features="html.parser")
    game_list = []
    for item in soup.find_all("div", class_="rj-ev-list__ev-card--upcoming"):
        try:
            team1 = item.find("div", class_="rj-ev-list__ev-card__team-1-name").text
            team2 = item.find("div", class_="rj-ev-list__ev-card__team-2-name").text

            r1 = item.find_all("span", class_="rj-ev-list__bet-btn__content rj-ev-list__bet-btn__odd")[0].text
            rX = item.find_all("span", class_="rj-ev-list__bet-btn__content rj-ev-list__bet-btn__odd")[1].text
            r2 = item.find_all("span", class_="rj-ev-list__bet-btn__content rj-ev-list__bet-btn__odd")[2].text
            game = OutrightGame("{} vs {}".format(team1, team2), r1, rX, r2)
            game_list.append(game)
        except Exception as e:
            logger.debug(e)
    return game_list

def parseSpinsports(driver):
    driver.get(url)
    if not makePageLoad(driver, 5):
        logger.error("Page didn't load, skipping for now")
        return []
    sleep(5)
    game_list = getMatchesOnPage(driver)
    #Click on the coming days
    for i in range(1,5):
        driver.find_elements_by_class_name("rj-carousel-item__details")[i].click()
        sleep(2)
        game_list += getMatchesOnPage(driver)
    return game_list
    

if __name__ == "__main__":
    driver = webdriver.Chrome("bin/chromedriver")
    game_list = parseSpinsports(driver)
    for game in game_list:
        print("{:<40} {:>7} {:>7}  {:>7}".format(game.name, game.r1, game.rX, game.r2))
