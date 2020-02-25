#napoli-vs-barcelona
game_string = "paris-st-germain-vs-dortmund"
betfair_name = "Paris St-G v Dortmund"

first_word = game_string.split("-")[0]
second_word = game_string.split("vs")[1]
second_word = second_word.replace("-", " ")
second_word = second_word.strip()
second_word = second_word.split(" ")[0]

if first_word in betfair_name.lower() and second_word in betfair_name.lower():
    print(game_string)
