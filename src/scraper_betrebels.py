from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep

from logger_manager import *

class OutrightGame:
    def __init__(self, name, r1, rX, r2):
        self.name = name
        self.r1 = r1
        self.rX = rX
        self.r2 = r2

def makePageLoad(driver, nr_of_tries):
    for _ in range(nr_of_tries):
        for _ in range(5):
            if len(driver.find_elements_by_class_name("asb-flex-col")) > 10:
                return True
            sleep(1)
        sleep(1)
    logger.debug("Page didn't want to load")
    return False

def parseBetrebels(driver):
    #url = "https://sb1client-altenar.biahosted.com/?origin=https://sb1client-altenar.biahosted.com/static/&token=&fixedbottom=60&walletcode=508729&skinid=betrebels&lang=en-GB&hasplacebetplatformerrorcallback=false#/tree/all/0/100192,100607,100608,100193,100214,100221,100291,100230,100219,100198/0/odds/bytime"
    url = "https://sb1client-altenar.biahosted.com/?origin=https://sb1client-altenar.biahosted.com/static/&token=&fixedbottom=60&walletcode=508729&skinid=betrebels&lang=en-GB&hasplacebetplatformerrorcallback=false#/tree/all/1/0/0/odds/bytime"
    driver.get(url)
    #sleep(5)

    if not makePageLoad(driver, 5):
        return []
    sleep(1)
    #print(driver.find_elements_by_class_name("events-tree-table-node-CH-name"))
    soup = BeautifulSoup(driver.page_source, features="html.parser")
    game_list = []
    for bet in soup.find_all("div", class_="events-table-row"):
        try:
            if "Electronic Leagues" in bet.text:
                continue
            if bet.find("div", class_="live-indicator"):
                continue
            team1 = bet.find_all("div", class_="events-table-row-competitor-name")[0].text.strip()
            team2 = bet.find_all("div", class_="events-table-row-competitor-name")[1].text.strip()
            r1 = bet.find_all("div", class_="prices-markets--price-block")[0].text.strip()
            rX = bet.find_all("div", class_="prices-markets--price-block")[1].text.strip()
            r2 = bet.find_all("div", class_="prices-markets--price-block")[2].text.strip()
            game_list.append(OutrightGame("{} vs {}".format(team1, team2), r1, rX, r2))
        except Exception as e:
            logger.debug(e)
    return game_list

if __name__ == "__main__":
    driver = webdriver.Chrome("bin/chromedriver")
    game_list = parseBetrebels(driver)
    for game in game_list:
        print("{:<40} {:>7} {:>7}  {:>7}".format(game.name, game.r1, game.rX, game.r2))
