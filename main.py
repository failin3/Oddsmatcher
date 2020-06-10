from BetfairInformation import *
from spinsports_scraper import *
from scraper_888sport import *
from fuzzywuzzy import fuzz
import operator


class OddsmatcherEntry:
    def __init__(self, name, bookmaker_odds, exchange_odds, exchange_liquidity, runner_id, closeness):
        self.name = name
        self.bkma_odds = bookmaker_odds
        self.exch_odds = exchange_odds
        self.exch_liquidity = exchange_liquidity
        self.runner_id = runner_id
        self.closeness = closeness

def getBetfairGames():
    bfInfo = BetfairInformation()
    app_key, username, password = bfInfo.getApiCredentials()
    api = betfairlightweight.APIClient(username, password , app_key)
    api.login_interactive()
    events = bfInfo.getEvents(api, START_DATE, START_TIME, END_DATE, END_TIME)
    #Limit to the top 40
    events = events[:40]
    market_ids, game_list = bfInfo.getMarketIds(api, events)

    list_with_odds = bfInfo.processMarkets(api, market_ids)
    game_list = bfInfo.updateGameClasses(list_with_odds, game_list)

    return game_list

def getSpinsportsGames(nr_of_games):
    url = "/en/sports/soccer/germany-1-bundesliga/20200224/eintracht-frankfurt-vs-union-berlin/"
    match_url = "https://spinsportsmga.spinpalace.com/en/sports/soccer/"
    browse_url = "https://spinsportsmga.spinpalace.com/en/sports/"

    driver = webdriver.Chrome("bin/chromedriver")

    url_list = getMatchUrls(browse_url, driver)[:nr_of_games]
    spinsports_games = []
    for url in url_list:
        game = parseMatch(url, driver)
        spinsports_games.append(game)
    return spinsports_games

def getCloseness(ss_odds, bf_odds):
    return (1/float(bf_odds) - 1/float(ss_odds))*100 + 100

def compareSpinsports(ss_games, bookmaker_games, set_closeness=95):
    """Compares the odds of all spinsports games in the list ss_games
    To those of the bookmaker selected.
    First checks whether the names of the two teams are similar, then it calculates the closenss of the odds
    Returns a list of the OddsmatcherEntrys that are within a given closesness"""
    good_odds = []
    for ss_game in ss_games:
        for bf_game in bookmaker_games:
            if fuzz.ratio(ss_game.name, bf_game.name) > 50:
                print("{} == {}".format(ss_game.name, bf_game.name))
                bf_runner = bf_game.runner
                
                vars_in_bf = list(vars(bf_runner).items())
                vars_in_ss = list(vars(ss_game).items())[1:]

                for bf_data, ss_odds in zip(vars_in_bf, vars_in_ss):
                    bf_odds = bf_data[1][1]
                    liquidity = bf_data[1][0]
                    score = bf_data[0]
                    if (bf_odds != None) and (ss_odds[1] != None):
                        closeness = getCloseness(bf_odds, ss_odds[1])
                        if closeness > set_closeness:
                            good_odds.append(OddsmatcherEntry(bf_game.name, ss_odds[1], bf_odds, liquidity, score, closeness))
    good_ss_odds = sorted(good_ss_odds, key=operator.attrgetter('closeness'))
    return good_odds


spinsports_games = getSpinsportsGames(2)
betfair_games = getBetfairGames()
#good_ss_odds = compareSpinsports(spinsports_games, betfair_games)
list888sport = get888sportData()

# for runner in good_ss_odds:
#     print("{} {}: {} - {}".format(runner.name, runner.runner_id, runner.bkma_odds, runner.exch_odds))

for game in list888sport:
    print("{}: 1: {} X: {}: 2{}".format(game.name, game.r1, game.rX, game.r2))





