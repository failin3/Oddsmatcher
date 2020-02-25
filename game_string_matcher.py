import json

class Runner:
    def __init__(self, score, name, backodds, layodds, closeness):
        self.name = name
        self.score = score
        self.backodds = backodds
        self.layodds = layodds
        self.closeness = closeness

def checkOdds(bfgame, ssgame):
    counter = 1
    for bfodds, ssodds in zip(bfgame, ssgame):
        closeness = (1/bfodds - 1/ssodds)*100 + 100
        if closeness > 95:
            runner = Runner(counter, bfgame["name"], ssodds, bfodds, closeness)
            return runner
        else:
            counter += 1

with open("betfair_output.json") as file:
    betfair_output = json.load(file)

with open("ss_output.json") as file:
    ss_output = json.load(file)
    
next_one = False
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
            break
    if next_one == False:
        print("Failure")

