from pyvirtualdisplay import Display
from selenium.common.exceptions import WebDriverException
from time import sleep
from fuzzywuzzy import fuzz
import operator
import pymysql.cursors
import argparse

from logger_manager import *

from BetfairClass import *
from MatchbookClass import *

from spinsports_scraper import *
from scraper_888sport import *
from scraper_betsson import *
from scraper_betrebels import *
from scraper_neobet import *
from scraper_intertops import *
from scraper_bet90 import *
from scraper_betathome import *
from scraper_unibet import *



#Parse command line arguments
parser = argparse.ArgumentParser(description = "Oddsmatcher backend")
parser.add_argument("-p", "--production", help = "Runs oddsmatcher without display", action='store_true')
parser.add_argument("-l", "--logs", help = "Show more verbose logging", action='store_true')
parser.add_argument("-s", "--schedule", help = "Change the schedule to be ran, default is schedule 1", type=int)

argument = parser.parse_args()


def startChromeDriver():
    if argument.production:
        display = Display(visible=0, size=(800, 600))
        display.start()
    driver = webdriver.Chrome("bin/chromedriver")
    return driver

class OddsmatcherEntry:
    def __init__(self, name, bookmaker_odds, exchange_odds, exchange_liquidity, runner_id, closeness, date, time, bet, exchange_id):
        self.name = name
        self.bkma_odds = bookmaker_odds
        self.exch_odds = exchange_odds
        self.exch_liquidity = exchange_liquidity
        self.runner_id = runner_id
        self.closeness = closeness
        self.date = date
        self.time = time
        self.bet = bet
        self.exchange_id = exchange_id

def getSpinsportsGames(nr_of_games, driver):
    url = "/en/sports/soccer/germany-1-bundesliga/20200224/eintracht-frankfurt-vs-union-berlin/"
    match_url = "https://spinsportsmga.spinpalace.com/en/sports/soccer/"
    browse_url = "https://spinsportsmga.spinpalace.com/en/sports/"

    url_list = getMatchUrls(browse_url, driver)[:nr_of_games]
    spinsports_games = []
    for url in url_list:
        game = parseMatch(url, driver)
        if game != None:
            logger.debug("Parsed {}".format(game.name))
            spinsports_games.append(game)
    return spinsports_games

def getCloseness(ss_odds, bf_odds):
    return (1/float(ss_odds) - 1/float(bf_odds))*100 + 100

def compareNames(bookmaker_game, betfair_name, exchange_split):
    try:
        Str1 = bookmaker_game
        Str2 = betfair_name
        Str1 = Str1.replace("-", " ").lower()
        Str2  = Str2.lower()
        Str1_first = Str1.split(' vs ')[0].strip()
        Str1_second = Str1.split(' vs ')[1].strip()
        Str2_first = Str2.split(exchange_split)[0].strip()
        Str2_second = Str2.split(exchange_split)[1].strip()

        reference = ["man utd", "man city", "man united"]
        replace = ["manchester united", "manchester city", "manchester united"]
        
        for ref, rep in zip(reference, replace):
            if ref in Str1_first:
                Str1_first = Str1_first.replace(ref, rep)
            if ref in Str1_second:
                Str1_second = Str1_second.replace(ref, rep)
            if ref in Str2_first:
                Str2_first = Str2_first.replace(ref, rep)
            if ref in Str2_second:
                Str2_second = Str2_second.replace(ref, rep)
        Str1 = "{} vs {}".format(Str1_first, Str1_second)
        Str2 = "{} vs {}".format(Str2_first, Str2_second)

        #Ignore women football on Unibet
        if "(W)" in Str1 or "(W)" in Str2:
            return False

        if (Str1_first in Str2_first or Str2_first in Str1_first) and (Str1_second in Str2_second or Str2_second in Str1_second):
            return True
        else:
            Ratio = fuzz.ratio(Str1,Str2)
            if Ratio > 85:
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

