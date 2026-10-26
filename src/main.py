from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QPushButton, QGridLayout, QFileDialog, QInputDialog, QStyle, QSlider, QDialog, QVBoxLayout, QHBoxLayout, QCheckBox, QProgressBar, QMainWindow, QCompleter, QLineEdit, QFrame, QDialog, QScrollArea, QLayout, QComboBox, QMenu, QMenuBar
from PyQt6.QtCore import QDir, QFileInfo, QUrl, QSize, QRect
from PyQt6.QtGui import QFont, QColor,QPalette, QPixmap, QPainter, QPen, QBrush, QIcon, QAction
from PyQt6.QtMultimedia import QAudio, QMediaPlayer, QAudioOutput, QAudioDevice, QMediaMetaData
from PyQt6 import QtCore
import random

from GameStats import GameStats

from backend import Song, SongLibrary, FILTERS_FILE
import sys




# Placeholder class to display where widgets will go
class Color(QWidget):
    def __init__(self, color, text=None, skip_col=False):
        super().__init__()

        if not skip_col:
            self.setAutoFillBackground(True)
            palette = self.palette()
            palette.setColor(QPalette.ColorRole.Window, QColor(color))
            self.setPalette(palette)
        if text != None:
            layout = QVBoxLayout()
            layout.addWidget(QLabel(text))
            self.setLayout(layout)





# Dialog for the filters menu in settings
class SettingsDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.layout = QGridLayout()
        self.filters = FiltersList()
        self.layout.addWidget(self.filters, 0, 0, 1, 2)
        self.new_filter_button = QPushButton("Add Filter")
        self.new_filter_button.pressed.connect(self.filters.addFilter)
        self.save_button = QPushButton("Save")
        self.save_button.pressed.connect(self.saveFilters)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.pressed.connect(self.close)

        self.layout.addWidget(self.new_filter_button, 1, 0, 1, 2)
        self.layout.addWidget(self.cancel_button, 2, 0, 1, 1)
        self.layout.addWidget(self.save_button, 2, 1, 1, 1)

        self.setWindowTitle("Settings")
        self.setLayout(self.layout)

        # Loads the current filters saved in the filter file
        self.loadFilters()


    # Saves the filters to the filter file
    def saveFilters(self):
        with open(FILTERS_FILE, "w") as ffile:
            ffile.writelines(self.filters.getLineData())
        self.close()

    # Loads the filters from the filter file
    def loadFilters(self):
        with open(FILTERS_FILE, "r") as ffile:
            for line in ffile.readlines():
                line = line.removesuffix("\n")
                self.filters.addFilterFromString(line)
        if self.filters.layout.count() < 2:
            self.filters.addFilter()


# Widget which contains the list of filters in a scrollable area
class FiltersList(QScrollArea):
    def __init__(self):
        super().__init__()
        self.widget = QWidget()
        self.num_filters = 1
        self.layout = QVBoxLayout()
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)


        # self.layout.addWidget(Filter())
        self.layout.addStretch()

        

        self.widget.setLayout(self.layout)
        self.setWidget(self.widget)

    # Create a new empty filter
    def addFilter(self):
        self.layout.insertWidget(self.layout.count()-1, Filter())

    # Create a new filter from a string
    def addFilterFromString(self, string: str):
        self.layout.insertWidget(self.layout.count()-1, Filter(string))


    # Gets the filter data as a string to be written to a file
    def getLineData(self):
        output = ""
        num_filters = self.layout.count()-1
        for i in range(num_filters):
            output += self.layout.itemAt(i).widget().outputData()
            if i != num_filters:
                output += "\n"

        return output



