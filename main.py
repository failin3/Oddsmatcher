from BetfairClass import *
from spinsports_scraper import *
from scraper_888sport import *
from fuzzywuzzy import fuzz
import operator
import pymysql.cursors


class OddsmatcherEntry:
    def __init__(self, name, bookmaker_odds, exchange_odds, exchange_liquidity, runner_id, closeness):
        self.name = name
        self.bkma_odds = bookmaker_odds
        self.exch_odds = exchange_odds
        self.exch_liquidity = exchange_liquidity
        self.runner_id = runner_id
        self.closeness = closeness

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
    return (1/float(ss_odds) - 1/float(bf_odds))*100 + 100

def compareOdds(ss_games, bookmaker_games, set_closeness=95, set_odds=30):
    """Compares the odds of all spinsports games in the list ss_games
    To those of the bookmaker selected.
    First checks whether the names of the two teams are similar, then it calculates the closenss of the odds
    Returns a list of the OddsmatcherEntrys that are within a given closesness"""
    good_odds = []
    for ss_game in ss_games:
        for bf_game in bookmaker_games:
            if fuzz.ratio(ss_game.name, bf_game.name) > 50:
                print("{} == {}".format(ss_game.name, bf_game.name))
                bf_runner = bf_game.correct_score
                
                vars_in_bf = list(vars(bf_runner).items())
                vars_in_ss = list(vars(ss_game).items())[1:]

                for bf_data, ss_odds in zip(vars_in_bf, vars_in_ss):
                    bf_odds = bf_data[1][1]
                    liquidity = bf_data[1][0]
                    score = bf_data[0]
                    if (bf_odds != None) and (ss_odds[1] != None):
                        closeness = getCloseness(bf_odds, ss_odds[1])
                        if closeness > set_closeness and float(ss_odds[1]) < set_odds:
                            good_odds.append(OddsmatcherEntry(bf_game.name, ss_odds[1], bf_odds, liquidity, score, closeness))
    good_odds = sorted(good_odds, key=operator.attrgetter('closeness'))
    return good_odds

def insertData(oddsmatcher_games):
    connection = pymysql.connect(host='185.104.29.14',
                             user='u80189p74860_oddsmatcher',
                             password='Kq90*r%XXlEXaUIvoxwo',
                             db='u80189p74860_oddsmatcher',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            sql = "DELETE FROM Odds"
            cursor.execute(sql)
        with connection.cursor() as cursor:                        
            for game in oddsmatcher_games:
                back_stake = 300
                commission = 4/100
                gains_bookmaker = back_stake*float(game.bkma_odds)
                lay_stake = (gains_bookmaker-800-back_stake)/(float(game.exch_odds)-1)
                exchange_lay_wins = lay_stake*(1-commission)-back_stake
                sql = "INSERT INTO Spinsports (MatchName, ExchangeOdds, BookmakerOdds, Closeness, Date, Liquidity, Loss) VALUES (%s,%s,%s,%s,%s,%s,%s)" 
                cursor.execute(sql, (game.name, game.exch_odds, game.bkma_odds, game.closeness, 1, game.exch_liquidity, exchange_lay_wins))
        connection.commit()
    finally:
        connection.close()

spinsports_games = getSpinsportsGames(10)
#list888sport = get888sportData()
betfair_games = getGames()
listSpinsports = compareOdds(spinsports_games, betfair_games)
#list888sport = compareOdds(list888sport, betfair_games)
insertData(listSpinsports)


# for game in list888sport:
#     # back_stake = 300
#     # commission = 4/100
#     # gains_bookmaker = back_stake*float(game.bkma_odds)
#     # lay_stake = (gains_bookmaker-800-back_stake)/(float(game.exch_odds)-1)
#     # exchange_lay_wins = lay_stake*(1-commission)-back_stake
#     print("{}: {} - {}".format(game.name, game.bkma_odds, game.exch_odds))





