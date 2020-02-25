import json

with open("betfair_output.json") as file:
    betfair_output = json.load(file)
    

# with open("ss_output.json") as file:
#     ss_output = json.load(file)


for item in betfair_output:
    print(item["name"])

#napoli-vs-barcelona
game_string = "paris-st-germain-vs-dortmund"
betfair_name = "Paris St-G v Dortmund"

first_word = game_string.split("-")[0]
second_word = game_string.split("vs")[1]
second_word = second_word.replace("-", " ")
second_word = second_word.strip()
second_word = second_word.split(" ")[0]

if first_word in betfair_name.lower() and second_word in betfair_name.lower():
    #print(game_string)
    pass
