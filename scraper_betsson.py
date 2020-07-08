from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep

url_matches = "https://www.betsson.com/en/sportsbook/football?tab=competitionsAndLeagues"


class OutrightGame:
    def __init__(self, name, r1, rX, r2):
        self.name = name
        self.r1 = r1
        self.rX = rX
        self.r2 = r2

def parseBetsson(driver):
    driver.get(url_matches)
    sleep(5)
    league_element = driver.find_elements_by_class_name("obg-m-events-master-detail-header-title")
    #Click on top 6 leagues
    for i in range(6):
        league_element[i].click()
        sleep(1)
    soup = BeautifulSoup(driver.page_source, features="html.parser")
    game_list = []
    for bet in soup.find_all("obg-event-row-market-container"):
        #Check if this match is live, we dont want live matches
        if len(bet.find_all("div", class_="live")) == 0:
            team_names = bet.find_all("span", class_="obg-selection-content-label")
            team1 = team_names[0].text
            team2 = team_names[2].text
            result = bet.find_all("obg-numeric-change", class_="obg-numeric-change")
            r1 = result[0].text
            rX = result[1].text
            r2 = result[2].text
            #print("{}: {} | {}: {} | {}: {}".format(team1, r1, "Draw", rX, team2, r2))
            game_name = team1 + " v " + team2 
            game = OutrightGame(game_name, r1, rX, r2)
            game_list.append(game)
    return game_list

if __name__ == "__main__":
    driver = webdriver.Chrome("bin/chromedriver")
    game_list = parseBetsson(driver)
    for game in game_list:
        print("{}: {} - {} - {}".format(game.name, game.r1, game.rX, game.r2))
    

