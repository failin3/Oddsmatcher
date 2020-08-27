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

def parsePage(soup):
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

def makePageLoad(driver, nr_of_tries):
    for _ in range(nr_of_tries):
        for _ in range(5):
            if len(driver.find_elements_by_class_name("ods-odd-link")) > 100:
                return True
            sleep(1)
        sleep(1)
    logger.debug("Page didn't want to load")
    return False

def parseBetathome(driver):
    url = "https://www.bet-at-home.com/en/sport"
    driver.get(url)
    sleep(1)
    #Click on Football
    driver.find_elements_by_class_name("ftl-item-link")[0].click()
    sleep(0.2)
    driver.find_elements_by_class_name("seb")[0].find_elements_by_tag_name("a")[0].click()
    sleep(1)
    #Start scraping
    if makePageLoad(driver, 5):
        soup = BeautifulSoup(driver.page_source, features="html.parser")
        game_list = parsePage(soup)
    driver.find_elements_by_class_name("m-pageNum2")[0].click()
    sleep(1)
    if makePageLoad(driver, 5):
        soup = BeautifulSoup(driver.page_source, features="html.parser")
        game_list += parsePage(soup)
    

    return game_list

if __name__ == "__main__":
    driver = webdriver.Chrome("bin/chromedriver")
    game_list = parseBetathome(driver)
    for game in game_list:
        print("{:<40} {:>7} {:>7}  {:>7}".format(game.name, game.r1, game.rX, game.r2))
