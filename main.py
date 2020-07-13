from pyvirtualdisplay import Display
from selenium.common.exceptions import WebDriverException
from time import sleep
from fuzzywuzzy import fuzz
import operator
import pymysql.cursors
import argparse

from BetfairClass import *
from spinsports_scraper import *
from scraper_888sport import *
from scraper_betsson import *
from scraper_betrebels import *
from scraper_neobet import *



#Parse command line arguments
parser = argparse.ArgumentParser(description = "Oddsmatcher backend")
parser.add_argument("-p", "--production", help = "Runs oddsmatcher without display", action='store_true')
parser.add_argument("-l", "--logs", help = "Show more verbose logging", action='store_true')

argument = parser.parse_args()

def startChromeDriver():
    if argument.production:
        display = Display(visible=0, size=(800, 600))
        display.start()
    driver = webdriver.Chrome("bin/chromedriver")
    return driver

class OddsmatcherEntry:
    def __init__(self, name, bookmaker_odds, exchange_odds, exchange_liquidity, runner_id, closeness, date, time, bet):
        self.name = name
        self.bkma_odds = bookmaker_odds
        self.exch_odds = exchange_odds
        self.exch_liquidity = exchange_liquidity
        self.runner_id = runner_id
        self.closeness = closeness
        self.date = date
        self.time = time
        self.bet = bet

def getSpinsportsGames(nr_of_games, driver):
    url = "/en/sports/soccer/germany-1-bundesliga/20200224/eintracht-frankfurt-vs-union-berlin/"
    match_url = "https://spinsportsmga.spinpalace.com/en/sports/soccer/"
    browse_url = "https://spinsportsmga.spinpalace.com/en/sports/"

    url_list = getMatchUrls(browse_url, driver)[:nr_of_games]
    spinsports_games = []
    for url in url_list:
        game = parseMatch(url, driver, argument.logs)
        if argument.logs:
            print("Parsed {}".format(game.name))
        if game != None:
            spinsports_games.append(game)
    return spinsports_games

def getCloseness(ss_odds, bf_odds):
    return (1/float(ss_odds) - 1/float(bf_odds))*100 + 100

def compareNames(bookmaker_game, betfair_name):
    try:
        Str1 = bookmaker_game
        Str2 = betfair_name
        Str1 = Str1.replace("-", " ").lower()
        Str2  = Str2.lower()
        Str1_first = Str1.split(' vs ')[0].strip()
        Str1_second = Str1.split(' vs ')[1].strip()
        Str2_first = Str2.split(' v ')[0].strip()
        Str2_second = Str2.split(' v ')[1].strip()
        if (Str1_first in Str2_first or Str2_first in Str1_first) and (Str1_second in Str2_second or Str2_second in Str1_second):
            return True
        else:
            Ratio = fuzz.ratio(Str1,Str2)
            if Ratio > 80:
                return True
        return False
    except IndexError:
        return False

def makeVarReadable(var, market):
    if market == "correct_score":
        score1 = var[1]
        score2 = var[2]
        return score1 + "-" + score2
    if market == "outrights":
        return var

def compareOdds(ss_games, bookmaker_games, market, set_closeness=95, set_odds=30):
    """Compares the odds of all spinsports games in the list ss_games
    To those of the bookmaker selected.
    First checks whether the names of the two teams are similar, then it calculates the closenss of the odds
    Returns a list of the OddsmatcherEntrys that are within a given closesness"""
    assert(market == "correct_score" or market == "outrights")
    good_odds = []
    for ss_game in ss_games:
        for bf_game in bookmaker_games:
            if compareNames(ss_game.name, bf_game.name):
                if argument.logs:
                    print("{} == {} score: {}".format(ss_game.name, bf_game.name, fuzz.ratio(ss_game.name, bf_game.name)))
                if market == "correct_score":
                    bf_runner = bf_game.correct_score
                elif market == "outrights":
                    bf_runner = bf_game.outrights
                
                vars_in_bf = list(vars(bf_runner).items())
                vars_in_ss = list(vars(ss_game).items())[1:]

                for bf_data, ss_odds in zip(vars_in_bf, vars_in_ss):
                    bf_odds = bf_data[1][1]
                    liquidity = bf_data[1][0]
                    score = bf_data[0]
                    if (bf_odds != None) and (ss_odds[1] != None):
                        closeness = getCloseness(bf_odds, ss_odds[1])
                        bet = makeVarReadable(ss_odds[0], market)
                        if closeness > set_closeness and float(bf_odds) < set_odds:
                            if bet == "r1":
                                bet = bf_game.name.split(" v ")[0]
                            elif bet == "rX":
                                bet = "Draw"
                            elif bet == "r2":
                                bet = bf_game.name.split(" v ")[1]
                            good_odds.append(OddsmatcherEntry(bf_game.name, ss_odds[1], bf_odds, liquidity, score, closeness, bf_game.date, bf_game.time, bet))
    good_odds = sorted(good_odds, key=operator.attrgetter('closeness'))
    return good_odds

