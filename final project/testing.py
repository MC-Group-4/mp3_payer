import sqlite3
from sqlite3 import Error
from music import Music

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

    pygame.mixer.music.load(f'music\\{music[count][3]}')
    play_call_back()


def next_call_back(music):
    global count
    global is_paused
    global is_stopped
    is_paused = False
    is_stopped = True
    count += 1
    stop_call_back()
    pygame.mixer.music.load(f'music\\{music[count][3]}')
    play_call_back()





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
    pygame.mixer.music.load(f'music\\{music[0][3]}')

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
    root.mainloop()


if __name__ == '__main__':
    main()

