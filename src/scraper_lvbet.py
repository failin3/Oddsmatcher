from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from time import sleep

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.expected_conditions import _find_element
import re


from logger_manager import *

#TODO: Add even more league ids
lvbet_url = "https://m-sports.lvbet.com/en/pre-matches/multiple--?leagues=53,392,617,853,942,20195,20191,4215,11470,860,18884,7306,486,823,3568,6877,9868,353,9659,42867,44230,754,4620,676,719,741,4858,5117,9593,9629,9630,12803,13039,671,604,909,400,583,4859,665,651,666,786,639,680,1613,290,846,850,753,904,629,633,2735,74,1224,1757,11654,12369,557,594,592,606,674,433,730,1109,2971,11320,11321,669,775"
energybet_url = "https://energybet.com/en/pre-matches/multiple--?leagues=53,392,617,853,942,20195,20191,4215,11470,860,18884,7306,486,823,3568,6877,9868,353,9659,42867,44230,754,4620,676,719,741,4858,5117,9593,9629,9630,12803,13039,671,604,909,400,583,4859,665,651,666,786,639,680,1613,290,846,850,753,904,629,633,2735,74,1224,1757,11654,12369,557,594,592,606,674,433,730,1109,2971,11320,11321,669,775"

class regex_match(object):
    def __init__(self, locator, regexp):
        self.locator = locator
        self.regexp = regexp

    def __call__(self, driver):
        element_text = _find_element(driver, self.locator).text
        return re.search(self.regexp, element_text)

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

def waitOnButtons(driver):
    wait = WebDriverWait(driver, 50)
    #wait.until(lambda d: "." in d.find_elements_by_tag_name("rate-button").text)
    wait.until(regex_match((By.TAG_NAME, "rate-button"), r"^[0-9.-]*$"))
    sleep(4)

def parseLVBet(driver):
    driver.get(lvbet_url)
    # if not makePageLoad(driver, 5):
    #     return []
    waitOnButtons(driver)
    soup = BeautifulSoup(driver.page_source, features="html.parser")
    game_list = []
    for bet in soup.find_all("div", class_="sb-bet"):
        try:
            team1 = bet.find_all("p", class_="team")[0].text
            team2 = bet.find_all("p", class_="team")[1].text
            game_name = "{} vs {}".format(team1, team2)

            odds_location = bet.find_all("market-selections")[0]

            r1 = odds_location.find_all("rate-button")[0].text.strip()
            rX = odds_location.find_all("rate-button")[1].text.strip()
            r2 = odds_location.find_all("rate-button")[2].text.strip()

            game = OutrightGame(game_name, r1, rX, r2)
            game_list.append(game)
        except Exception as e:
            logger.debug(e)
    return game_list

def parseEnergybet(driver):
    driver.get(energybet_url)
    if not makePageLoad(driver, 5):
        return []
    sleep(2)
    soup = BeautifulSoup(driver.page_source, features="html.parser")
    game_list = []
    for bet in soup.find_all("div", class_="lv-table-entry"):
        try:
            team1 = bet.find("p").contents[2].strip()
            team2 = bet.find("p").contents[5].replace("-", "").strip()
            game_name = "{} vs {}".format(team1, team2)

            odds_location = bet.find_all("market-selections")[0]

            r1 = odds_location.find_all("rate-button")[0].text.strip().split(" ")[1]
            rX = odds_location.find_all("rate-button")[1].text.strip().split(" ")[1]
            r2 = odds_location.find_all("rate-button")[2].text.strip().split(" ")[1]

            game = OutrightGame(game_name, r1, rX, r2)
            game_list.append(game)
        except Exception as e:
            logger.debug(e)
    return game_list

if __name__ == "__main__":
    driver = webdriver.Chrome("bin/chromedriver")
    game_list = parseLVBet(driver)
    for game in game_list:
        print("{:<40} {:>7} {:>7}  {:>7}".format(game.name, game.r1, game.rX, game.r2))