# Base filter class which provides the widgets for setting a filter
class Filter(QWidget):
    def __init__(self, string=""):
        super().__init__()
        
        # List of string operations that will be displayed in the combo box
        self.string_operations = ["equals", "not equals", "contains", "does not contain"]
        # Codes for the string operations that go in the file
        self.string_operation_codes = ["==", "!=", "~", "!~"]

        # List of number operations that will be displayed in the combo box
        self.number_operations = ["equals", "not equals", "greater than", "less than", "greater than or equals", "less than or equals"]
        # Codes for the number operations that will be displayhed in the combo box
        self.number_operation_codes = ["==", "!=", ">", "<", ">=", "<="]

        self.layout = QGridLayout()
        
        # Button to remove the filter
        self.remove_button = QPushButton("Remove")
        self.remove_button.pressed.connect(self.deleteLater)

        # Combo box which contains the different fields to filter
        self.field_button = QComboBox()

        # Combo box which contains the different operations on the filters
        self.operation_button = QComboBox()

        # Line edit where the user enters the value they want to compare to
        self.value_button = QLineEdit()

        # When the field button changes, we want to ensure the appropriate combo box is used
        self.field_button.currentIndexChanged.connect(self.comboBoxChanged)

        # Populate with fields from song library
        # We don't include the first field name (filename) since we don't want to filter by it
        self.field_button.insertItems(0,sl.field_names[1:])


        self.layout.addWidget(self.field_button, 0, 0, 1, 2)
        self.layout.addWidget(self.operation_button, 0, 2, 1, 2)
        self.layout.addWidget(self.value_button, 0, 4, 1, 2)
        self.layout.addWidget(self.remove_button, 0, 6, 1, 1)
        self.setLayout(self.layout)

        # Ensures that the filters aren't weird shapes
        self.setFixedHeight(50)
        self.setMinimumWidth(600)

        # Used when loading from a string

        # Split the string into the different parts
        split = string.split("|")
        if len(split) != 4:
            return

        filter_type = split[0]
        field = split[1]
        operation = split[2]
        value = split[3]

        # Set the field from the string
        self.field_button.setCurrentIndex(sl.fields.index(field)-1)

        # Set the operation based on the type of field
        if filter_type == 's':
            self.operation_button.setCurrentIndex(self.string_operation_codes.index(operation))
        else:
            self.operation_button.setCurrentIndex(self.number_operation_codes.index(operation))
        
        # Set the text for the value button
        self.value_button.setText(value)





    # When the field is chosen, need to correct the other widgets
    def comboBoxChanged(self):
        # print(self.field_button.currentIndex())
        self.operation_button.clear()
        if sl.field_types[self.field_button.currentIndex()+1] == 's':
            self.operation_button.insertItems(0, self.string_operations)
        else:
            self.operation_button.insertItems(0, self.number_operations)
    
    # Return the full filter line
    def outputData(self):
        field_index = self.field_button.currentIndex() + 1
        operation_index = self.operation_button.currentIndex()
        field_type = sl.field_types[field_index]

        output = f"{field_type}|{sl.fields[field_index]}|{self.string_operation_codes[operation_index] if field_type == 's' else self.number_operation_codes[operation_index]}|{self.value_button.text()}"
        return output



# Class for the top widget which contains the logo
class TopWidget(QWidget):
    def __init__(self):
        super().__init__()




        layout = QGridLayout()
        title = QLabel()
        title.setPixmap(QPixmap("assets/PyHeardle Logo.png").scaled(QSize(410, 113), aspectRatioMode= QtCore.Qt.AspectRatioMode.KeepAspectRatio))

        layout.addWidget(title, 0, 1, 0, 8, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)




# Class to display the progress bar
class ProgressBar(QLabel):
    def __init__(self):
        super().__init__()
        # Canvas where the progress bar is drawn
        self.canvas = QPixmap(500, 15)
        self.canvas.fill(QColor('white'))

        # Scale to the label
        self.setPixmap(self.canvas.scaled(QSize(self.geometry().width(), 1000), aspectRatioMode=QtCore.Qt.AspectRatioMode.KeepAspectRatio))


    # Called when the parent label is resized to automatically resize the canvas
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.setPixmap(self.canvas.scaled(QSize(self.geometry().width(), 1000), aspectRatioMode=QtCore.Qt.AspectRatioMode.KeepAspectRatio))



    # Function to draw progress bar and dividing lines
    def drawProgressBar(self, song_pos):
        
        # If no song is loaded, the rest of the function is skipped to avoid errors
        if gs.no_song:
            return

        # Get song data from game stats
        splits = gs.splits
        current_split = gs.guess
        total = gs.song_total * 1000
        
        position = song_pos - gs.song_start_pos

        if position < 0:
            position = 0

        # Set up canvas painter and parameters
        painter = QPainter(self.canvas)
        width = self.canvas.width()
        height = self.canvas.height()
        pen = QPen()
        pen.setWidth(1)


        # Draw the current split of the progress bar
        pen.setColor(QColor('grey'))
        brush = QBrush(QColor('grey'), QtCore.Qt.BrushStyle.SolidPattern)
        painter.setPen(pen)
        painter.setBrush(brush)

        self.canvas.fill(QColor('white'))

        painter.drawRect(QRect(0, 0, int(width * gs.getCurrentSplit()*1000/total), height))


        pen.setColor(QColor('red'))
        brush.setColor(QColor('red'))
        painter.setPen(pen)
        painter.setBrush(brush)

        # Only draw bar when song has started
        if position != 0:
            # Draw red bar showing how far through the song
            painter.drawRect(QRect(0, 0, int(width * position/total), height))


        

        # Change parameters to draw split lines
        pen.setColor(QColor('black'))
        brush.setColor(QColor('black'))
        painter.setPen(pen)
        painter.setBrush(brush)

        # Draw lines for each split
        for split in splits:
            painter.drawRect(QRect(int(width * split*1000 /total), 0, 1, height))


        # Update canvas onto label
        self.setPixmap(self.canvas.scaled(QSize(self.geometry().width(), 1000), aspectRatioMode=QtCore.Qt.AspectRatioMode.KeepAspectRatio))