def compareOdds(ss_games, bookmaker_games, market, set_closeness=95, set_odds=30, exchange_split=" v "):
    """Compares the odds of all spinsports games in the list ss_games
    To those of the bookmaker selected.
    First checks whether the names of the two teams are similar, then it calculates the closenss of the odds
    Returns a list of the OddsmatcherEntrys that are within a given closesness"""
    assert(market == "correct_score" or market == "outrights")
    good_odds = []
    for ss_game in ss_games:
        for bf_game in bookmaker_games:
            try:
                if compareNames(ss_game.name, bf_game.name, exchange_split):
                    logger.debug("{} == {} score: {}".format(ss_game.name, bf_game.name, fuzz.ratio(ss_game.name, bf_game.name)))
                    if market == "correct_score":
                        bf_runner = bf_game.correct_score
                    elif market == "outrights":
                        bf_runner = bf_game.outrights
                    
                    vars_in_bf = list(vars(bf_runner).items())
                    vars_in_ss = list(vars(ss_game).items())[1:]

                    for bf_data, ss_odds in zip(vars_in_bf, vars_in_ss):
                        #Sometimes there is 0 available on betfair
                        if bf_data[1] == None:
                            continue
                        #Or betfair LOL
                        if ss_odds[1] == None:
                            continue
                        bf_odds = bf_data[1][1]
                        liquidity = bf_data[1][0]
                        score = bf_data[0]
                        if (bf_odds != None) and (ss_odds[1] != None):
                            closeness = getCloseness(bf_odds, ss_odds[1])
                            bet = makeVarReadable(ss_odds[0], market)
                            if closeness > set_closeness and float(bf_odds) < set_odds:
                                if bet == "r1":
                                    bet = bf_game.name.split(exchange_split)[0]
                                elif bet == "rX":
                                    bet = "Draw"
                                elif bet == "r2":
                                    bet = bf_game.name.split(exchange_split)[1]
                                good_odds.append(OddsmatcherEntry(bf_game.name, ss_odds[1], bf_odds, liquidity, score, closeness, bf_game.date, bf_game.time, bet, bf_game.event_id))
            except Exception as e:
                logger.debug(e)
    good_odds = sorted(good_odds, key=operator.attrgetter('closeness'))
    return good_odds

