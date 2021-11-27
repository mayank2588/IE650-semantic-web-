# this is a first approach to the music quiz application

import pandas as pd
from QuestionTemplates import QTemplate1

import rdflib as rdf
import random

g = rdf.Graph()
g.parse("D:\IE650-semantic-web--main\IE650-semantic-web--main\songs.xml")


def exit_check(continue_game):
    while True:
        if continue_game.lower() != "no":
            return
        if continue_game.lower() == "no":
            ask_again = input("Are you sure you want to exit the game? (yes/no)")
            if ask_again.lower() == "yes":
                print("You chose to exit the game. Have a good time! =)")
                exit(0)
            elif ask_again.lower() == "no":
                return False
            else:
                print("Please enter one of the given options")
                continue


def play_check(continue_game):
    if continue_game.lower() == "yes":
        return True
    else:
        return False


def get_player_names():
    # read the players csv and extract series with names
    players = pd.read_csv("D:/IE650-semantic-web--main/IE650-semantic-web--main/pythonProject/resources/players.csv")
    player_names = players["player_name"]
    return player_names


def check_for_menu_return(user_input):
    # check string
    if user_input == "RETURN":
        return True
    else:
        return False


def get_new_player_name():
    # define max player name length
    min_length_player_name = 4
    max_length_player_name = 15

    while True:
        # get the payer input
        print("Enter a player name with minimal " + str(min_length_player_name) + " and maximal " + str(
            max_length_player_name) + " characters.")
        print("Enter RETURN to return to the previous menu:")
        player_name_input: str = input("Player name: ")

        # check for break condition
        if player_name_input.lower() == "return":
            # return to introduction
            return None

        # check if player name is short enough
        if max_length_player_name >= len(player_name_input) > min_length_player_name:
            player_names = get_player_names()
            if player_name_input.lower() in player_names.values or player_name_input in player_names.values:
                print("\nSorry. This name is already taken")
                continue
            else:
                return player_name_input
        else:
            print("\nYou entered to to little or to many as your player name")
            continue


def create_player():
    # print out the introduction to the quiz
    print("Hello, welcome to the ... music quiz")
    print("Further introduction text")

    while True:
        # get the first user input - check of user wants to play or quit the quiz
        continue_game: str = input("\nWould you like to play a round?(yes/no)").lower()

        # check if user wants to exit the game, if yes quit the process
        if exit_check(continue_game) is False:
            continue_game = "yes"
        # check for yes, if user dos not give a given option - ask again
        if play_check(continue_game):
            # get the users name if he wants to play
            print("\nGreat! Then tell us your player name for the highscore list.")

            # get the players name
            player_name = get_new_player_name()
            if player_name is not None:
                return player_name
        else:
            print("Please enter one of the given options")
            continue

def pick_song() -> object:
    # random pick a song from the list
    q = "\n SELECT distinct ?label ?album \n  WHERE { \n ?song rdfs:label ?label. \n ?song property:album ?album .\n }\n"
    R = g.query(q)
    l = []
    for r in R:
        l.append(r['label'])
    song = random.choice(l)
    return song


def create_question1():

    song = pick_song()
    print("What is the name of the album of '" + song + "' ?")
    # get answer
    a = "\n SELECT distinct ?album \n  WHERE {\n    ?song rdfs:label '" + song + "'.\n ?song property:album ?album .\n }\n"
    A = g.query(a)
    for r in A:
        answer = r["album"]
    print(answer)


def create_question2():
    song = pick_song()
    print("What is the artist of '" + song + "' ?")
    # get answer
    a = "\n SELECT distinct ?artist \n  WHERE {\n    ?song rdfs:label '" + song + "'.\n ?song property:artist ?artist .\n }\n"
    A = g.query(a)
    for r in A:
        answer = r["artist"]
    print(answer)


def create_question3():
    song = pick_song()
    print("In what genre is '" + song + "' from?")
    # get answer
    a = "\n SELECT distinct ?genre \n  WHERE {\n    ?song rdfs:label '" + song + "'.\n ?song property:genre ?genre .\n }\n"
    A = g.query(a)
    for r in A:
        answer = r["genre"]
    print(answer)


def create_question4():
    song = pick_song()
    print("Who is the producer of '" + song + "'?")
    # get answer
    a = "\n SELECT distinct ?producer \n  WHERE {\n    ?song rdfs:label '" + song + "'.\n ?song property:producer ?producer .\n }\n"
    A = g.query(a)
    for r in A:
        answer = r["producer"]
    print(answer)


def create_question5():
    song = pick_song()
    print("Who wrote the lyrics '" + song + "'?")
    # get answer
    a = "\n SELECT distinct ?writer \n  WHERE {\n    ?song rdfs:label '" + song + "'.\n ?song property:writer ?writer .\n }\n"
    A = g.query(a)
    for r in A:
        answer = r["writer"]
    print(answer)


def create_question6():
    song = pick_song()
    print("When was '" + song + "' released ? yyyy-mm-dd")
    # get answer
    a = "SELECT distinct ?releaseDate\n WHERE {\n?song rdfs:label '" + song + "'.\n ?song property:releaseDate ?releaseDate.\n }\n"
    A = g.query(a)
    for r in A:
        answer = r["releaseDate"]
    print(answer)

if __name__ == '__main__':
    # gets through the whole introduction process of getting a new players name
    player_name = create_player()

    # select difficulty
    # question tempaltes for different difficulties or diffuculty indicator

    # start the quiz

    # safe results and exit quit (or maybe new round)
    print(player_name)
    # Template1.is_usable_for_question()


