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
    counter = 1
    print(ssgame["odds"])
    try:
        for bfodds, ssodds, liquidity in zip(bfgame["odds"], ssgame["odds"], bfgame["liquidity"]):
            closeness = (1/float(bfodds) - 1/float(ssodds))*100 + 100
            if closeness > 95:
                runner = Runner(counter, bfgame["name"], ssodds, bfodds, round(closeness,2), liquidity, bfgame["marketId"])
                runner_list.append(runner)
                counter += 1
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

            if first_word in betfair_name.lower() and second_word in betfair_name.lower():
                print("SUCCESS: {}".format(game_string))
                next_one = True
                new_runners = checkOdds(bfgame, ssgame)
                if new_runners:
                    good_runners = good_runners + new_runners
                break
        if next_one == False:
            print("Failure")

    good_runners = sorted(good_runners, key=operator.attrgetter('closeness'), reverse=True)
    good_runners = getOutcomeFromNumber(good_runners)

    json_s = "["
    for runner in good_runners:
        json_s += runner.toJSON()
    json_s = json_s.replace("}{", "},{")
    json_s += "]"

    with open("OM_site/site_input.json", "w") as file:
        file.write(json_s)
    sleep(5*60)
