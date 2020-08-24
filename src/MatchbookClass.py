from matchbook.apiclient import APIClient
from datetime import datetime
import pytz

from logger_manager import *

class OutrightRunner:
    def __init__(self, r1, rX, r2):
        self.r1 = r1
        self.rX = rX
        self.r2 = r2

class MatchbookGame:
    def __init__(self, name, event_id, day_, time_):
        self.name = name
        self.event_id = event_id
        self.date = day_
        self.time = time_
        self.outrights = None
        self.correct_score = None

def processDate(event_date):
    date = event_date.split("T")[0]
    time = event_date.split("T")[1].split(".")[0]
    date = datetime.strptime("{} {}".format(date, time), "%Y-%m-%d %H:%M:%S")
    #Convert timezone
    amsterdam = pytz.timezone('Europe/Amsterdam')
    date = pytz.utc.localize(date).astimezone(amsterdam)
    event_date = date.strftime("%d-%m")
    time = date.strftime("%H:%M:%S")
    return event_date, time

def getMatchbookGames():
    mb = APIClient('tKofschip', 'N1hj001*UJZwIkx$')
    mb.login()

    game_list = []

    sports = mb.reference_data.get_sports()
    football_id = [s['id'] for s in sports if s['name']=='Soccer'][0]
    football_events = mb.market_data.get_events(sport_ids=football_id, price_depth=1, minimum_liquidity=50)
    for event in football_events:
        try:
            event_name = event["name"]
            event_id = event['id']
            event_date = event["start"]
            if event["markets"][0]["live"] == True:
                #Live game, skip
                continue

            date, time = processDate(event_date)
            game = MatchbookGame(event_name, event_id, date, time)

            all_markets = mb.market_data.get_markets(event_id)
            try:
                #correct_score_market_id = [m['id'] for m in all_markets if m['market-type']=='correct_score'][0]
                outright_market_id = [m['id'] for m in all_markets if m['market-type']=='one_x_two'][0]
            except IndexError:
                #Doesn't have the market
                continue
            if outright_market_id:
                market_data = mb.market_data.get_runners(event_id, outright_market_id)
                team1 = market_data["runners"][0]["name"]
                team2 = market_data["runners"][1]["name"]

                #r1 = [liquidity, odds]
                try:
                    r1 = [round([m["available-amount"] for m in market_data["runners"][0]["prices"] if m["side"] == "lay"][0], 2), round([m["decimal-odds"] for m in market_data["runners"][0]["prices"] if m["side"] == "lay"][0], 2)]
                    rX = [round([m["available-amount"] for m in market_data["runners"][2]["prices"] if m["side"] == "lay"][0], 2), round([m["decimal-odds"] for m in market_data["runners"][2]["prices"] if m["side"] == "lay"][0], 2)]
                    r2 = [round([m["available-amount"] for m in market_data["runners"][1]["prices"] if m["side"] == "lay"][0], 2), round([m["decimal-odds"] for m in market_data["runners"][1]["prices"] if m["side"] == "lay"][0], 2)]
                except IndexError:
                    continue

                #print("Name: {} v {}".format(team1, team2))
                #print("r1: {} rX: {} r2: {}".format(r1[1], rX[1], r2[1]))
                #print("r1: €{} rX: €{} r2: €{}".format(r1[0], rX[0], r2[0]))
                runner = OutrightRunner(r1, rX, r2)
                game.outrights = runner
                game_list.append(game)
        except Exception as e:
            logger.debug(e)
    return game_list


if __name__ == "__main__":
    game_list = getMatchbookGames()
    for game in game_list:
        print("{:<40} {:>7} {:>7}  {:>7} {:>7} {:>7}  {:>7}".format(game.name, game.outrights.r1[1], game.outrights.rX[1], game.outrights.r2[1], game.outrights.r1[0], game.outrights.rX[0], game.outrights.r2[0]))
