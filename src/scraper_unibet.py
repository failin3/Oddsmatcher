from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.expected_conditions import _find_element
import re

from logger_manager import *

url = "https://www.unibet.eu/betting/sports/filter/all/all/all/all/starting-soon"


class OutrightGame:
    def __init__(self, name, r1, rX, r2):
        self.name = name
        self.r1 = r1
        self.rX = rX
        self.r2 = r2

def makePageLoad(driver, nr_of_tries):
    for _ in range(nr_of_tries):
        for _ in range(5):
            if len(driver.find_elements_by_class_name("KambiBC-filter-events-by-sports-container")) > 1:
                sleep(1)
                return True
            sleep(1)
        driver.get(url)
    return False

def waitOnButtons(driver):
    wait = WebDriverWait(driver, 60)
    #wait.until(lambda d: "." in d.find_elements_by_tag_name("rate-button").text)
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "KambiBC-filter-events-by-sports-container")))
    #sleep(4)

def classExists(game_to_check, game_list):
    for game in game_list:
        if game_to_check.name == game.name:
            return True
    return False

def parseUnibet(driver):
    driver.get(url)
    if not makePageLoad(driver, 5):
        logger.error("Page didn't load, skipping for now")
        return []
    sleep(1)
    #Click cookie accept
    try:
        driver.find_element_by_id("CybotCookiebotDialogBodyButtonAccept").click()
    except:
        logger.debug("Cookie button has already been pressed")
    sleep(1)
    #Click on football
    driver.find_elements_by_class_name("KambiBC-filter-events-by-sports-container")[0].click()
    sleep(1)

    #Collapse expanded
    for item in driver.find_elements_by_class_name("KambiBC-expanded"):
        item.find_element_by_class_name("KambiBC-mod-event-group-header__title-inner").click()
        sleep(0.1)

    #Open all
    for item in driver.find_elements_by_class_name("KambiBC-mod-event-group-header__title-inner"):
        item.click()
        sleep(0.05)

    soup = BeautifulSoup(driver.page_source, features="html.parser")
    soup = soup.find("div", class_="KambiBC-time-ordered-list-content")
    game_list = []
    for item in soup.find_all("div", class_="KambiBC-event-item__event-wrapper"):
        try:
            team1 = item.find_all("div", class_="KambiBC-event-participants__name")[0].text
            team2 = item.find_all("div", class_="KambiBC-event-participants__name")[1].text
            
            r1 = item.find_all("div", class_="sc-AxheI")[0].text
            rX = item.find_all("div", class_="sc-AxheI")[1].text
            r2 = item.find_all("div", class_="sc-AxheI")[2].text
            game = OutrightGame("{} vs {}".format(team1, team2), r1, rX, r2)
            if not classExists(game, game_list):
                game_list.append(game)
        except Exception as e:
            logger.debug(e)
    return game_list

if __name__ == "__main__":
    driver = webdriver.Chrome("bin/chromedriver")
    game_list = parseUnibet(driver)
    for game in game_list:
        print("{:<40} {:>7} {:>7}  {:>7}".format(game.name, game.r1, game.rX, game.r2))
