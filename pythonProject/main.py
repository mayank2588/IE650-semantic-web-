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


# takes a query for a song and one additional information
def query_song_and_info(query_string, name_add_info):
    # query for the answer
    sparql_query_songs = g.query(query_string)

    # prepare a list for the songs and add the results to the list
    song_list = []
    add_info_list = []
    for record in sparql_query_songs:
        song_list.append(str(record['label']))
        add_info_list.append(str(record[name_add_info]))

    # create a dictionary from the lists
    dictionary = {
        'song': song_list,
        name_add_info: add_info_list
    }

    # convert dict to pandas dataFrame adn return
    return pd.DataFrame(dictionary)


def get_random_song_and_answer(data_frame, name_add_info):
    # filter out songs with non unique additional information
    data_frame['count'] = data_frame.groupby('song')['song'].transform('size')
    df_cleaned = data_frame[data_frame['count'] == 1].drop('count', axis=1)

    # randomly select an observation from the data frame
    song_and_additional_info = df_cleaned.sample(n=1)

    # get the song and the album and cast to list
    song_and_additional_info = song_and_additional_info.values.flatten().tolist()

    # remove all records with the same additional information from the data frame
    df_cleaned = df_cleaned[df_cleaned[name_add_info] != song_and_additional_info[1]]

    # sample  alternative answers
    possible_answers = pd.Series(df_cleaned[name_add_info].unique())
    alternative_answers = possible_answers.sample(n=3).tolist()

    return [song_and_additional_info, alternative_answers]


def create_question_1():
    # give user feedback that it might take a moment for the question to display
    print("\nLoading question ...")

    # create query for song and album. Results will contain all available records which contain an album and a song.
    query_sing_song = "\n SELECT DISTINCT ?label ?album " \
                      "\n WHERE { " \
                      "\n ?song rdfs:label ?label. " \
                      "\n ?song property:album ?album .\n " \
                      "}\n"

    # get a data frame with a song and and additional information about the song
    songs_albums_df = query_song_and_info(query_sing_song, "album")

    # get a random song and additional information, as well as alternative answer
    answer = get_random_song_and_answer(songs_albums_df, "album")
    result = answer

    # get the correct and the alternative answers from the result
    answer_song_and_album = result[0]
    alternative_albums = result[1]

    # print question
    print("\nWhat album is the song \"" + str(answer_song_and_album[0]) + "\" on?")

    # call print_and_check_answer and return result
    return print_and_check_answers(answer_song_and_album[1], alternative_albums)


def create_question_2():
    # give user feedback that it might take a moment for the question to display
    print("\n Loading question ...")

    # create a query for artist and song
    query_string_song_and_artist = "\n SELECT DISTINCT ?label ?artist" \
                                   "\n WHERE {" \
                                   "\n ?song rdfs:label ?label." \
                                   "\n ?song property:artist ?artist." \
                                   "}"

    # get a data frame with a song and and additional information about the song
    songs_artists_df = query_song_and_info(query_string_song_and_artist, "artist")

    # get a random song and additional information, as well as alternative answer
    result = get_random_song_and_answer(songs_artists_df, "artist")

    # get the correct and the alternative answers from the result
    answer_song_and_artist = result[0]
    alternative_artists = result[1]

    # print question
    print("\nWhat is the artist of the song \"" + str(answer_song_and_artist[0]) + "\"?")

    # call print_and_check_answer and return result
    return print_and_check_answers(answer_song_and_artist[1], alternative_artists)


def create_question_3():
    # give user feedback that it might take a moment for the question to display
    print("\n Loading question ...")

    # create a query for artist and song
    query_string_song_and_genre = "\n SELECT DISTINCT ?label ?genre" \
                                  "\n WHERE {" \
                                  "\n ?song rdfs:label ?label." \
                                  "\n ?song property:genre ?genre." \
                                  "}"

    # get a data frame with a song and and additional information about the song
    songs_genre_df = query_song_and_info(query_string_song_and_genre, "genre")

    # get a random song and additional information, as well as alternative answer
    result = get_random_song_and_answer(songs_genre_df, "genre")

    # get the correct and the alternative answers from the result
    answer_song_and_genre = result[0]
    alternative_genres = result[1]

    # print question
    print("\nWhat genre is the song \"" + str(answer_song_and_genre[0]) + "\" from?")

    # call print_and_check_answer and return result
    return print_and_check_answers(answer_song_and_genre[1], alternative_genres)


def create_question_4():
    # give user feedback that it might take a moment for the question to display
    print("\n Loading question ...")

    # create a query for artist and song
    query_string_song_and_producer = "\n SELECT DISTINCT ?label ?producer" \
                                     "\n WHERE {" \
                                     "\n ?song rdfs:label ?label." \
                                     "\n ?song property:producer ?producer." \
                                     "}"

    # get a data frame with a song and and additional information about the song
    songs_producer_df = query_song_and_info(query_string_song_and_producer, "producer")

    # get a random song and additional information, as well as alternative answer
    result = get_random_song_and_answer(songs_producer_df, "producer")

    # get the correct and the alternative answers from the result
    answer_song_and_producer = result[0]
    alternative_producer = result[1]

    # print question
    print("\nWho is the producer of the song \"" + str(answer_song_and_producer[0]) + "\" ?")

    # call print_and_check_answer and return result
    return print_and_check_answers(answer_song_and_producer[1], alternative_producer)


