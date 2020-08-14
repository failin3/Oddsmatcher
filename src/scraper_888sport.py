from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep
import json

from logger_manager import *


class OutrightGame:
    def __init__(self, name, r1, rX, r2):
        self.name = name
        self.r1 = r1
        self.rX = rX
        self.r2 = r2

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

def makePageLoad(driver, url, nr_of_tries):
    #Make it LOAAADD!!!!
    for _ in range(nr_of_tries):
        for _ in range(10):
            if len(driver.find_elements_by_class_name("main-loader")) == 0:
                sleep(2)
                return
            sleep(1)
        driver.get(url)
    logger.info("Page just doesn't want to load")

def classExists(game_to_check, game_list):
    for game in game_list:
        if game_to_check.name == game.name:
            return True
    return False

def get888sportData(driver):
    url = "https://www.888sport.com/#/filter/football"
    driver.get(url)
    sleep(1)
    makePageLoad(driver, url, 3)
    sleep(2)
    #webdriver.ActionChains(driver).key_down(u'\ue00d').perform()
    close_buttons = driver.find_elements_by_class_name("close")
    for button in close_buttons:
        button.click()
        sleep(1)
    #countries = driver.find_elements_by_class_name("KambiBC-collapsible-container")[2:10]
    countries = driver.find_elements_by_css_selector("div[class='KambiBC-collapsible-container KambiBC-mod-event-group-container']")
    for country in countries:
        country.click()
        sleep(0.05)
    soup = BeautifulSoup(driver.page_source, features="html.parser")
    game_list = []
    for element in soup.find_all("a", class_="KambiBC-event-item__link"):
        try:
            team_names = element.find_all("div", class_="KambiBC-event-participants__name")
            team1 = team_names[0].text
            team2 = team_names[1].text

            #0 selects outright, otherwise you get second bet type as well
            odds = element.find_all("div", class_="KambiBC-bet-offer__outcomes")[0]
            r1 = odds.find_all("button", class_="KambiBC-betty-outcome")[0].find_all("div")[5].text
            rX = odds.find_all("button", class_="KambiBC-betty-outcome")[1].find_all("div")[5].text
            r2 = odds.find_all("button", class_="KambiBC-betty-outcome")[2].find_all("div")[5].text
            game = OutrightGame("{} vs {}".format(team1, team2), r1, rX, r2)                
            if not classExists(game, game_list):
                game_list.append(game)
        except Exception as e:
            logger.debug(e)

    return game_list

if __name__ == "__main__":
    driver = webdriver.Chrome("bin/chromedriver")
    game_list = get888sportData(driver)
    for game in game_list:
        print("{:<40} {:>7} {:>7}  {:>7}".format(game.name, game.r1, game.rX, game.r2))