def insertData(oddsmatcher_games, table_name):
    try:
        if len(oddsmatcher_games) == 0:
            logger.debug("Table {} insert is empty".format(table_name))
        connection = pymysql.connect(host='185.104.29.14',
                             user='u80189p74860_oddsmatcher',
                             password='Kq90*r%XXlEXaUIvoxwo',
                             db='u80189p74860_oddsmatcher',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
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
                if "_Matchbook" in table_name:
                    url = "https://www.matchbook.com/events/soccer/{}".format(game.exchange_id)
                else: 
                    url = "https://www.betfair.com/exchange/plus/en/football/--/---{}".format(game.exchange_id)
                sql = "INSERT INTO {} (MatchName, ExchangeOdds, BookmakerOdds, Closeness, Date, Time, Liquidity, Loss, Bet, Url) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)".format(table_name)
                cursor.execute(sql, (game.name, game.exch_odds, game.bkma_odds, game.closeness, game.date, game.time, game.exch_liquidity, exchange_lay_wins, game.bet, url))
                logger.debug("Inserted game: {} into database succesfully".format(game.name))
        connection.commit()
    except Exception as e:
        logger.error("MySQL error: {}".format(e))
    finally:
        connection.close()

def compareAndInsert(bookmaker_games, betfair_games, matchbook_games, odds_type, bf_database_name, mb_database_name):
    logger.info("Comparing odds")
    try:
        compared_list = compareOdds(bookmaker_games, betfair_games, odds_type, exchange_split=" v ")
        compared_list_matchbook = compareOdds(bookmaker_games, matchbook_games, odds_type, exchange_split=" vs ")
    except Exception as e:
        compared_list = []
        logger.error(e)
    logger.info("Inserting into database")
    insertData(compared_list, bf_database_name)
    insertData(compared_list_matchbook, mb_database_name)

def runSpinsports(driver):
    logger.info("Collecting spinsports data")
    try:
        bookmaker_games = getSpinsportsGames(15, driver)
    except WebDriverException:
        #Test if chrome has really crashed
        try:
            driver.title
            logger.debug("WebDriverException, but chrome didn't crash")
        except WebDriverException:
            logger.warning("Chrome has crashed, reopening")
            driver = startChromeDriver()
            bookmaker_games = getSpinsportsGames(15, driver)
    except Exception as e:
        logger.error("Some other error with spinsports: {}".format(e))
        return getGames(), driver
    logger.info("Collecting exchange info")
    betfair_games = getGames()
    logger.info("Comparing odds")
    try:
        compared_list = compareOdds(bookmaker_games, betfair_games, "correct_score")
    except Exception as e:
        logger.error(e)
        return betfair_games, driver
    logger.info("Inserting into database")
    insertData(compared_list, "Spinsports")
    return betfair_games, driver

def runBetsson(driver, betfair_games, matchbook_games):
    logger.info("Collecting Betsson group data")
    #Try 3 times
    for _ in range(3):
        betsson_games = []
        try:
            betsson_games = parseBetsson(driver)
            break
        except WebDriverException:
            try:
                driver.title
                logger.debug("WebDriverException, but chrome didn't crash")
            except WebDriverException:
                logger.warning("Chrome has crashed, reopening")
                driver = startChromeDriver()
        except Exception as e:
            logger.error("Betsson:")
            logger.error(e)
    for _ in range(3):
        betsafe_games = []
        try:
            betsafe_games = parseBetsafe(driver)
            break
        except WebDriverException:
            try:
                driver.title
                logger.debug("WebDriverException, but chrome didn't crash")
            except WebDriverException:
                logger.warning("Chrome has crashed, reopening")
                driver = startChromeDriver()
        except Exception as e:
            logger.error("Betsafe:")
            logger.error(e)
    for _ in range(3):
        casinowinner_games = []
        try:
            casinowinner_games = parseCasinowinner(driver)
            break
        except WebDriverException:
            try:
                driver.title
                logger.debug("WebDriverException, but chrome didn't crash")
            except WebDriverException:
                logger.warning("Chrome has crashed, reopening")
                driver = startChromeDriver()
        except Exception as e:
            logger.error("Casinowinner:")
            logger.error(e)
    logger.info("Betsson:")
    compareAndInsert(betsson_games, betfair_games, matchbook_games, "outrights", "Betsson", "Betsson_Matchbook")
    logger.info("Betsafe:")
    compareAndInsert(betsafe_games, betfair_games, matchbook_games, "outrights", "Betsafe", "Betsafe_Matchbook")
    logger.info("Casinowinner:")
    compareAndInsert(casinowinner_games, betfair_games, matchbook_games, "outrights", "Casinowinner", "Casinowinner_Matchbook")
    return driver

def run888sport(driver, betfair_games, matchbook_games):
    logger.info("Collecting 888sport data")
    for _ in range(3):
        bookmaker_games = []
        try:
            bookmaker_games = get888sportData(driver)
            break
        except WebDriverException:
            try:
                driver.title
                logger.debug("WebDriverException, but chrome didn't crash")
            except WebDriverException:
                logger.warning("Chrome has crashed, reopening")
                driver = startChromeDriver()
        except Exception as e:
            logger.error(e)
    compareAndInsert(bookmaker_games, betfair_games, matchbook_games, "outrights", "888sport", "888sport_Matchbook")
    return driver

def runBetrebels(driver, betfair_games, matchbook_games):
    logger.info("Collecting betrebels data")
    for _ in range(3):
        bookmaker_games = []
        try:
            bookmaker_games = parseBetrebels(driver)
            break
        except WebDriverException:
            try:
                driver.title
                logger.debug("WebDriverException, but chrome didn't crash")
            except WebDriverException:
                logger.warning("Chrome has crashed, reopening")
                driver = startChromeDriver()
        except Exception as e:
            logger.error(e)
    compareAndInsert(bookmaker_games, betfair_games, matchbook_games, "outrights", "Betrebels", "Betrebels_Matchbook")
    return driver

def runNeobet(driver, betfair_games, matchbook_games):
    logger.info("Collecting neobet data")
    for _ in range(3):
        bookmaker_games = []
        try:
            bookmaker_games = parseNeobet(driver)
            break
        except WebDriverException:
            try:
                driver.title
                logger.debug("WebDriverException, but chrome didn't crash")
            except WebDriverException:
                logger.warning("Chrome has crashed, reopening")
                driver = startChromeDriver()
        except Exception as e:
            logger.error(e)
    compareAndInsert(bookmaker_games, betfair_games, matchbook_games, "outrights", "Neobet", "Neobet_Matchbook")
    return driver

def runIntertops(driver, betfair_games ,matchbook_games):
    logger.info("Collecting intertops data")
    for _ in range(3):
        bookmaker_games = []
        try:
            bookmaker_games = parseIntertops(driver)
            break
        except WebDriverException:
            try:
                driver.title
                logger.debug("WebDriverException, but chrome didn't crash")
            except WebDriverException:
                logger.warning("Chrome has crashed, reopening")
                driver = startChromeDriver()
        except Exception as e:
            logger.error(e)
    compareAndInsert(bookmaker_games, betfair_games, matchbook_games, "outrights", "Intertops", "Intertops_Matchbook")
    return driver

def runBet90(driver, betfair_games, matchbook_games):
    logger.info("Collecting bet90 data")
    for _ in range(3):
        bookmaker_games = []
        try:
            bookmaker_games = parseBet90(driver)
            break
        except WebDriverException:
            try:
                driver.title
                logger.debug("WebDriverException, but chrome didn't crash")
            except WebDriverException:
                logger.warning("Chrome has crashed, reopening")
                driver = startChromeDriver()
        except Exception as e:
            logger.error(e)
    compareAndInsert(bookmaker_games, betfair_games, matchbook_games, "outrights", "Bet90", "Bet90_Matchbook")
    return driver

def runBetathome(driver, betfair_games, matchbook_games):
    logger.info("Collecting betathome data")
    for _ in range(3):
        bookmaker_games = []
        try:
            bookmaker_games = parseBetathome(driver)
            break
        except WebDriverException:
            try:
                driver.title
                logger.debug("WebDriverException, but chrome didn't crash")
            except WebDriverException:
                logger.warning("Chrome has crashed, reopening")
                driver = startChromeDriver()
        except Exception as e:
            logger.error(e)
    compareAndInsert(bookmaker_games, betfair_games, matchbook_games, "outrights", "Betathome", "Betathome_Matchbook")
    return driver

def runUnibet(driver, betfair_games, matchbook_games):
    logger.info("Collecting unibet data")
    for _ in range(3):
        bookmaker_games = []
        try:
            bookmaker_games = parseUnibet(driver)
            break
        except WebDriverException:
            try:
                driver.title
                logger.debug("WebDriverException, but chrome didn't crash")
            except WebDriverException:
                logger.warning("Chrome has crashed, reopening")
                driver = startChromeDriver()
        except Exception as e:
            logger.error(e)
    compareAndInsert(bookmaker_games, betfair_games, matchbook_games, "outrights", "Unibet", "Unibet_Matchbook")
    return driver


logger.info("Starting driver")
driver = startChromeDriver()

def schedule1(driver):
    betfair_games, driver = runSpinsports(driver)
    matchbook_games = getMatchbookGames()
    driver = runBetsson(driver, betfair_games, matchbook_games)
    driver = run888sport(driver, betfair_games, matchbook_games)
    driver = runBetrebels(driver, betfair_games, matchbook_games)
    driver = runNeobet(driver, betfair_games, matchbook_games)
    return driver

def schedule2(driver):
    betfair_games = getGames()
    matchbook_games = getMatchbookGames()
    driver = runUnibet(driver, betfair_games, matchbook_games)
    driver = runBetathome(driver, betfair_games, matchbook_games)
    driver = runIntertops(driver, betfair_games, matchbook_games)
    driver = runBet90(driver, betfair_games, matchbook_games)
    return driver

def schedule3(driver):
    betfair_games = getGames()
    matchbook_games = getMatchbookGames()
    driver = run888sport(driver, betfair_games, matchbook_games)
    return driver


while True:
    if not argument.schedule:
        #Default
        driver = schedule1(driver)
    else:
        if argument.schedule == 1:
            driver = schedule1(driver)
        elif argument.schedule == 2:
            driver = schedule2(driver)
        elif argument.schedule == 3:
            #Debug schedule
            driver = schedule3(driver)
        else:
            logger.info("This schedule does not exist")
            break
    
    #schedule1(driver)
    #schedule2(driver)

    #logger.info("Sleeping for 1 minute")
    #sleep(60*1)







