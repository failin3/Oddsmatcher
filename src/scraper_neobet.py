from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep
import re

from logger_manager import *


class OutrightGame:
    def __init__(self, name, r1, rX, r2):
        self.name = name
        self.r1 = r1
        self.rX = rX
        self.r2 = r2

def makePageLoad(driver, url, nr_of_tries):
    #Make it LOAAADD!!!!
    for _ in range(nr_of_tries):
        for _ in range(5):
            if len(driver.find_elements_by_class_name("matchRow")) > 2:
                sleep(2)
                return True
            sleep(1)
        driver.get(url)
    return False

def getFootballSection(soup):
    #Get football section
    soup = soup.find_all("section")
    for item in soup:
        if item["data-onsite-sport-block"] == "Football":
            soup = item
            break
    return soup

def openContainers(driver):
    #Click to open first 20 containers
    for i in range(20):
        try:
            collapse_container = driver.find_elements_by_class_name("s1z_headerRow")[i]
            if "closedBlock" in collapse_container.get_attribute("class"):
                collapse_container.click()
                sleep(0.1)
        except:
            pass

def classExists(game_to_check, game_list):
    for game in game_list:
        if game_to_check.name == game.name:
            return True
    return False

def parseNeobet(driver):
    url = "https://neo.bet/en/Sportbets"
    driver.get(url)
    if not makePageLoad(driver, url, 5):
        return []
    sleep(1)
    openContainers(driver)
    #Scrape main page
    soup = BeautifulSoup(driver.page_source, features="html.parser")
    soup = getFootballSection(soup)
    game_list = []
    for bet in soup.find_all("div", class_="matchRow"):
        try:
            team1 = bet.find_all("div", class_=re.compile("s1\w_team"))[0].text.strip()
            team2 = bet.find_all("div", class_=re.compile("s1\w_team"))[2].text.strip()
            r1 = bet.find_all("span", class_=re.compile("s1\w_decimal"))[0].text.strip()
            rX = bet.find_all("span", class_=re.compile("s1\w_decimal"))[1].text.strip()
            r2 = bet.find_all("span", class_=re.compile("s1\w_decimal"))[2].text.strip()
            game_list.append(OutrightGame("{} vs {}".format(team1, team2), r1, rX, r2))
        except Exception as e:
            logger.debug(e)

    #Why 3? Idk, weird web design
    driver.find_elements_by_xpath("//*[contains(text(), 'Time')]")[3].click()
    sleep(1)
    #Why 1? Again IDK!
    driver.find_elements_by_xpath("//*[contains(text(), 'Today')]")[1].click()
    sleep(1)
    openContainers(driver)
    #print(driver.find_elements_by_class_name("events-tree-table-node-CH-name"))    
    soup = BeautifulSoup(driver.page_source, features="html.parser")
    soup = getFootballSection(soup)
    for bet in soup.find_all("div", class_="matchRow"):
        #TODO: implement live indicator, to dismiss that game.
        # if bet.find("div", class_="live-indicator"):
        #     continue
        #Now using \w in regex because s1*_betmarket etc keeps changing
        #if len(bet.find_all("div", class_=re.compile("s1\w_betmarket"))[1].find_all("div", class_=re.compile("s1\w_center"))) == 3:
        try:
            team1 = bet.find_all("div", class_=re.compile("s1\w_team"))[0].text.strip()
            team2 = bet.find_all("div", class_=re.compile("s1\w_team"))[2].text.strip()
            r1 = bet.find_all("span", class_=re.compile("s1\w_decimal"))[0].text.strip()
            rX = bet.find_all("span", class_=re.compile("s1\w_decimal"))[1].text.strip()
            r2 = bet.find_all("span", class_=re.compile("s1\w_decimal"))[2].text.strip()
            game = OutrightGame("{} vs {}".format(team1, team2), r1, rX, r2)
            if not classExists(game, game_list):
                game_list.append(game)
        except Exception as e:
            logger.debug(e)
    return game_list

if __name__ == "__main__":
    driver = webdriver.Chrome("bin/chromedriver")
    game_list = parseNeobet(driver)
    for game in game_list:
        print("{:<40} {:>7} {:>7}  {:>7}".format(game.name, game.r1, game.rX, game.r2))
