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
            if len(driver.find_elements_by_tag_name("rate-button")) > 500:
                return True
            sleep(1)
        sleep(1)
    logger.debug("Page didn't want to load")
    return False

def parseLVBet(driver):
    #TODO: Add Laliga, Serie A and more league ids to url
    url = "https://sports.lvbet.com/en/pre-matches/multiple--?leagues=53,392,617,853,942,20195,20191,4215,11470,860,18884,7306,486,823,3568,6877,9868,353,9659,42867,44230,754,4620,676,719,741,4858,5117,9593,9629,9630,12803,13039,671,604,909,400,583,4859,665,651"
    driver.get(url)
    if not makePageLoad(driver, 5):
        return []
    sleep(2)
    soup = BeautifulSoup(driver.page_source, features="html.parser")
    game_list = []
    for bet in soup.find_all("div", class_="sb-odds-table-game"):
        try:
            team1 = bet.find("a", class_="game").find_all("li")[0].text
            team2 = bet.find("a", class_="game").find_all("li")[1].text
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

if __name__ == "__main__":
    driver = webdriver.Chrome("bin/chromedriver")
    game_list = parseLVBet(driver)
    for game in game_list:
        print("{:<40} {:>7} {:>7}  {:>7}".format(game.name, game.r1, game.rX, game.r2))
