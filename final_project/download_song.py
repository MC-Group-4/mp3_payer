
import pytube
from pytube import YouTube
import moviepy.editor as mp
import urllib
import requests
from PIL import Image
import os
from model import Song
from db import Database
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

db = Database()


def download_song(song_title, artist_name):

    url = f'https://www.youtube.com/results?search_query={song_title} {artist_name} audio'
    DRIVER_PATH = 'C:\PATH_PROGRAMS\chromedriver.exe'


    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')

    driver = webdriver.Chrome(executable_path=DRIVER_PATH, chrome_options=options)
    driver.get(url)
    time.sleep(5)
    video = driver.find_element_by_xpath('//*[@id="thumbnail"]')
    link = video.get_attribute(name='href')


    driver.close()

    yt = YouTube(link)

    yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first().download('./music')
    metadata = pytube.extract.metadata(yt.initial_data)

    if yt._metadata:
        song = metadata[0]['Song']
        artist = metadata[0]['Artist']
    else:
        if '-' in yt.title:
            song = yt.title.split(' (')[0].split(' - ')[1]
        else:
            song = yt.title
        if '-' in yt.author:
            artist = yt.author.split(' - ')[0]
        else:
            artist = yt.author

    song_found = db.find_song_by_artist_name(artist)
    if song_found and song_found[0][-1] != 'default.png':
        artist_cover_art = song_found[0][-1]
    else:
        artist_cover_art = f"{artist.lower().replace(' ', '_')}.png"

        img = urllib.request.urlretrieve(yt.thumbnail_url, f"./images/cover_art/{artist_cover_art}")

        Image.open(img[0]).resize((150, 150)).save(f"./images/cover_art/{artist_cover_art}")


    filename = yt.title
    for char in ['.', "'", '"', ',', ':', '$', '#', '@']:
        if char in filename:
            filename = filename.replace(char, '')

    

    found_song = convert_to_mp3(filename, song, artist, artist_cover_art)
    return found_song



def convert_to_mp3(filename, song, artist, artist_cover_art):
    clip = mp.VideoFileClip(f"./music/{filename}.mp4")
    mp3 = clip.audio.write_audiofile(f"./music/{song}.mp3")
    clip.audio.close()
    clip.close()

    os.remove(f"./music/{filename}.mp4")


    song_found = db.find_song_by_song_title(song)
    if not song_found:
        s = Song(song, f"{song}.mp3")
        
        db.add_song(s.get_song_title(), s.get_song_file(), s.get_song_duration(), artist, artist_cover_art)
        return db.find_song_by_song_title(s.get_song_title())


