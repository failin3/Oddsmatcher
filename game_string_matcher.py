import json
import operator

class Runner:
    def __init__(self, score, name, backodds, layodds, closeness, liquidity):
        self.name = name
        self.score = score
        self.backodds = backodds
        self.layodds = layodds
        self.closeness = closeness
        self.liquidity = liquidity

def checkOdds(bfgame, ssgame):
    runner_list = []
    counter = 1
    print(ssgame["odds"])
    try:
        for bfodds, ssodds, liquidity in zip(bfgame["odds"], ssgame["odds"], bfgame["liquidity"]):
            closeness = (1/float(bfodds) - 1/float(ssodds))*100 + 100
            if closeness > 95:
                runner = Runner(counter, bfgame["name"], ssodds, bfodds, closeness, liquidity)
                runner_list.append(runner)
            else:
                counter += 1
        return runner_list
    except:
        pass

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

good_runners = sorted(good_runners, key=operator.attrgetter('closeness'))
for runner in good_runners:
    print("{}: {} - {}      {}%     Liquidity: {}".format(runner.name, runner.backodds, runner.layodds, runner.closeness, runner.liquidity))

