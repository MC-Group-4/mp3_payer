from mutagen.mp3 import MP3
import sqlite3
import os

base = os.getcwd()
print(base + '\music')
class Song():
    def __init__(self, song_title, song_file, artist=None, album_title=None):
        self.song_title = song_title
        self.song_file = song_file
        self.album_title = album_title
        if artist:
            self.artist = artist
        else:
            self.artist = Artist()
        self.set_song_duration()
        

    def __repr__(self):
        return f'<Song: {self.song_title}>'

    def get_song_title(self):
        return self.song_title

    def get_song_file(self):
        return self.song_file

    def get_song_duration(self):
        return self.song_duration

    def set_song_duration(self):
        music_dir = base + '\music'
        song_file = os.path.join(music_dir, self.get_song_file())
        self.song_duration = MP3(song_file).info.length

class Artist():
    def __init__(self, artist_name='unknown', cover_art="default.png"):
        self.artist_name = artist_name
        self.cover_art = cover_art
    
    def __repr__(self):
        return f'<Artist: {self.artist_name}>'

    def get_artist_name(self):
        return self.artist_name

    def get_cover_art(self):
        return self.cover_art

class Album():
    def __init__(self, album_title):
        self.album_title = album_title
        self.songs = []

    def __repr__(self):
        return f'<Album: {self.album_title}>'

    def add_song(self, song):
        self.songs.append(song)

    def get_songs(self):
        return self.songs


        




# justin_timberlake = Artist("Justin Timberlake", 'justin_timberlke.png')
# adele = Artist("Adele", 'adele.png')
# post_malone = Artist("Post Malone", 'post_malone.png')
# ed_sheeran = Artist("Ed Sheeran", 'ed_sheeran.png')
# neyo = Artist("Ne-Yo", 'neyo.png')
# jcole = Artist("JCole", "jcole.png")
# wiz_khalifa = Artist("Wiz Khalifa", 'wiz_khalifa.png')
# bruno_mars = Artist("Bruno Mars", 'bruno_mars.png')
# chris_brown = Artist("Chris Brown", 'chris_brown.png')
# drake = Artist("Drake", 'drake.png')
# future = Artist("Future", 'future.png')
# justin_bieber = Artist("Justin Bieber", 'justin_bieber.png')
# kendric_lamar = Artist("Kendric Lamar", 'kendric_lamar.png')
# the_weeknd = Artist("The Weeknd", 'the_weeknd.png')

# party = Song(song_title = 'Party', song_file = 'Party.mp3', artist=chris_brown)
# no_role_models = Song(song_title = 'No Role Models', song_file = 'No Role Models.mp3', artist=jcole)
# work_hard_play_hard = Song(song_title = 'Work Hard Play Hard', song_file = 'Work Hard Play Hard.mp3', artist=wiz_khalifa)
# pound_cake = Song(song_title = 'Pound cake', song_file = 'Pound cake.mp3', artist=drake)
# gods_plan = Song(song_title = "God's Plan", song_file = "God's Plan.mp3", artist=drake)
# after_hour = Song(song_title = 'After Hour', song_file = 'After Hour.mp3', artist=the_weeknd)
# save_your_tears = Song(song_title = 'Save Your Tears', song_file = 'Save Your Tears.mp3', artist=the_weeknd)
# middle_child = Song(song_title = 'Middle Child', song_file = 'Middle Child.mp3', artist=jcole)
# peaches = Song(song_title = 'Peaches', song_file = 'Peaches.mp3', artist=justin_bieber)
# these_walls = Song(song_title = 'These Walls', song_file = 'These Walls.mp3', artist=kendric_lamar)
# leave_the_door_open = Song(song_title = 'Leave The Door Open', song_file = 'Leave The Door Open.mp3', artist=bruno_mars)
# life_is_good = Song(song_title = 'Life is Good', song_file = 'Life is Good.mp3', artist=future)

