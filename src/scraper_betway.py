from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from time import sleep

from logger_manager import *

class OutrightGame:
    def __init__(self, name, r1, rX, r2):
        self.name = name
        self.r1 = r1
        self.rX = rX
        self.r2 = r2

def classExists(game_to_check, game_list):
    for game in game_list:
        if game_to_check == game.name:
            return True
    return False

def makePageLoad(driver, nr_of_tries):
    for _ in range(nr_of_tries):
        for _ in range(5):
            if len(driver.find_elements_by_class_name("outcomes3x")) > 3:
                return True
            sleep(1)
        sleep(1)
    logger.debug("Page didn't want to load")
    return False

def parseBetway(driver):
    url = "https://sports.betway.com/en/sports/cps/soccer"
    driver.get(url)
    if not makePageLoad(driver, 5):
        return []
    sleep(1)
    try:
        driver.find_element_by_class_name("cookiePolicyAcceptButton").click()
    except:
        logger.debug("Cookie button has already been pressed")
    for i in range(4):
        driver.find_elements_by_class_name("alternativeHeaderBackground")[i+1].click()
        sleep(1)
    sleep(1)
    soup = BeautifulSoup(driver.page_source, features="html.parser")
    game_list = []
    for bet in soup.find_all("div", class_="oneLineEventItem"):
        try:
            team1 = bet.find_all("span", class_="teamNameFirstPart")[0].text.strip()
            team2 = bet.find_all("span", class_="teamNameFirstPart")[1].text.strip()
            game_name = "{} vs {}".format(team1, team2)

            odds_location = bet.find_all("div", class_="outcomes3x")[0]

            r1 = odds_location.find_all("div", class_="odds")[0].text
            rX = odds_location.find_all("div", class_="odds")[1].text
            r2 = odds_location.find_all("div", class_="odds")[2].text

            game = OutrightGame(game_name, r1, rX, r2)
            game_list.append(game)
        except Exception as e:
            logger.debug(e)
    return game_list

if __name__ == "__main__":
    driver = webdriver.Chrome("bin/chromedriver")
    game_list = parseBetway(driver)
    for game in game_list:
        print("{:<40} {:>7} {:>7}  {:>7}".format(game.name, game.r1, game.rX, game.r2))
