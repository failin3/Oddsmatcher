from urllib import request
import json
import requests
from threading import Thread
import webbrowser
import datetime
from time import sleep

class Game:
    def __init__(self, name, odds, marketid, liquidity, day_, time_):
        self.name = name
        self.odds = odds
        self.marketId = marketid
        self.liquidity = liquidity
        self.day_ = day_
        self.time_ = time_
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

DATE_OF_MATCHES = datetime.datetime.now().strftime("%Y-%m-%d")
if datetime.datetime.now().hour >= 21:
    DATE_OF_MATCHES = (datetime.datetime.now()+datetime.timedelta(days=1)).strftime("%Y-%m-%d")
START_TIME = "00:00"
END_TIME = "23:59"

global runner_labels
global price_labels
global size_labels
global name_labels
global labels

runner_labels = []
price_labels = []
size_labels = []
labels = []
name_labels = []

def getApiCredentials():
    with open("credentials.txt") as f:
        application_key = f.readline().strip()
        session_key = f.readline().strip()
        return application_key, session_key

def sortRunnerLists(runner_list):
    liquidity_list = [None]*16
    odds_list = [None]*16
    for runner in runner_list:
        if runner[1] <= 16:
            odds_list[runner[1]-1] = runner[2]
            liquidity_list[runner[1]-1] = runner[0]
    return odds_list, liquidity_list
        
def getMarkets(game_list, url, header):
        css = ""
        for game in game_list:
            css = css + '"' + game.marketId + '",'
        css = css[:-1]
        #Get amount of money in market
        #"1.168140579", "1.168611121"
        total_list = []
        json_req = '[{{"jsonrpc":"2.0","method":"SportsAPING/v1.0/listMarketBook","params":{{"marketIds":[{}],"priceProjection":{{"priceData":["EX_BEST_OFFERS"],"virtualise":"true"}}}},"id":1}}]'.format(css)
        response = requests.post(url, data=json_req, headers=header).json()
        counter = 0
        for game in response[0]["result"]:
            size_list = []
            market_id = game["marketId"]
            for runner in game["runners"]:
                try:
                    selectionId = runner["selectionId"]
                    available_to_lay = float((runner["ex"]["availableToLay"][0]["size"]))
                    price = float(runner["ex"]["availableToLay"][0]["price"])
                except IndexError:
                    available_to_lay = 0
                size_list.append([available_to_lay, selectionId, price])
            total_list.append([market_id, sorted(size_list, reverse=True)])
            counter += 1
        return total_list

def parseApiDatetime(date_time):
    year = date_time.split("-")[0]
    month = date_time.split("-")[1]
    day = date_time.split("-")[2][:2]
    time = date_time.split("T")[1][:5]
    time = datetime.datetime.strptime(time, "%H:%M")+datetime.timedelta(hours=1)
    return "{}-{}-{}".format(day, month, year), datetime.datetime.strftime(time, "%H:%M")
    

def getBestMatches(date, application_key, session_key):
    url="https://api.betfair.com/exchange/betting/json-rpc/v1"
    header = { 'X-Application' : application_key, 'X-Authentication' : session_key ,'content-type' : 'application/json' }
    
    list_of_games = []
    list_of_market_ids = []
    list_of_names = []

    game_classes = []

    #Get football events in date range
    json_req = '[{{"jsonrpc": "2.0","method": "SportsAPING/v1.0/listEvents","params": {{"filter": {{"eventTypeIds": ["1"],"marketStartTime": {{"from": "{}T{}:00Z","to": "{}T{}:00Z"}}}}}},"id": 1}}]'.format(date[0], date[1], date[0], date[2])
    response = requests.post(url, data=json_req, headers=header)
    games = response.json()

    for event in games[0]["result"]:
        #event_title = event["event"]["name"]
        list_of_games.append(event["event"]["id"])


    #Get correct score market ID for each game
    css = '"' + '","'.join(list_of_games) + '"'
    json_req = '[{{"jsonrpc":"2.0","method":"SportsAPING/v1.0/listMarketCatalogue","params":{{"filter":{{"textQuery":"CORRECT_SCORE","eventIds":[{}]}},"marketProjection": ["EVENT"],"maxResults":"200"}},"id":1}}]'.format(css)
    response = requests.post(url, data=json_req, headers=header).json()
    for event in response[0]["result"]:
        date_, time_ = parseApiDatetime(event["event"]["openDate"])
        game = Game(event["event"]["name"], None, event["marketId"], None, date_, time_)
        game_classes.append(game)
        # list_of_market_ids.append(event["marketId"])
        # list_of_names.append(event["event"]["name"])

    if len(game_classes) > 40:
        total_list = []
        for i in range(0,100):
            total_list = total_list + getMarkets(game_classes[0+40*i:40+40*i], url, header)
            if(len(list_of_market_ids)-40*i < 40):
                break
        total_list = total_list + getMarkets(list_of_market_ids[40*i:], url, header)
    else:
        total_list = getMarkets(list_of_market_ids, url, header)

    for game_element in total_list:
        odds_list, liquidity_list = sortRunnerLists(game_element[1])
        market_id = game_element[0]
        for my_class in game_classes:
            if my_class.marketId == market_id:
                my_class.odds = odds_list
                my_class.liquidity = liquidity_list
    return game_classes

def sentKeepAlive(application_key, session_key):
    url="https://api.betfair.com/exchange/betting/json-rpc/v1"
    header = { 'Accept' : 'application/json', 'X-Application' : application_key, 'X-Authentication' : session_key }
    response = requests.post(url, headers=header)
    

application_key, session_key = getApiCredentials()

#Dont call keepAlive too often (once an hour)
keepAliveCounter = 0
max_keepAlive = 30
while True:
    if keepAliveCounter > 30:
        sentKeepAlive(application_key, session_key)
    try:
        final_list = getBestMatches([DATE_OF_MATCHES, START_TIME, END_TIME], application_key, session_key)
        json_s = '['
        for item in final_list:
            json_s += item.toJSON()
        json_s = json_s.replace("}{", "},{")
        json_s += ']'


        with open("betfair_output.json", "w") as file:
            file.write(json_s)
        sleep(2*60)
    except ValueError:
        print("No JSON, retrying")
        sleep(60)