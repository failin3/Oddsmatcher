import betfairlightweight
import json
import datetime

START_DATE = DATE_OF_MATCHES = datetime.datetime.now().strftime("%Y-%m-%d")
END_DATE = DATE_OF_MATCHES = (datetime.datetime.now()+datetime.timedelta(days=1)).strftime("%Y-%m-%d")
START_TIME = "00:00"
END_TIME = "23:59"

class Runner:
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

    def updateRunners(self, runner_list):
        for runner in runner_list:
            #Why the fuck is the runner id on index 1???
            selection_id = runner[1]
            data = [runner[0], runner[2]]
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

class BetfairGame:
    def __init__(self, name, event_id, marketid, day_, time_):
        self.name = name
        self.event_id = event_id
        self.market_id = marketid
        self.day_ = day_
        self.time_ = time_
        self.runner = None

    def insertRunner(self, runner_list):
        runner = Runner()
        runner.updateRunners(runner_list)
        self.runner = runner

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

class BetfairInformation:
    def __init__(self):
        self.games = None

    def createGameClasses(self, response):
        game_list = []
        for game in response:
            gameClass = BetfairGame(game.event.name, game.event.id, game.market_id, game.event.open_date, None)
            game_list.append(gameClass)
        return game_list

    def getGames(self):
        return self.games

    def getApiCredentials(self):
        with open("betfair_api_credentials.txt") as f:
            application_key = f.readline().strip()
            username = f.readline().strip()
            password = f.readline().strip()
            return application_key, username, password

    def getEvents(self, api, start_date, start_time, end_date, end_time):
        football_event_id = [item.event_type.id for item in api.betting.list_event_types() if item.event_type.name == "Soccer"][0]
        filter = {
            "eventTypeIds": [football_event_id],
            "marketStartTime": {
                "from": "{}T{}:00Z".format(START_DATE, START_TIME),
                "to": "{}T{}:00Z".format(END_DATE, END_TIME)
            }      
        }
        return api.betting.list_events(filter)

    def getMarketIds(self, api, list_of_games):
        game_ids = [event.event.id for event in list_of_games]
        filter = {
            "textQuery" : "CORRECT_SCORE",
            "eventIds": game_ids
        }
        response = api.betting.list_market_catalogue(filter, max_results=200, market_projection=["EVENT"])
        game_list = self.createGameClasses(response)
        return [item.market_id for item in response], game_list

    def processMarkets(self, market_ids):
        market_book = api.betting.list_market_book(market_ids, price_projection={"priceData" : ["EX_BEST_OFFERS"]})
        processed_list = []
        for game in market_book:
            size_list = []
            market_id = game.market_id
            for runner in game.runners:
                try:
                    selection_id = runner.selection_id
                    #0 because it gets 3 values to lay, want only the first one as its the lowest
                    available_to_lay = runner.ex.available_to_lay[0].size
                    price = runner.ex.available_to_lay[0].price
                except IndexError:
                    available_to_lay = 0
                    price = 0
                size_list.append([available_to_lay, selection_id, price])
            processed_list.append([market_id, sorted(size_list, reverse=True)])
        return processed_list

    def updateGameClasses(self, list_with_odds, game_list):
        for game in list_with_odds:
            market_id = game[0]
            runner_odds = game[1]
            for game_class in game_list:
                if game_class.market_id == market_id:
                    game_class.insertRunner(runner_odds)
        return game_list




if __name__ == "__main__": 
    bfInfo = BetfairInformation()
    app_key, username, password = bfInfo.getApiCredentials()
    api = betfairlightweight.APIClient(username, password , app_key)
    api.login_interactive()
    events = bfInfo.getEvents(api, START_DATE, START_TIME, END_DATE, END_TIME)
    #Limit to the top 40
    events = events[40:80]
    market_ids, game_list = bfInfo.getMarketIds(api, events)

    list_with_odds = bfInfo.processMarkets(market_ids)
    game_list = bfInfo.updateGameClasses(list_with_odds, game_list)

    for game in game_list:
        print(game.runner.s01)


