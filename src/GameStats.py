from backend import Song
import random

# Class which stores the game data such as what the current song is
class GameStats():
    def __init__(self):
        self.song: Song = None
        self.guess = 0
        self.duration = 0
        self.song_total = 0
        self.game_done = False
        self.game_won = False


        # If true then the song start position can be any point from 0 to 16 seconds before the end
        self.random_song_part = False
        
        # Shows where the song can start from
        self.song_start_pos = 0

        # Specifies if the song is empty
        self.no_song = True
        # self.answer = ""

    # Loads a new song and resets the data from the previous round
    def newSong(self, song: Song):


        self.song = song
        self.no_song = song.empty
        self.duration = song.song_length * 1000
        self.guess = 0
        self.splits = [2, 4, 6, 8, 12, 16]
        self.song_total = 16


        # Gives the song a random start point if enabled
        self.game_done = False
        self.game_won = False
        if self.no_song:
            return

        if self.random_song_part:
            self.song_start_pos = random.randint(0, int(self.duration - (16 * 1000)))
        else:
            self.song_start_pos = 0


    # Returns the current split the game is on, if the game is complete it returns the end of the song so that the whole song plays
    def getCurrentSplit(self):
        if self.game_done:
            return self.song_total
        else:
            return self.splits[self.guess]


    # Increments the number of guesses, or specifies if the game is finished
    def nextGuess(self):
        if self.guess < 5:
            self.guess += 1
        else:
            self.game_done = True

    # Checks if the guess is correct
    def checkGuess(self, guess):
        if guess == self.song.answer:
            self.game_done = True
            self.game_won = True
            return True
