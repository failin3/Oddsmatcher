from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep

from logger_manager import *

betsson_url = "https://www.betsson.com/en/sportsbook/football?tab=competitionsAndLeagues"
betsafe_url = "https://www.betsafe.com/en/sportsbook/football?tab=competitionsAndLeagues"
casinowinner_url = "https://sb.bpsgameserver.com/?token=00000000-0000-0000-0000-000000000000&sid=1101&lc=en&tz=GMT+Standard+Time&dc=EUR&c=nl-NL&pagemenuheaderurl=https%3a%2f%2fwww.casinowinner.com%2fen%2fsport%2fPageMenuHeader.aspx&mainpromourl=https%3a%2f%2fwww.casinowinner.com%2fen%2fsport%2fMainPromo.aspx&articleurl=https%3a%2f%2fwww.casinowinner.com%2fen%2fsport%2f&sidebarpromourl=https%3a%2f%2fwww.casinowinner.com%2fen%2fsport%2fSidebarPromo.aspx&proxyurl=https%3a%2f%2fwww.casinowinner.com%2fsport%2fScript%2fCross-frame%2fproxy.html&minigamesurl=https%3a%2f%2fwww.casinowinner.com%2fen%2fsport%2fMiniGame.aspx&mc=%7B%22marketing%22%3A1%7D"

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

def parseBetsson(driver):
    driver.get(betsson_url)
    sleep(7)
    league_element = driver.find_elements_by_class_name("obg-m-events-master-detail-header-title")
    #Click on top 10 leagues
    for i in range(10):
        league_element[i].click()
        sleep(1)
    soup = BeautifulSoup(driver.page_source, features="html.parser")
    game_list = []
    for bet in soup.find_all("obg-event-row-market-container"):
        #Check if this match is live, we dont want live matches
        if len(bet.find_all("div", class_="live")) == 0:
            try:
                team_names = bet.find_all("span", class_="obg-selection-content-label")
                team1 = team_names[0].text
                team2 = team_names[2].text
                result = bet.find_all("obg-numeric-change", class_="obg-numeric-change")
                r1 = result[0].text
                rX = result[1].text
                r2 = result[2].text
                #print("{}: {} | {}: {} | {}: {}".format(team1, r1, "Draw", rX, team2, r2))
                game_name = team1 + " vs " + team2 
                game = OutrightGame(game_name, r1, rX, r2)
                game_list.append(game)
            except Exception as e:
                logger.debug(e)
    return game_list

def parseBetsafe(driver):
    driver.get(betsafe_url)
    sleep(7)
    league_element = driver.find_elements_by_class_name("obg-m-events-master-detail-header-title")
    #Click on top 10 leagues
    for i in range(10):
        league_element[i].click()
        sleep(1)
    soup = BeautifulSoup(driver.page_source, features="html.parser")
    game_list = []
    for bet in soup.find_all("obg-event-row-market-container"):
        #Check if this match is live, we dont want live matches
        if len(bet.find_all("div", class_="live")) == 0:
            try:
                team_names = bet.find_all("span", class_="obg-selection-content-label")
                team1 = team_names[0].text
                team2 = team_names[2].text
                result = bet.find_all("obg-numeric-change", class_="obg-numeric-change")
                r1 = result[0].text
                rX = result[1].text
                r2 = result[2].text
                #print("{}: {} | {}: {} | {}: {}".format(team1, r1, "Draw", rX, team2, r2))
                game_name = team1 + " vs " + team2 
                game = OutrightGame(game_name, r1, rX, r2)
                game_list.append(game)
            except Exception as e:
                logger.debug(e)
    return game_list

def parseCasinowinner(driver):
    driver.get(casinowinner_url)
    #Piece of shit website
    sleep(10)
    #Get top games
    game_list = []
    soup = BeautifulSoup(driver.page_source, features="html.parser")
    for bet in soup.find_all("div", class_="most-popular-event-container"):
        try:
            game_name = bet.find_all("div", class_="most-popular-event-name-label")[0].text
            game_name = "{} vs {}".format(game_name.split("-")[0].strip(), game_name.split("-")[1].strip())
            selection_buttons = bet.find_all("div", class_="live-selection")
            r1 = selection_buttons[0].text
            rX = selection_buttons[1].text
            r2 = selection_buttons[2].text
            game = OutrightGame(game_name, r1, rX, r2)
            game_list.append(game)
        except Exception as e:
            logger.debug(e)
    element = driver.find_element_by_id("leftmenuitem1")
    #This thing has 95!!! Why!?!? We just choose the first one LOL
    element.find_elements_by_tag_name("material-checkbox")[0].click()
    sleep(1)
    driver.find_elements_by_xpath("//*[contains(text(), 'Show')]")[0].click()
    sleep(5)
    for _ in range(3):
        soup = BeautifulSoup(driver.page_source, features="html.parser")
        for bet in soup.find_all("div", class_="market-mw ng-scope"):
            try:
                game_name = bet.find_all("div", class_="event-description")[0].text
                game_name = "{} vs {}".format(game_name.split("-")[0].strip(), game_name.split("-")[1].strip())
                selection_buttons = bet.find_all("material-button")
                r1 = selection_buttons[0].text
                rX = selection_buttons[1].text
                r2 = selection_buttons[2].text
                #print("{}: {} - {} - {}".format(game_name, r1, rX, r2))
                game = OutrightGame(game_name, r1, rX, r2)
                if not classExists(game.name, game_list):
                    game_list.append(game)
            except Exception as e:
                logger.debug(e)
        driver.find_elements_by_xpath("//*[contains(text(), 'Next')]")[0].click()
        sleep(2)
    return game_list

if __name__ == "__main__":
    driver = webdriver.Chrome("bin/chromedriver")
    game_list = parseCasinowinner(driver)
    for game in game_list:
        print("{:<40} {:>7} {:>7}  {:>7}".format(game.name, game.r1, game.rX, game.r2))
    