# Boxes where previous guesses are recorded
class GuessBoxes(QWidget):
    def __init__(self):
        super().__init__()
        # self.guess_number = 0
        layout = QVBoxLayout()

        font = QFont()
        font.setPointSize(18)


        self.boxes = []
        for i in range(6):
            self.boxes.append(QLabel(""))
            self.boxes[i].setWordWrap(True)
            self.boxes[i].setFont(font)
            self.boxes[i].setFrameShape(QFrame.Shape.Panel)
            self.boxes[i].setLineWidth(3)

            layout.addWidget(self.boxes[i])
        self.setLayout(layout)


    # Adds a guess into the next box
    def addGuess(self, guess):
        correct = gs.checkGuess(guess)

        if guess =="Skip":
            self.boxes[gs.guess].setStyleSheet(" QLabel {color: yellow}")
        elif correct:
            self.boxes[gs.guess].setStyleSheet(" QLabel {color: green}")
        else:
            self.boxes[gs.guess].setStyleSheet(" QLabel {color: red}")

        self.boxes[gs.guess].setText(guess)
        return gs.checkGuess(guess)


    # Clears the boxes
    def clearBoxes(self):
        for box in self.boxes:
            box.setText("")
            box.setStyleSheet(" QLabel {color: white}")







# Class to hold progress bar and play button along with durations
class ProgressBarPlayButton(QWidget):
    def __init__(self):
        super().__init__()

        self.player = QMediaPlayer()
        self.output = QAudioOutput()
        self.output.setVolume(0.5)
        self.player.setAudioOutput(self.output)


        self.progress_bar = ProgressBar()
        print("\n")
        self.player.positionChanged.connect(self.progress_bar.drawProgressBar)
        self.player.positionChanged.connect(self.updatePlayback)



        layout = QGridLayout()


        self.play_button = QPushButton()
        # play_button.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
        self.play_button.setIcon(QApplication.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.play_button.clicked.connect(self.playSong)

        self.time_passed = QLabel("0:00")
        self.total_time = QLabel("0:00")

        layout.addWidget(self.progress_bar, 0, 0, 1, 4)
        # layout.addWidget(Color('blue', "Time Passed"), 1, 0, 1, 1)
        layout.addWidget(self.time_passed, 1, 0, 1, 1)
        layout.addWidget(self.total_time, 1, 3, 1, 1)
        # layout.addWidget(Color('blue', "Total Time"), 1, 3, 1, 1)
        layout.addWidget(self.play_button, 1, 1, 1, 2)
        # layout.addWidget(Color('blue', "Play"), 1, 1, 1, 2)
        self.setLayout(layout)


    # Called to stop and start playback, updates the playbutton icons
    def playSong(self):
        if self.player.isPlaying():
            self.player.pause()
            self.play_button.setIcon(QApplication.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        else:
            if self.player.playbackState() == QMediaPlayer.PlaybackState.StoppedState:
                self.player.play()
                self.player.setPosition(gs.song_start_pos)
            else:
                self.player.play()
            self.play_button.setIcon(QApplication.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))



    

    # Called when a new song is added
    def newSong(self, path):
        self.total_time.setText(self.time_to_string(gs.song_total * 1000))
        self.player.setSource(QUrl.fromLocalFile(path))
        self.progress_bar.drawProgressBar(0)
        self.play_button.setIcon(QApplication.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))


    # Updates the timer remaining and total time labels and stops the song when it reached the current split
    def updatePlayback(self, position):
        new_pos = position - gs.song_start_pos
        if new_pos < 0:
            new_pos = 0

        self.total_time.setText(self.time_to_string(gs.song_total * 1000))
        self.time_passed.setText(self.time_to_string(new_pos))
        if position-gs.song_start_pos >=  gs.getCurrentSplit() *1000:
            self.player.stop()
        

        
    def time_to_string(self, time_ms):
        time_secs = int(time_ms / 1000)
        mins = str(time_secs // 60)
        secs = str(time_secs % 60)

        if len(secs) < 2:
            secs = f"0{secs}"


        return f"{mins}:{secs}"

    def updateProgressBar(self):
        # if not self.player.isPlaying():
        self.progress_bar.drawProgressBar(self.player.position())



# Class for the display showed when you finish a round
class EndDisplay(QLabel):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setFrameShape(QFrame.Shape.Panel)
        self.setLineWidth(3)
        font = QFont()
        font.setPointSize(24)

        self.song_label = QLabel("")
        self.song_label.setFont(font)
        self.song_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.song_label.setWordWrap(True)


        self.artist_label = QLabel("")
        self.artist_label.setFont(font)
        self.artist_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.artist_label.setWordWrap(True)

        self.error_label = QLabel("Error: No songs found. Try changing filters or song library")


        layout.addWidget(self.song_label)
        layout.addWidget(self.artist_label)
        layout.addWidget(self.error_label)

        self.error_label.hide()
        self.setLayout(layout)

    def setLabels(self):
        # self.error_label.hide()
        self.artist_label.show()
        if gs.game_won:
            self.setStyleSheet(" QLabel {color: green}")
            self.song_label.setStyleSheet(" QLabel {color: green}")
            self.artist_label.setStyleSheet(" QLabel {color: green}")
        else:
            self.setStyleSheet(" QLabel {color: red}")
            self.song_label.setStyleSheet(" QLabel {color: red}")
            self.artist_label.setStyleSheet(" QLabel {color: red}")

        self.song_label.setText(gs.song.song_name)        
        self.artist_label.setText(gs.song.song_artist)        


    def setError(self):
        self.setStyleSheet(" QLabel {color: red}")
        self.song_label.setText("Error: No songs found. Try changing filters or song library")
        self.song_label.setStyleSheet(" QLabel {color: red}")

        self.artist_label.hide()

        # self.error_label.setStyleSheet(" QLabel {color: red}")
        # self.error_label.show()




# Class to enter guesses
class GuessBox(QLineEdit):
    def __init__(self):
        super().__init__()
    
    # Adds autocomplete to the guesses
    def addCompleter(self):
        names = sl.getSongAnswers()
        completer = QCompleter(names)
        completer.setFilterMode(QtCore.Qt.MatchFlag.MatchContains)
        completer.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)
        self.setCompleter(completer)

    

