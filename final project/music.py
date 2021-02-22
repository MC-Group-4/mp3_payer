class Music:
    def __init__(self, title, artist, file_name):
        self.title = title
        self.artist = artist
        self.file_name = file_name
    def get_music(self):
        return self.title, self.artist, self.file_name


music1 = Music('No Role Models', 'j cole', 'No Role Models.wav')

