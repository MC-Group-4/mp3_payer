import sqlite3
from sqlite3 import Error
from music import Music
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
import datetime
import string 
import random

import pygame
from tkinter import *
import tkinter.ttk as ttk
import time

#Global Variables

is_paused = False
is_stopped = True
count = 0
song_info_dict = {}
slider_mouse_clicked = False



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




#for displaying time of song playing 
def song_time():
    '''
    need to restart the time when new song starts
    need to update the time without having to click play and stop
    '''
    current_song_time = pygame.mixer.music.get_pos()/1000
    format_current_time = time.strftime("%M:%S", time.gmtime(current_song_time))
    status_bar.config(text=format_current_time)

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
    
    #calling from play so updates the time of the song every time it is paused and played, need to fix 
    status_bar.after(1000,song_time())


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
    if count > 0:
        count -= 1
    else:
        count = 3
    stop_call_back()
    file = f'music\\{music[count][3]}'
    pygame.mixer.music.load(file)

    #update song info dict
    update_song_info(file)
    update_song_start_pos(0)#set start position as 0

    #reset slider position to 0 and set slider max equal to length of song
    position_slider.configure(value = 0, to=song_info_dict['length'] )
    play_call_back()


def next_call_back(music):
    global count
    global is_paused
    global is_stopped
    is_paused = False
    is_stopped = True
    if count < 3:
        count += 1
    else:
        count = 0 
    stop_call_back()
    file = f'music\\{music[count][3]}'
    pygame.mixer.music.load(file)

    #update song info dict
    update_song_info(file)
    update_song_start_pos(0) #set start position as 0

    #reset slider position to 0 and set slider max equal to length of song
    position_slider.configure(value = 0, to=song_info_dict['length'] )
    
    play_call_back()


def update_song_info(file):
    print(file)#file):#Sean
    audio = MP3(file) #info about MP3 File
    tags = ID3(file)
    song_info_dict['length'] = audio.info.length #find and store lenght of file, in seconds
    song_info_dict['Artist'] = tags['TPE1'].text[0] #store Artist from MP3 Metadata Tag
    song_info_dict['Title'] = tags['TIT2'].text[0] #store Song Title from MP3 Metadata Tag
    
    
    
def update_song_start_pos(position):#Sean
    song_info_dict['start_pos'] = position #must store song start position because pygame music uses relative position for MP3 Files.

def current_position(): #Sean
    realtivePosition = pygame.mixer.music.get_pos()/1000 #get current relative song position from pygame, in seconds
    absolutePosition = song_info_dict['start_pos'] + realtivePosition #find absolute position by adding relative positon to starting positon
    position_str = convert_seconds(absolutePosition)
    length = convert_seconds(song_info_dict['length']) #length of song in h:mm:ss format

    
    #check if song has starded, if not return tupple (0:00, 0)
    if absolutePosition < 1:
        return ('0:00:00',0)
    
    #if song is not at 0, but relative position is < 1, then song has ended. Return tupple(song length, length in seconds)
    elif realtivePosition < 0:
        return (length,song_info_dict['length'])

    #else return current position tupple
    else:
        return (position_str,absolutePosition)  #return tuple of (h:mm:ss, seconds)
    

    

def seek_position(seconds):#Sean
    if seconds > song_info_dict['length']: #if input is larger than length of song, play song from beginning
        pygame.mixer.music.rewind()
        pygame.mixer.music.play()
    else:   
        pygame.mixer.music.play(start = seconds) #else play song from desired starting position and update dictionary start position value
        song_info_dict['start_pos'] = seconds

def skip_forward_10():
    current = current_position()[1]
    new = current + 10
    if new < song_info_dict['length']:
        seek_position(new)
    
    print("Forward 10 Seconds")

def skip_backward_10():
    current = current_position()[1]
    new = current - 10
    if new > 0:
        seek_position(new)
    else:
        pygame.mixer.music.rewind()
        pygame.mixer.music.play()
        song_info_dict['start_pos'] = 0
        
        
    print("Backward 10 Seconds")