# Main window class
class MainWindow(QMainWindow):
    
    # Set up all of the top level widgets
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyHeardle")

        # Main layout for the whole window
        self.layout = QGridLayout()

        # Placeholder for parent widget containing top widgets

        self.skip_button = QPushButton(text="Skip")
        self.PBPB = ProgressBarPlayButton()
        self.skip_button.pressed.connect(lambda x = True: self.makeGuess(x))

        self.submit_button = QPushButton(text="Submit")
        self.submit_button.pressed.connect(self.makeGuess)

        self.new_song_button = QPushButton(text="New Song")
        self.new_song_button.pressed.connect(self.setGuessScreen)

        self.guess_box = GuessBox()

        self.guess_box.returnPressed.connect(self.makeGuess)

        self.guess_boxes = GuessBoxes()

        self.end_display = EndDisplay()

        self.settings_dialog = SettingsDialog()
        self.file_dialog = QFileDialog()
        self.file_dialog.setFileMode(QFileDialog.FileMode.Directory)


        self.menu_bar = QMenuBar(self)

        self.settings_menu = QMenu("Settings", self)
        filters_action = QAction("Filters", self)
        song_start_action = QAction("Play Random Song Part", self)
        song_start_action.setCheckable(True)
        self.settings_menu.addAction(filters_action)
        self.settings_menu.addAction(song_start_action)
        filters_action.triggered.connect(self.start_settings_dialog)
        song_start_action.toggled.connect(self.start_action_toggled)

        self.file_menu = QMenu("File", self)
        library_path_action = QAction("Choose Library Folder", self)
        self.file_menu.addAction(library_path_action)
        library_path_action.triggered.connect(self.start_file_dialog)


        self.menu_bar.addMenu(self.settings_menu)
        self.menu_bar.addMenu(self.file_menu)



        self.setMenuBar(self.menu_bar)



        self.layout.addWidget(TopWidget(), 0, 0, 1, 7)
        self.layout.setVerticalSpacing(10)
        # self.layout.setHorizontalSpacing(4)


        self.layout.addWidget(self.guess_boxes, 1, 2, 3, 3)
        self.layout.addWidget(self.end_display, 4, 2, 2, 3)
        # self.layout.addWidget(Color('red', "Success"), 4, 2, 3, 3)
        self.layout.addWidget(self.PBPB, 8, 2, 1, 3)
        self.layout.addWidget(self.guess_box, 10, 2, 1, 3)
        self.layout.addWidget(self.skip_button, 11, 2, 1, 1)
        self.layout.addWidget(self.new_song_button, 11, 3, 1, 1)
        # self.layout.addWidget(Color('teal', "Skip"), 9, 2, 1, 1)
        self.layout.addWidget(self.submit_button, 11, 4, 1, 1)

        for i in range(12):
            self.layout.setRowStretch(i, 1)

        # self.layout.addWidget(Color('darkorange', "Submit"), 9, 3, 1, 1)

        widget = QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)

        self.setGuessScreen()

        self.setGeometry(50, 50, 1000, 1000)
        # self.new_song_button.hide()

        # gs.newSong(sl.getRandomSong())
        # PBPB.newSong(sl.getRandomSong())



    def makeGuess(self, skip: bool=False):
        if gs.guess < 6:
            correct = False
            if skip:
                self.guess_boxes.addGuess("Skip")
            else:
                correct = self.guess_boxes.addGuess(self.guess_box.text())
            self.guess_box.clear()
            gs.nextGuess()
            self.PBPB.updateProgressBar()
            if gs.game_done:
                self.setWinScreen()




    # Change the screen to the win screen where skip, submit and guess are hidden and a new button to get next song appears
    def setWinScreen(self):
        gs.song_total = gs.duration / 1000
        gs.splits = []
        self.PBPB.updateProgressBar()
        self.skip_button.hide()
        self.submit_button.hide()
        self.guess_box.hide()
        self.new_song_button.show()
        self.end_display.show()
        self.end_display.setLabels()
        if not self.PBPB.player.isPlaying():
            self.PBPB.playSong()
            self.PBPB.player.setPosition(gs.song_start_pos)
        gs.song_start_pos = 0

    # Change the screen from the win screen back to the regular guessing screen, also functions as a reset of the current song
    def setGuessScreen(self):
        gs.newSong(sl.getRandomSong())

        if gs.no_song:
            self.setErrorScreen()
        else:
            self.PBPB.newSong(gs.song.song_path)
            self.PBPB.show()
            self.skip_button.show()
            self.submit_button.show()
            self.guess_box.show()
            self.guess_boxes.show()
            self.new_song_button.hide()
            self.guess_boxes.clearBoxes()
            self.guess_box.addCompleter()
            self.end_display.hide()


    def setErrorScreen(self):
        self.PBPB.hide()
        self.new_song_button.show()
        self.skip_button.hide()
        self.submit_button.hide()
        self.guess_box.hide()
        self.guess_boxes.hide()
        self.end_display.show()
        self.end_display.setError()


    def start_action_toggled(self, checked: bool):
        print(checked)
        gs.random_song_part = checked


    def start_settings_dialog(self):
        self.settings_dialog.exec()

    def start_file_dialog(self):
        if self.file_dialog.exec():
            filename = self.file_dialog.selectedFiles()[0]
            sl.updateSongLibrary(filename)
            
            self.setGuessScreen()

            # print(filename)



# Create application
app = QApplication([])


sl = SongLibrary()
# sl.updateSongLibrary("/home/mikey/Music")
gs = GameStats()

# Create window
window = MainWindow()
window.show()


app.exec()
