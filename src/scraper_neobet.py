from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep

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
                return
            sleep(1)
        driver.get(url)
    print("Page just doesn't want to load")

def parseNeobet(driver):
    url = "https://neo.bet/en/Sportbets"
    driver.get(url)
    makePageLoad(driver, url, 5)
    #Why 3? Idk, weird web design
    driver.find_elements_by_xpath("//*[contains(text(), 'Time')]")[3].click()
    sleep(1)
    #Why 1? Again IDK!
    driver.find_elements_by_xpath("//*[contains(text(), 'Today')]")[1].click()
    sleep(1)
    
    #print(driver.find_elements_by_class_name("events-tree-table-node-CH-name"))    
    soup = BeautifulSoup(driver.page_source, features="html.parser")
    game_list = []
    for bet in soup.find_all("div", class_="matchRow"):
        # if bet.find("div", class_="live-indicator"):
        #     continue
        if len(bet.find_all("div", class_="s1x_betmarket")[0].find_all("div", class_="s1w_center")) == 3:
            team1 = bet.find_all("div", class_="s1v_team")[0].text.strip()
            team2 = bet.find_all("div", class_="s1v_team")[1].text.strip()
            r1 = bet.find_all("span", class_="s1w_decimal")[0].text.strip()
            rX = bet.find_all("span", class_="s1w_decimal")[1].text.strip()
            r2 = bet.find_all("span", class_="s1w_decimal")[2].text.strip()
            game_list.append(OutrightGame("{} vs {}".format(team1, team2), r1, rX, r2))
        else:
            break
    return game_list

if __name__ == "__main__":
    driver = webdriver.Chrome("bin/chromedriver")
    game_list = parseNeobet(driver)
    for game in game_list:
        print("{:<40} {:>7} {:>7}  {:>7}".format(game.name, game.r1, game.rX, game.r2))