def shuffle_songs(conn, music):
    random.shuffle(music)
    print("Shuffle")
    
def volume(x):
    pygame.mixer.music.set_volume(volumeSlider.get())
    current_volume = pygame.mixer.music.get_volume()
    
    
def update_position(): #update label showing file name, current position and song lenth
    """ update the label every second """
    
    global position_label #update position label
    song_length = convert_seconds(song_info_dict['length']) 
    position_label.configure(text=current_position()[0]+' / '+song_length)

    global song_label #update song Label
    
    try:
        song_label.configure(text = 'Now Playing: '+song_info_dict['fileName'])
    except: #if no song is loaded, display ''
        song_label.configure(text = '')

    #update slider position, ONLY IF MOUSE IS NOT CLICKING THE SLIDER!
    if not slider_mouse_clicked:
        position_slider.configure(value = current_position()[1])

    # schedule another timer
    position_label.after(100, update_position) #makes a loop

def convert_seconds(seconds):
    #takes in a seconds value and returns a string in the form of h:mm:ss
    position = datetime.timedelta(seconds=seconds) #convert to h:mm:ss.ms
    position_str = str(position).split(".")[0] #drop microseconds and format as string
    return position_str

def slider_clicked(event):
    global slider_mouse_clicked
    slider_mouse_clicked = True

def slider_released(event):
    global slider_mouse_clicked
    slider_mouse_clicked = False

    #once mouse button is released, set slider to positon where the mouse was released
    seconds = position_slider.get()
    position_slider.configure(value = seconds)

    #then move song to the desired position
    seek_position(seconds)


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
    #update_song_info(file)
    update_song_start_pos(0)
    pygame.mixer.music.load(file)
    audio = MP3(file) #info about MP3 File
    song_info_dict['length'] = audio.info.length #find and store lenght of file, in seconds, store in song_info_dict dictionary

    root = Tk()
    root.geometry('500x500')

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

    #Seek Buttons
    Forward_Logo = PhotoImage(file='Assets/FF.png')
    Backward_Logo = PhotoImage(file='Assets/FR.png')
    SeekForward_btn = Button(root, image = Forward_Logo, command=skip_forward_10)
    SeekForward_btn.pack()
    SeekBackward_btn = Button(root, image = Backward_Logo, command=skip_backward_10)
    SeekBackward_btn.pack()

    # Volume button 
    global volumeSlider
    volumeLable = Label(root, text = 'Volume')
    volumeLable.pack()
    volumeSlider = Scale(root, from_=0.0, to = 1.0, resolution = 0.1, length= 400, orient=HORIZONTAL, command = volume )
    volumeSlider.pack()
    
    #Show Current Positon
    global position_label
    song_length = convert_seconds(song_info_dict['length']) 
    position_label = Label(text=f'0:00:00 / {song_length}')
    position_label.pack(expand=True)
    position_label.after(100, update_position) #calls function after 1/10s

    #Now Playing Label
    global song_label
    song_label = Label(text = '')
    song_label.pack()


    #Position Slider
    global position_slider
    position_slider = ttk.Scale(root, from_=0, to=song_info_dict['length'],value=0, length = 400)
    position_slider.pack(pady = 20)

    #bind mouse click and release events (only when clicking slider bar) to functions
    position_slider.bind('<Button-1>', slider_clicked)
    position_slider.bind('<ButtonRelease-1>', slider_released)


    #shuffle button 
    #shuffle_btn_image = PhotoImage(file = '/Users/mannat/PycharmProjects/Trial/shuffle.png')
    #shuffle_btn = Button(root, image = shuffle_btn_image, command = shuffle_songs, height = 25, width=40)
    shuffle_btn = Button(root, text = "shuffle", lambda: command = shuffle_songs(connection, music))
    shuffle_btn.pack()
    #label for displaying time of song 
    global status_bar
    status_bar = Label(root, text=" ", bd=5, relief= FLAT, anchor=W)
    status_bar.pack(fill=X, side= BOTTOM, ipady=2)

   
    
    
    list_box = Listbox()
    

    root.mainloop()
   


if __name__ == '__main__':
    main()

