import betfairlightweight
import json
import datetime
from time import sleep
import pytz

from logger_manager import *

GAME_DATE_RANGE = 1
START_TIME = "00:00"
END_TIME = "23:59"


class CorrectScoreRunner:
    def __init__(self):
        self.s00 = None
        self.s10 = None
        self.s11 = None 
        self.s01 = None 
        self.s20 = None 
        self.s21 = None 
        self.s22 = None 
        self.s12 = None 
        self.s02 = None 
        self.s30 = None 
        self.s31 = None 
        self.s32 = None 
        self.s33 = None 
        self.s23 = None 
        self.s13 = None 
        self.s03 = None 
        
    def updateRunner(self, selection_id, available_to_lay, price):
            data = [available_to_lay, price]
            if selection_id == 1:
                self.s00 = data
            if selection_id == 2:
                self.s10 = data
            if selection_id == 3:
                self.s11 = data
            if selection_id == 4:
                self.s01 = data
            if selection_id == 5:
                self.s20 = data
            if selection_id == 6:
                self.s21 = data
            if selection_id == 7:
                self.s22 = data
            if selection_id == 8:
                self.s12 = data
            if selection_id == 9:
                self.s02 = data
            if selection_id == 10:
                self.s30 = data
            if selection_id == 11:
                self.s31 = data
            if selection_id == 12:
                self.s32 = data
            if selection_id == 13:
                self.s33 = data
            if selection_id == 14:
                self.s23 = data
            if selection_id == 15:
                self.s13 = data
            if selection_id == 16:
                self.s03 = data


class OutrightRunner:
    def __init__(self, r1, rX, r2):
        self.r1 = r1
        self.rX = rX
        self.r2 = r2


class BetfairGame:
    def __init__(self, name, event_id, day_, time_):
        self.name = name
        self.event_id = event_id
        self.date = day_
        self.time = time_
        self.outrights = None
        self.correct_score = None


def getApiCredentials():
    with open("betfair_api_credentials.txt") as f:
        app_key = f.readline().strip()
        username = f.readline().strip()
        password = f.readline().strip()
        api = betfairlightweight.APIClient(username, password , app_key)
        api.login_interactive()
        return api


def getCorrectScore(game, markets):
    correct_score_runner = CorrectScoreRunner()
    for runner in markets.runners:
        try:
            selection_id = runner.selection_id
            #0 because it gets 3 values to lay, want only the first one as its the lowest
            available_to_lay = runner.ex.available_to_lay[0].size
            price = runner.ex.available_to_lay[0].price
        except IndexError:
            available_to_lay = 0
            price = 0
        correct_score_runner.updateRunner(selection_id, available_to_lay, price)
    game.correct_score = correct_score_runner
    return game


def getOutrights(game, markets):
    try:
        data = [runner.ex.available_to_lay[0] for runner in markets.runners]
        #rX is the last one in the packet apparently
        r1 = [data[0].size, data[0].price]
        rX = [data[2].size, data[2].price]
        r2 = [data[1].size, data[1].price]
    except IndexError:
        r1 = None
        rX = None
        r2 = None
    runner = OutrightRunner(r1, rX, r2)
    game.outrights = runner
    return game
    

def getGames():
    #Calculate new date every time this function is called
    START_DATE = datetime.datetime.now().strftime("%Y-%m-%d")
    END_DATE = (datetime.datetime.now()+datetime.timedelta(days=GAME_DATE_RANGE)).strftime("%Y-%m-%d")
    while True:
        try:
            api = getApiCredentials()
            football_event_id = [item.event_type.id for item in api.betting.list_event_types() if item.event_type.name == "Soccer"][0]
            filter = {
                "eventTypeIds": [football_event_id],
                "marketStartTime": {
                    "from": "{}T{}:00Z".format(START_DATE, START_TIME),
                    "to": "{}T{}:00Z".format(END_DATE, END_TIME)
                }      
            }
            events =  api.betting.list_events(filter)
            events = [event for event in events if event.market_count > 25]
            game_list = []
            break
        except Exception as e:
            logger.error(e)
            pass
    

    for i, event in enumerate(events):
        while True:
            try:
                logger.debug("{}/{}".format(i+1, len(events)))
                #Loop over event, create class then save info
                event_name = event.event.name
                event_id = event.event.id
                event_date = event.event.open_date
                #Convert timezone
                amsterdam = pytz.timezone('Europe/Amsterdam')
                event_date = pytz.utc.localize(event_date).astimezone(amsterdam)
                date_ = event_date.strftime("%d-%m")
                time_ = event_date.strftime("%H:%M") 
                game = BetfairGame(event_name, event_id, date_, time_)
                #Get correct score markets
                filter = {
                    #"textQuery" : "CORRECT_SCORE",
                    "eventIds": [event_id]
                }
                #Get all marketids
                response = api.betting.list_market_catalogue(filter, max_results=200, market_projection=["EVENT"])
                for market in response:
                    if market.market_name == "Correct Score":
                        correct_score_id = market.market_id
                    if market.market_name == "Match Odds":
                        outrights_id = market.market_id
                #Process markets
                #Correct score
                try:
                    markets = api.betting.list_market_book([correct_score_id, outrights_id], price_projection={"priceData" : ["EX_BEST_OFFERS"]})
                except NameError:
                    #Doesn't have this market, skip this game
                    #TODO: Maybe don't skip but only not execute this part
                    #print("NameError")
                    continue
                game = getCorrectScore(game, markets[1])
                game = getOutrights(game, markets[0])


                game_list.append(game)
            except Exception as e:
                logger.error(e)
                continue
            break
    return game_list
            

if __name__ == "__main__": 
    game_list = getGames()
    for game in game_list:
        print("{}: 1: {} - X: {} - 2: {}".format(game.name, game.outrights.r1[1], game.outrights.rX[1], game.outrights.r2[1]))
