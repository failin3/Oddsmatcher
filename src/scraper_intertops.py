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


def getDataFromPage(soup):
    game_list = []
    for list_item in soup.find_all("li"):
        try:
            #End of games
            try:
                if list_item.has_attr("class") and list_item["class"][0] == "load-more-container":
                    break
            except IndexError:
                pass
            team_names = list_item.find("a").text.strip()
            #Sometimes extra marketing info is like last minute or top bet is on extra lines, remove those
            team_names = team_names.split("\n")
            if isinstance(team_names, list):
                team_names = team_names[0]
            team1 = team_names.split(" v ")[0]
            team2 = team_names.split(" v ")[1]

            odds_location = list_item.find_all("span", "fright odds")
            
            r1 = odds_location[0].text
            rX = odds_location[1].text
            r2 = odds_location[2].text

            game = OutrightGame("{} vs {}".format(team1, team2), r1, rX, r2)   
            game_list.append(game)
        except Exception as e:
            logger.debug(e)
    return game_list


def classExists(game_to_check, game_list):
    for game in game_list:
        if game_to_check.name == game.name:
            return True
    return False

def parseIntertops(driver):
    url = "https://sports.intertops.eu/en/Bets/Soccer/12"
    driver.get(url)
    sleep(1)
    driver.find_element_by_class_name("topbets").click()
    sleep(1.5)
    driver.find_element_by_class_name("nextbets").click()
    sleep(1)

    for _ in range(10):
        if len(driver.find_elements_by_class_name("toast-close-button")) > 0:
            driver.find_elements_by_class_name("toast-close-button")[0].click()
            sleep(1)
        try:
            driver.find_element_by_class_name("load-more-lnk").click()
        except:
            #Not pretty this, but effective
            #Might crash if there are no pages left anymore
            try:
                driver.find_elements_by_class_name("toast-close-button")[0].click()
            except:
                #No more pages
                break
        sleep(1)
    soup = BeautifulSoup(driver.page_source, features="html.parser")
    soup_next = soup.find("ul", class_="nextbets")
    soup_top = soup.find("ul", class_="topbets")
    game_list = getDataFromPage(soup_next)
    top_games = getDataFromPage(soup_top)
    #Avoid duplicates
    for game in top_games:
        if not classExists(game, game_list):
            game_list.append(game)
    
    
    return game_list


if __name__ == "__main__":
    driver = webdriver.Chrome("bin/chromedriver")
    game_list = parseIntertops(driver)
    for game in game_list:
        print("{:<40} {:>7} {:>7}  {:>7}".format(game.name, game.r1, game.rX, game.r2))