import os
from tinytag import TinyTag
import csv
import random


FILTERS_FILE = "resources/search_terms.txt"

SONG_LIBRARY_FILE = "resources/songlibrary.csv"



# Class which is responsible for scanning the song library and returning songs
class SongLibrary():
    def __init__(self):
        self.current_song_list = []

        # Fields in the csv
        self.fields = ['filename', 'title', 'album', 'artist', 'duration', 'genre', 'year', 'grouping']
        # Names of the fields with nicer formatting
        self.field_names = ['Filename', 'Title', 'Album', 'Artist', 'Duration', 'Genre', 'Year', 'Grouping']
        # Shows the types of each field (string or numeric)
        self.field_types = ['s', 's', 's', 's', 'n', 's', 'n', 's']


    # Called when the folder changes
    # Indexes the song library into a csv containing the song path and all relevant tags
    def updateSongLibrary(self, folder_path):
        rows = []

        # Walk through all files in the folder path recursively
        for root, dirs, files in os.walk(folder_path):
            if files != []:
                for file in files:
                    # If the file is an mp3 then we index it
                    if file.endswith('mp3'):

                        # Use TinyTag to extract the tags and place it into a dictionary
                        tag = TinyTag.get(f"{root}/{file}")
                        temp_dict = {}
                        temp_dict['filename'] = tag.filename
                        temp_dict['title'] = tag.title
                        temp_dict['album'] = tag.album
                        temp_dict['artist'] = tag.artist
                        temp_dict['duration'] = tag.duration
                        temp_dict['genre'] = tag.genre
                        # print(tag.filename)
                        temp_dict['grouping'] = tag.other.get('grouping')[0]
                        temp_dict['year'] = tag.year
                        rows.append(temp_dict)
        # Write the tags to the csv
        with open(SONG_LIBRARY_FILE, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fields)
            writer.writeheader()
            writer.writerows(rows)

    # Gets a random song and updates which possible songs it could be
    def getRandomSong(self):
        self.current_song_list = []
        with open(SONG_LIBRARY_FILE, 'r') as csvfile:
            csvreader = csv.DictReader(csvfile)
            for row in csvreader:
                # Checks the song against the filters
                if fp.checkSong(FILTERS_FILE, row) and float(row['duration'])>30:
                    self.current_song_list.append(row)

        # If there are no songs, return the error song
        if len(self.current_song_list) == 0:
            return Song("", 0, "", "", "", True)
        song = random.choice(self.current_song_list)
        return Song(song['title'], float(song['duration']), song['filename'], song['artist'], self.getSongAnswerFormat(song))


    # Returns a string of the song in Artist - Title format which is used for guessing
    def getSongAnswerFormat(self, row):
        return f"{row['artist']} - {row['title']}"

    # Returns a list of possible song answers in Artist - Title format
    def getSongAnswers(self):
        output = []
        for song in self.current_song_list:
            output.append(self.getSongAnswerFormat(song))
        return output

    # Function which sets which songs show up
    def setSongParams():
        pass
    





# Class to store song data
class Song():
    def __init__(self, name, length, path, artist, answer, empty=False):
        self.song_name = name
        self.song_length = length
        self.song_path = path
        self.song_artist = artist
        self.answer = answer
        self.empty = empty
    




# Class used to check if songs pass the filter list
class FilterParser():

    def __init__(self):
        pass

    # Check the song against the filter list
    def checkSong(self, filter_file: str, song_csv: dict):
        with open(filter_file, 'r') as filters:
            for line in filters.readlines():

                line = line.removesuffix("\n")
                split = line.split("|")
                if len(split) != 4:
                    continue
                filter_type = split[0]
                field = split[1]
                operation = split[2]
                value = split[3]
            

                if filter_type == 's':
                    if not self.resolveString(field, operation, value.lower(), song_csv):
                        return False
                elif filter_type == 'n':
                    if not self.resolveNumber(field, operation, float(value), song_csv):
                        return False
            return True


    # Checks for string based filters
    def resolveString(self, field, operation, value, song_csv: dict):
        
        if field in song_csv.keys():
            song_field_value = song_csv[field].lower()
            match operation:
                case "==":
                    return value == song_field_value
                case "!=":
                    return value != song_field_value
                case "~":
                    return value in song_field_value
                case "!~":
                    return value not in song_field_value
                case _:
                    return False
        else:
            return False

    def resolveNumber(self, field, operation, value, song_csv: dict):
        if song_csv[field] == "":
            return False


        if field in song_csv.keys():
            song_field_value = float(song_csv[field])
            match operation:
                case "<":
                    return song_field_value < value
                case "<=":
                    return song_field_value <= value
                case ">":
                    return song_field_value > value
                case ">=":
                    return song_field_value >= value
                case "==":
                    return song_field_value == value
                case "!=":
                    return song_field_value != value
                case _:
                    return False
        else:
            return False




fp = FilterParser()


