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

def parseBetathome(driver):
    url = "https://www.bet-at-home.com/en/sport"
    driver.get(url)
    sleep(1)
    #Click on Football
    driver.find_elements_by_class_name("ftl-item-link")[0].click()
    sleep(1)
    #Click on all leagues
    for i in range(15):
        try:
            driver.find_elements_by_class_name("ftl-nestedItem-title")[i+1].click()
            driver.find_elements_by_class_name("i-checkRegionBlue15x14")[i+1].click()
        except:
            logger.debug("Probably tooltip in the way and couldn't click")
        sleep(0.5)
    sleep(1)
    #Start scraping
    soup = BeautifulSoup(driver.page_source, features="html.parser")
    #First one is not a game
    soup = soup.find("div", class_="sport-odds")
    iterate = soup.find_all("tr")
    game_list = []
    for item in iterate:
        try:
            team1 = item.find("span").text.split(" - ")[0]
            team2 = item.find("span").text.split(" - ")[1]
            
            r1 = item.find_all("a", class_="ods-odd-link l-right l-textCenter")[0].text
            rX = item.find_all("a", class_="ods-odd-link l-right l-textCenter")[1].text
            r2 = item.find_all("a", class_="ods-odd-link l-right l-textCenter")[2].text

            game = OutrightGame("{} vs {}".format(team1, team2), r1, rX, r2)
            game_list.append(game)
        #Tip thingy doesnt have odds obviously
        except AttributeError:
            pass
        except Exception as e:
            logger.debug(e)

    return game_list

if __name__ == "__main__":
    driver = webdriver.Chrome("bin/chromedriver")
    game_list = parseBetathome(driver)
    for game in game_list:
        print("{:<40} {:>7} {:>7}  {:>7}".format(game.name, game.r1, game.rX, game.r2))
