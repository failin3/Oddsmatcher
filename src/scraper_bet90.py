from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from time import sleep

from logger_manager import *

SCROLL_DOWN_AMOUNTS = 5
SLEEP_TIME_BETWEEN_SPACES = 0.5


class OutrightGame:
    def __init__(self, name, r1, rX, r2):
        self.name = name
        self.r1 = r1
        self.rX = rX
        self.r2 = r2

def clickTab(driver, tab_text):
    elements = driver.find_elements_by_tag_name("li")
    for element in elements:
        if element.text == tab_text:
            element.click()
            sleep(1)
            break

def classExists(game_to_check, game_list):
    for game in game_list:
        if game_to_check == game.name:
            return True
    return False


def parseBet90(driver):
    url = "https://www.bet90.com/en/"
    driver.get(url)
    sleep(2)
    clickTab(driver, "Upcoming")
    game_list = []
    #Lazy loading so you have to process every time you scroll down
    for _ in range(SCROLL_DOWN_AMOUNTS):
        try:
            ActionChains(driver).send_keys(Keys.SPACE).perform()
            soup = BeautifulSoup(driver.page_source, features="html.parser")
            for item in soup.find_all("div", class_="rj-ev-list__ev-card rj-ev-list__ev-card--upcoming rj-ev-list__ev-card--regular"):
                team1 = item.find_all("span", class_="rj-ev-list__name-text")[0].text
                team2 = item.find_all("span", class_="rj-ev-list__name-text")[1].text
                r1 = item.find_all("span", class_="rj-ev-list__bet-btn__odd")[0].text
                rX = item.find_all("span", class_="rj-ev-list__bet-btn__odd")[1].text
                r2 = item.find_all("span", class_="rj-ev-list__bet-btn__odd")[2].text
                if not classExists("{} vs {}".format(team1, team2), game_list):
                    game_list.append(OutrightGame("{} vs {}".format(team1, team2), r1, rX, r2))
            sleep(SLEEP_TIME_BETWEEN_SPACES)
        except Exception as e:
            logger.debug(e)
    clickTab(driver, "Highlights")
    for _ in range(SCROLL_DOWN_AMOUNTS):
        try:
            ActionChains(driver).send_keys(Keys.SPACE).perform()
            soup = BeautifulSoup(driver.page_source, features="html.parser")
            for item in soup.find_all("div", class_="rj-ev-list__ev-card rj-ev-list__ev-card--upcoming rj-ev-list__ev-card--regular"):
                #Highlights has a league name above team names so need to take second and third
                team1 = item.find_all("span", class_="rj-ev-list__name-text")[1].text
                team2 = item.find_all("span", class_="rj-ev-list__name-text")[2].text
                r1 = item.find_all("span", class_="rj-ev-list__bet-btn__odd")[0].text
                rX = item.find_all("span", class_="rj-ev-list__bet-btn__odd")[1].text
                r2 = item.find_all("span", class_="rj-ev-list__bet-btn__odd")[2].text
                if not classExists("{} vs {}".format(team1, team2), game_list):
                    game_list.append(OutrightGame("{} vs {}".format(team1, team2), r1, rX, r2))
            sleep(SLEEP_TIME_BETWEEN_SPACES)
        except Exception as e:
            logger.debug(e)
    return game_list

if __name__ == "__main__":
    driver = webdriver.Chrome("bin/chromedriver")
    game_list = parseBet90(driver)
    for game in game_list:
        print("{:<40} {:>7} {:>7}  {:>7}".format(game.name, game.r1, game.rX, game.r2))
