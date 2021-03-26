import sqlite3
from sqlite3 import Error
from music import Music
from mutagen.mp3 import MP3
import datetime

import pygame
from tkinter import *


def create_connection(db_file):
    conn = None
    try:
        connection = sqlite3.connect(db_file)
        print(sqlite3.version)

    except Error as e:
        print(e)

    return connection


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


def create_music(conn, m):

    sql = ''' INSERT INTO music(title,artist,file_name)
              VALUES(?,?,?) '''
    cursor = conn.cursor()
    cursor.execute(sql, m)
    conn.commit()
    return cursor.lastrowid


def get_all_music(conn):
    sql = ''' SELECT * from music'''
    cursor = conn.cursor()
    cursor.execute(sql)
    return cursor.fetchall()

def update_song(conn, music):
    sql = ''' UPDATE music 
              SET file_name = ?
              WHERE id = ? '''

    cursor = conn.cursor()
    cursor.execute(sql, music)
    conn.commit()


is_paused = False
is_stopped = True
count = 0
song_info_dict = {}

def play_call_back():
    global is_paused
    global is_stopped
    if is_paused:
        pygame.mixer.music.unpause()
        is_paused = False
        print('unpausing')
    elif is_stopped:
        pygame.mixer.music.play(loops=0)
        is_stopped = False
        print('playing')
    else:
        pygame.mixer.music.pause()
        is_paused = True
        print('pausing')


def stop_call_back():
    global is_stopped
    if not is_stopped:
        pygame.mixer.music.stop()
        is_stopped = True


def prev_call_back(music):
    global count
    global is_paused
    global is_stopped
    is_paused = False
    is_stopped = True
    count -= 1
    stop_call_back()
    file = f'music\\{music[count][3]}'
    pygame.mixer.music.load(file)
    update_song_lenth(file)
    update_song_start_pos(0)
    play_call_back()


def next_call_back(music):
    global count
    global is_paused
    global is_stopped
    is_paused = False
    is_stopped = True
    count += 1
    stop_call_back()
    file = f'music\\{music[count][3]}'
    pygame.mixer.music.load(file)
    update_song_lenth(file)
    update_song_start_pos(0)
    play_call_back()

def update_song_lenth(file):#Sean
    audio = MP3(file)
    song_info_dict['length'] = audio.info.length #find and store lenght of file, in seconds


def update_song_start_pos(position):#Sean
    song_info_dict['start_pos'] = position #must store song start position because pygame music uses relative position for MP3 Files.

def current_position(): #Sean
    realtivePosition = pygame.mixer.music.get_pos()/1000 #get current relative song position from pygame, in seconds
    absolutePosition = song_info_dict['start_pos'] + realtivePosition #find absolute position by adding relative positon to starting positon
    position = datetime.timedelta(seconds=absolutePosition) #convert to h:mm:ss.ms
    position_str = str(position).split(".")[0] #drop microseconds and format as string
    return position_str  #return current position 


def get_song_length(): #Sean
    length = datetime.timedelta(seconds=song_info_dict['length']) #convert to h:mm:ss.ms
    length_str = str(length).split(".")[0] #drop microseconds and format as string
    return length_str  #return track length string
    

def seek_position(seconds):#Sean
    if seconds > song_info_dict['length']: #if input is larger than length of song, play song from beginning
        pygame.mixer.music.rewind()
        pygame.mixer.music.play()
    else:   
        pygame.mixer.music.play(start = seconds) #else play song from desired starting position and update dictionary start position value
        song_info_dict['start_pos'] = seconds




def main():
    sql_create_music_table = """ CREATE TABLE IF NOT EXISTS music (
                                        id integer PRIMARY KEY,
                                        title text NOT NULL,
                                        artist text NOT NULL,
                                        file_name text NOT NULL
                                    ); """

    connection = create_connection('music.db')

    if connection is not None:
        create_table(connection, sql_create_music_table)
    else:
        print("Error! cannot create the database connection.")

    # music = Music('Hello', 'Adele', 'Hello')
    # create_music(connection, music.get_music())
    # update_song(connection, ('Hello.wav', 3))
    # update_song(connection, ('Empire State Of Mind.wav', 2))
    music = get_all_music(connection)
    pygame.mixer.init()
    file = f'music\\{music[0][3]}'
    update_song_lenth(file)
    update_song_start_pos(0)
    pygame.mixer.music.load(file)

    root = Tk()
    root.geometry('500x400')

    music_list = Listbox(root, width= 120)
    music_list.pack()

    # adding muic lists in the list
    for m in music:
        music_list.insert(END, m[1])

    play_btn = Button(root, text='play', command=play_call_back)
    play_btn.pack()
    stop_btn = Button(root, text='stop', command=stop_call_back)
    stop_btn.pack()
    prev_btn = Button(root, text='prev', command=lambda : prev_call_back(music))
    prev_btn.pack()
    next_btn = Button(root, text='next', command=lambda : next_call_back(music))
    next_btn.pack()
    
    
    list_box = Listbox()
    #root.mainloop()


if __name__ == '__main__':
    main()