def create_question_5():
    # give user feedback that it might take a moment for the question to display
    print("\n Loading question ...")

    # create a query for artist and song
    query_string_song_and_writer = "\n SELECT DISTINCT ?label ?writer" \
                                   "\n WHERE {" \
                                   "\n ?song rdfs:label ?label." \
                                   "\n ?song property:writer ?writer." \
                                   "}"

    # get a data frame with a song and and additional information about the song
    songs_writer_df = query_song_and_info(query_string_song_and_writer, "writer")

    # get a random song and additional information, as well as alternative answer
    result = get_random_song_and_answer(songs_writer_df, "writer")

    # get the correct and the alternative answers from the result
    answer_song_and_writer = result[0]
    alternative_writer = result[1]

    # print question
    print("\nWho is the writer of the song \"" + str(answer_song_and_writer[0]) + "\" ?")

    # call print_and_check_answer and return result
    return print_and_check_answers(answer_song_and_writer[1], alternative_writer)


def create_question_6():
    # give user feedback that it might take a moment for the question to display
    print("\n Loading question ...")

    # create a query for artist and song
    query_string_song_and_release_date = "\n SELECT DISTINCT ?label ?releaseDate" \
                                         "\n WHERE {" \
                                         "\n ?song rdfs:label ?label." \
                                         "\n ?song property:releaseDate ?releaseDate." \
                                         "}"

    # get a data frame with a song and and additional information about the song
    songs_release_data_df = query_song_and_info(query_string_song_and_release_date, "releaseDate")

    # filter out songs with non unique additional information
    songs_release_data_df['count'] = songs_release_data_df.groupby('Song')['Song'].transform('size')
    songs_release_data_df_cleaned = songs_release_data_df[songs_release_data_df['count'] == 1].drop('count', axis=1)

    # remove exact date from the data frame
    songs_release_data_df_cleaned['releaseDate'] = songs_release_data_df_cleaned['releaseDate'].apply(lambda x: x[0:4])

    # randomly select an observation from the data frame
    song_and_release_date = songs_release_data_df_cleaned.sample(n=1)

    # get the song and the album and cast to list
    song_and_release_date = song_and_release_date.values.flatten().tolist()

    # remove all records with the same additional information from the data frame
    df_cleaned = songs_release_data_df_cleaned[songs_release_data_df_cleaned['releaseDate'] != song_and_release_date[1]]

    # sample  alternative answers
    possible_answers = pd.Series(df_cleaned['releaseDate'].unique())
    alternative_answers = possible_answers.sample(n=3).tolist()

    # print question
    print("\nIn which year was the song \"" + str(song_and_release_date[0]) + "\" ?")

    # call print_and_check_answer and return result
    return print_and_check_answers(song_and_release_date[1], alternative_answers)


def create_question_7():
    # give user feedback that it might take a moment for the question to display
    print("\n Loading question ...")

    # create a query for artist and song
    query_string_artist_and_song = "\n SELECT DISTINCT ?label ?artist" \
                                   "\n WHERE {" \
                                   "\n ?song rdfs:label ?label." \
                                   "\n ?song property:artist  ?artist." \
                                   "}"

    # get a data frame with a song and and additional information about the song
    artists_and_songs_data_df = query_song_and_info(query_string_artist_and_song, "artist")

    # randomly select an observation from the data frame
    artists_and_songs = artists_and_songs_data_df.sample(n=1)

    # get the song and the album and cast to list
    artists_and_songs = artists_and_songs.values.flatten().tolist()

    # remove all records with the same additional information from the data frame
    df_cleaned_1 = artists_and_songs_data_df[artists_and_songs_data_df['artist'] != artists_and_songs[1]]
    df_cleaned_2 = df_cleaned_1[df_cleaned_1['song'] != artists_and_songs[0]]

    # sample  alternative answers
    possible_answers = pd.Series(df_cleaned_2['song'].unique())
    alternative_answers = possible_answers.sample(n=3).tolist()

    # print question
    print("\nWhich song was sang by the artist \"" + str(artists_and_songs[1]) + "\" ?")

    # call print_and_check_answer and return result
    return print_and_check_answers(artists_and_songs[0], alternative_answers)


if __name__ == '__main__':
    # gets through the whole introduction process of getting a new players name
    # player_name = create_player()

    # select difficulty
    # question tempaltes for different difficulties or diffuculty indicator

    # start the quiz

    # safe results and exit quit (or maybe new round)
    # print(player_name)
    create_question_7()


    # safe_player_name_and_score(player_name, 100)
    # Template1.is_usable_for_question()
