import json
import operator
from time import sleep

class Runner:
    def __init__(self, score, name, backodds, layodds, closeness, liquidity, marketId):
        self.name = name
        self.score = score
        self.backodds = backodds
        self.layodds = layodds
        self.closeness = closeness
        self.liquidity = liquidity
        self.marketId = marketId

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

def getOutcomeFromNumber(good_runners):
    for runner in good_runners:
        if runner.score == 1:
            runner.score = "0:0"
        if runner.score == 2:
            runner.score = "1:0"
        if runner.score == 3:
            runner.score = "1:1"
        if runner.score == 4:
            runner.score = "0:1"
        if runner.score == 5:
            runner.score = "2:0"
        if runner.score == 6:
            runner.score = "2:1"
        if runner.score == 7:
            runner.score = "2:2"
        if runner.score == 8:
            runner.score = "1:2"
        if runner.score == 9:
            runner.score = "0:2"
        if runner.score == 10:
            runner.score = "3:0"
        if runner.score == 11:
            runner.score = "3:1"
        if runner.score == 12:
            runner.score = "3:2"
        if runner.score == 13:
            runner.score = "3:3"
        if runner.score == 14:
            runner.score = "2:3"
        if runner.score == 15:
            runner.score = "1:3"
        if runner.score == 16:
            runner.score = "0:3"
    return good_runners

def checkOdds(bfgame, ssgame):
    runner_list = []
    counter = 0
    #print(ssgame["odds"])
    try:
        for bfodds, ssodds, liquidity in zip(bfgame["odds"], ssgame["odds"], bfgame["liquidity"]):
            counter += 1
            closeness = (1/float(bfodds) - 1/float(ssodds))*100 + 100
            if closeness > 95 and liquidity > 0:
                runner = Runner(counter, bfgame["name"], ssodds, bfodds, round(closeness,2), liquidity, bfgame["marketId"])
                runner_list.append(runner)
        return runner_list
    except:
        pass

while True:
    with open("betfair_output.json") as file:
        betfair_output = json.load(file)

    with open("ss_output.json") as file:
        ss_output = json.load(file)
        
    next_one = False
    good_runners = []
    for bfgame in betfair_output:
        betfair_name = bfgame["name"]
        for ssgame in ss_output:
            game_string = ssgame["name"]
            first_word = game_string.split("-")[0]
            second_word = game_string.split("vs")[1]
            second_word = second_word.replace("-", " ")
            second_word = second_word.strip()
            second_word = second_word.split(" ")[0]
            try:
                if betfair_name.lower().startswith('fc') or betfair_name.lower().startswith('al') or betfair_name.lower().startswith('fk') or betfair_name.lower().split("v")[1].strip().startswith('fc') or betfair_name.lower().split("v")[1].strip().startswith('al') or betfair_name.lower().split("v")[1].strip().startswith('fk'):
                    if betfair_name.split(" ")[1].lower().startswith(game_string.split("-")[1].lower()) and betfair_name.split("v", 1)[1].strip().split(" ")[1].lower().startswith(game_string.split('vs-', 1)[1].split("-")[1].lower()):
                        print("{} -> {}".format(betfair_name, game_string))
                        next_one = True
                        new_runners = checkOdds(bfgame, ssgame)
                        if new_runners:
                            good_runners = good_runners + new_runners
                        break
                elif betfair_name.lower().startswith(first_word.lower()) and betfair_name.lower().split("v")[1].strip().startswith(second_word.lower()) or (first_word.lower().startswith(betfair_name.split(" ")[0].strip().lower()) and second_word.startswith(betfair_name.split('v')[1].strip().lower())):          
                    print("{} -> {}".format(betfair_name, game_string))
                    next_one = True
                    new_runners = checkOdds(bfgame, ssgame)
                    if new_runners:
                        good_runners = good_runners + new_runners
                    break
            except IndexError:
                break
        if next_one == False:
            print("Could not find a match for: {}".format(betfair_name))

    good_runners = sorted(good_runners, key=operator.attrgetter('closeness'), reverse=True)
    good_runners = getOutcomeFromNumber(good_runners)

    json_s = "["
    for runner in good_runners:
        json_s += runner.toJSON()
    json_s = json_s.replace("}{", "},{")
    json_s += "]"

    with open("OM_site/site_input.json", "w") as file:
        file.write(json_s)
    sleep(60)