def insertData(oddsmatcher_games, table_name):
    connection = pymysql.connect(host='185.104.29.14',
                             user='u80189p74860_oddsmatcher',
                             password='Kq90*r%XXlEXaUIvoxwo',
                             db='u80189p74860_oddsmatcher',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            sql = "DELETE FROM {}".format(table_name)
            cursor.execute(sql)
        with connection.cursor() as cursor:                        
            for game in oddsmatcher_games:
                back_stake = 300
                commission = 4/100
                gains_bookmaker = back_stake*float(game.bkma_odds)
                lay_stake = (gains_bookmaker-800-back_stake)/(float(game.exch_odds)-1)
                exchange_lay_wins = lay_stake*(1-commission)-back_stake
                sql = "INSERT INTO {} (MatchName, ExchangeOdds, BookmakerOdds, Closeness, Date, Time, Liquidity, Loss, Bet) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)" .format(table_name)
                cursor.execute(sql, (game.name, game.exch_odds, game.bkma_odds, game.closeness, game.date, game.time, game.exch_liquidity, exchange_lay_wins, game.bet))
        connection.commit()
    finally:
        connection.close()

def runSpinsports(driver):
    print("Collecting spinsports data")
    try:
        bookmaker_games = getSpinsportsGames(15, driver)
    except WebDriverException:
        print("Chrome has crashed, reopening")
        driver = startChromeDriver()
        bookmaker_games = getSpinsportsGames(15, driver)
    except:
        print("Some other error with spinsports")
        return getGames(), driver
    print("Collecting exchange info")
    betfair_games = getGames()
    print("Comparing odds")
    try:
        compared_list = compareOdds(bookmaker_games, betfair_games, "correct_score")
    except Exception as e:
        print(e)
        return betfair_games, driver
    print("Inserting into database")
    insertData(compared_list, "Spinsports")
    return betfair_games, driver

def runBetsson(driver, betfair_games):
    print("Collecting Betsson group data")
    #Try 3 times
    for _ in range(3):
        betsson_games = []
        try:
            betsson_games = parseBetsson(driver)
            break
        except WebDriverException:
            print("Chrome has crashed, reopening")
            driver = startChromeDriver()
        except Exception as e:
            print("Betsson:")
            print(e)
    for _ in range(3):
        betsafe_games = []
        try:
            betsafe_games = parseBetsafe(driver)
            break
        except WebDriverException:
            print("Chrome has crashed, reopening")
            driver = startChromeDriver()
        except Exception as e:
            print("Betsafe:")
            print(e)
    for _ in range(3):
        casinowinner_games = []
        try:
            casinowinner_games = parseCasinowinner(driver)
            break
        except WebDriverException:
            print("Chrome has crashed, reopening")
            driver = startChromeDriver()
        except Exception as e:
            print("Casinowinner:")
            print(e)
    print("Comparing games, and uploading")
    print("Betsson")
    try:
        betsson_games = compareOdds(betsson_games, betfair_games, "outrights")
        insertData(betsson_games, "Betsson")
    except:
        print("Probably float by zero error, skipping for now")
    print("Betsafe")
    try:
        betsafe_games = compareOdds(betsafe_games, betfair_games, "outrights")
        insertData(betsafe_games, "Betsafe")
    except:
        print("Probably float by zero error, skipping for now")
    print("Casinowinner")
    try:
        casinowinner_games = compareOdds(casinowinner_games, betfair_games, "outrights")
        insertData(casinowinner_games, "Casinowinner")
    except:
        print("Probably float by zero error, skipping for now")
    return driver

def run888sport(driver, betfair_games):
    print("Collecting 888sport data")
    for _ in range(3):
        bookmaker_games = []
        try:
            bookmaker_games = get888sportData(driver)
            break
        except WebDriverException:
            print("Chrome has crashed, reopening")
            driver = startChromeDriver()
        except:
            print("Some problem with 888sport again")
            return driver
    print("Comparing games, and uploading")
    try:
        compared_list = compareOdds(bookmaker_games, betfair_games, "outrights")
    except Exception as e:
        print(e)
    print("Inserting into database")
    insertData(compared_list, "888sport")
    return driver

def runBetrebels(driver, betfair_games):
    print("Collecting betrebels data")
    for _ in range(3):
        bookmaker_games = []
        try:
            bookmaker_games = parseBetrebels(driver)
            break
        except WebDriverException:
            print("Chrome has crashed, reopening")
            driver = startChromeDriver()
        except Exception as e:
            print(e)
    print("Comparing odds")
    try:
        compared_list = compareOdds(bookmaker_games, betfair_games, "outrights")
    except Exception as e:
        print(e)
    print("Inserting into database")
    insertData(compared_list, "Betrebels")
    return driver

def runNeobet(driver, betfair_games):
    print("Collecting neobet data")
    for _ in range(3):
        bookmaker_games = []
        try:
            bookmaker_games = parseNeobet(driver)
            break
        except WebDriverException:
            print("Chrome has crashed, reopening")
            driver = startChromeDriver()
        except Exception as e:
            print(e)
    print("Comparing odds")
    try:
        compared_list = compareOdds(bookmaker_games, betfair_games, "outrights")
    except Exception as e:
        print(e)
    print("Inserting into database")
    insertData(compared_list, "Neobet")
    return driver

print("Starting driver")
driver = startChromeDriver()


while True:
    #first spinsports
    betfair_games, driver = runSpinsports(driver)
    #betfair_games = getGames()
    driver = runBetsson(driver, betfair_games)
    #driver = run888sport(driver, betfair_games)
    driver = runBetrebels(driver, betfair_games)
    driver = runNeobet(driver, betfair_games)
    
    print("Sleeping for 1 minute")
    sleep(60*1)







