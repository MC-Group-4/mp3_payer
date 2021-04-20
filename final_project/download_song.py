
import pytube
from pytube import YouTube
import moviepy.editor as mp
import urllib
from PIL import Image
import os
from model import Song
from db import Database

db = Database()

def download_song(link):

    yt = YouTube(link)

    yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first().download('./music')
    metadata = pytube.extract.metadata(yt.initial_data)

    if yt._metadata:
        song = metadata[0]['Song']
        artist = metadata[0]['Artist']
    else:
        song = yt.title.split(' (')[0].split(' - ')[1]
        artist = yt.author.split(' - ')[0]

    song_found = db.find_song_by_artist_name(artist)
    if song_found and song_found[0][-1] != 'default.png':
        artist_file_name = song_found[0][-1]
    else:
        artist_file_name = f"{artist.lower().replace(' ', '_')}.png"

        img = urllib.request.urlretrieve(yt.thumbnail_url, f"./images/cover_art/{artist_file_name}")

        Image.open(img[0]).resize((150, 150)).save(f"./images/cover_art/{artist_file_name}")




    filename = yt.title
    for char in ['.', "'", '"', ',', ':']:
        if char in filename:
            filename = filename.replace(char, '')

    

    convert_to_mp3(filename, song, artist, artist_file_name)


def convert_to_mp3(filename, song, artist, artist_file_name):
    clip = mp.VideoFileClip(f"./music/{filename}.mp4")
    mp3 = clip.audio.write_audiofile(f"./music/{song}.mp3")


    song_found = db.find_song_by_song_title(song)
    if not song_found:
        s = Song(song, f"{song}.mp3")
        
        db.add_song(s.get_song_title(), s.get_song_file(), s.get_song_duration(), artist, artist_file_name)



