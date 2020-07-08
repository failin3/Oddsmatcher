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
    #webdriver.ActionChains(driver).key_down(u'\ue00d').perform()
    driver.find_element_by_class_name("close").click()
    countries = driver.find_elements_by_class_name("KambiBC-collapsible-container")[2:7]
    for country in countries:
        country.click()
        sleep(1)
    soup = BeautifulSoup(driver.page_source, features="html.parser")
    game_list = []
    for element in soup.find_all("a", class_="KambiBC-event-item__link"):
        team_names = element.find_all("div", class_="KambiBC-event-participants__name")
        team1 = team_names[0].text
        team2 = team_names[1].text

        #0 selects outright, otherwise you get second bet type as well
        odds = element.find_all("div", class_="KambiBC-bet-offer__outcomes")[0]
        r1 = odds.find_all("button", class_="KambiBC-betty-outcome")[0].find_all("div")[5].text
        rX = odds.find_all("button", class_="KambiBC-betty-outcome")[1].find_all("div")[5].text
        r2 = odds.find_all("button", class_="KambiBC-betty-outcome")[2].find_all("div")[5].text
        game_list.append(OutrightGame("{} - {}".format(team1, team2), r1, rX, r2))

    return game_list

if __name__ == "__main__":
    game_list = get888sportData()
    for game in game_list:
        print("{:<40} {:>7} {:>7}  {:>7}".format(game.name, game.r1, game.rX, game.r2))