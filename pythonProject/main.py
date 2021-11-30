# this is a first approach to the music quiz application

import pandas as pd
from QuestionTemplates import QTemplate1

import rdflib as rdf
import random

g = rdf.Graph()
g.parse("resources/songs.xml")


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
    players = pd.read_csv("resources/players.csv")
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
            # get all player names in lower case, so the same letter combination can't be repicked
            player_names = get_player_names().str.lower()
            if player_name_input.lower() in player_names.values:
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


def safe_player_name_and_score(safe_player_name, safe_player_score):
    # open file with "a" to append data to csv
    file = open("resources/players.csv", "a")
    # append player name and score
    file.write("\n" + safe_player_name + ", " + str(safe_player_score))
    # close file
    file.close()


def pick_song() -> object:
    # random pick a song from the list
    q = "\n SELECT distinct ?label ?album \n  WHERE { \n ?song rdfs:label ?label. \n ?song property:album ?album .\n }\n"
    R = g.query(q)
    l = []
    for r in R:
        l.append(r['label'])
    song = random.choice(l)
    return song


def print_and_check_answers(correct_answer, alternative_answers):
    # create the answer options
    answer_options = alternative_answers
    answer_options.append(correct_answer)

    # randomly shuffle list
    random.shuffle(answer_options)

    # print out the answer options
    print("a: " + str(answer_options[0]))
    print("b: " + str(answer_options[1]))
    print("c: " + str(answer_options[2]))
    print("d: " + str(answer_options[3]))

    # start loop to get an answer string
    while True:

        # get the input
        answer: str = input("\nPlease enter the corresponding letter (a, b, c, d) as yours answer: ").lower()

        # map answer to list numbers
        if answer == "a":
            list_num = 0
        elif answer == "b":
            list_num = 1
        elif answer == "c":
            list_num = 2
        elif answer == "d":
            list_num = 3
        else:
            print("\nThe entered option is not valid")
            continue

        # check if answer is correct
        if answer_options[list_num] == correct_answer:
            return True
        else:
            return False


def create_question1():
    # create query for song and album. Results will contain all available records which contain an album and a song.
    query_sing_song = "\n SELECT DISTINCT ?label ?album " \
                      "\n WHERE { " \
                      "\n ?song rdfs:label ?label. " \
                      "\n ?song property:album ?album .\n " \
                      "}\n"

    # query for the answer
    sparql_query_songs = g.query(query_sing_song)

    # prepare a list for the songs and add the results to the list
    song_list = []
    album_list = []
    for record in sparql_query_songs:
        song_list.append(str(record['label']))
        album_list.append(str(record['album']))

    # create a dictionary from the lists
    song_album_dict = {
        'Song': song_list,
        'Album': album_list
    }

    # convert dict to pandas dataFrame
    songs_albums_df = pd.DataFrame(song_album_dict)

    # filter out songs which appear on more than one album
    songs_albums_df['count'] = songs_albums_df.groupby('Song')['Song'].transform('size')
    songs_albums_df_cleaned = songs_albums_df[songs_albums_df['count'] == 1].drop('count', axis=1)

    # randomly select an observation from the data frame
    song_and_album = songs_albums_df_cleaned.sample(n=1)

    # get the song and the album
    answer_song_and_album = song_and_album.values.flatten().tolist()

    # remove all records with the same album from the data frame
    songs_albums_df_cleaned = songs_albums_df_cleaned[songs_albums_df_cleaned['Album'] != answer_song_and_album[1]]

    # sample three other albums as alternative answer
    alternative_songs_albums = pd.Series(songs_albums_df_cleaned['Album'].unique())
    alternative_albums = alternative_songs_albums.sample(n=3).tolist()

    # print question
    print("\nWhat album is the song \"" + str(answer_song_and_album[0]) + "\" on?")

    # call print_and_check_answer and return result
    return print_and_check_answers(answer_song_and_album[1], alternative_albums)


def create_question2():
    # create a query for artist and song
    query_string_song_and_artist = "\n SELECT DISTINCT ?label ?artist" \
                                   "\n WHERE {" \
                                   "\n ?song rdfs:label ?label." \
                                   "\n ?song property:artist ?artist." \
                                   "}"

    # set the result from the query
    sparql_query_songs_and_artists = g.query(query_string_song_and_artist)

    # prepare a list for the songs and add the results to the list
    song_list = []
    artist_list = []
    for record in sparql_query_songs_and_artists:
        song_list.append(str(record['label']))
        artist_list.append(str(record['artist']))

    # create a dictionary from the lists
    song_album_dict = {
        'Song': song_list,
        'Artist': artist_list
    }

    # convert dict to pandas dataFrame
    songs_artists_df = pd.DataFrame(song_album_dict)

    # filter out songs ware performed by more than one artist
    songs_artists_df['count'] = songs_artists_df.groupby('Song')['Song'].transform('size')
    songs_artists_df_cleaned = songs_artists_df[songs_artists_df['count'] == 1].drop('count', axis=1)

    # randomly select an observation from the data frame
    song_and_artists = songs_artists_df_cleaned.sample(n=1)

    # get the song and the artist
    answer_song_and_artist = song_and_artists.values.flatten().tolist()

    # remove all records with the same artist from the data frame
    songs_artists_df_cleaned = songs_artists_df_cleaned[songs_artists_df_cleaned['Artist'] != answer_song_and_artist[1]]

    # sample three other artists as alternative answer
    alternative_songs_artist = pd.Series(songs_artists_df_cleaned['Artist'].unique())
    alternative_artists = alternative_songs_artist.sample(n=3).tolist()

    # print question
    print("\nWhat is the artist of the song \"" + str(answer_song_and_artist[0]) + "\"?")

    # call print_and_check_answer and return result
    return print_and_check_answers(answer_song_and_artist[1], alternative_artists)


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
    # player_name = create_player()

    # select difficulty
    # question tempaltes for different difficulties or diffuculty indicator

    # start the quiz

    # safe results and exit quit (or maybe new round)
    # print(player_name)
    create_question2()

    # safe_player_name_and_score(player_name, 100)
    # Template1.is_usable_for_question()
