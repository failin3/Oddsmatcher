from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep
import json


class OutrightGame:
    def __init__(self, name, r1, rX, r2):
        self.name = name
        self.r1 = r1
        self.rX = rX
        self.r2 = r2

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

def get888sportData():
    driver = webdriver.Chrome("bin/chromedriver")
    driver.get("https://www.888sport.com/#/filter/football")
    sleep(10)
    webdriver.ActionChains(driver).key_down(u'\ue00d').perform()
    soup = BeautifulSoup(driver.page_source, features="html.parser")
    game_list = []
    for element in soup.find_all("a", class_="KambiBC-event-item__link"):
        team_names = element.find_all("div", class_="KambiBC-event-participants__name")
        team1 = team_names[0].text
        team2 = team_names[1].text

        #0 selects outright, otherwise you get second bet type as well
        odds = element.find_all("div", class_="KambiBC-bet-offer__outcomes")[0]
        r1 = odds.find_all("div", class_="sc-AxheI cWjOQp")[0].text
        rX = odds.find_all("div", class_="sc-AxheI cWjOQp")[1].text
        r2 = odds.find_all("div", class_="sc-AxheI cWjOQp")[2].text
        game_list.append(OutrightGame("{} - {}".format(team1, team2), r1, rX, r2))

    return game_list

if __name__ == "__main__":
    pass