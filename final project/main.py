import sqlite3
from sqlite3 import Error
from music import Music
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
from mutagen.id3 import TIT2, TPE1
import datetime
import string
import random
import os
import os.path
import shutil
import pygame
from tkinter import *
from tkinter import filedialog
import atexit
import tkinter.ttk as ttk
from PIL import ImageTk, Image
import time
import sys

# Global Variables

is_paused = False
is_stopped = True
is_repeat = False
count = 0
song_info_dict = {}
slider_mouse_clicked = False
listbox_total_count = 0




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


def create_music(title, artist, file_name, music_list):
    global listbox_total_count
    global music
    global numOfSongs
    connect = sqlite3.connect('music.db')
    cursor_object = connect.cursor()
    cursor_object.execute("INSERT INTO music(title,artist,file_name)VALUES(?,?,?)", (title, artist, file_name,))
    connect.commit()

    #check if any songs are in playlist
    music_inital = len(music)
        
    music = get_all_music(connect)
    music_list.insert(END, music[-1][1])
    listbox_total_count = listbox_total_count + 1
    numOfSongs = get_num_of_songs(connect)
    if music_inital == 0:
        next_call_back(music, numOfSongs)
    return cursor_object.lastrowid



def get_all_music(conn):
    sql = ''' SELECT * from music'''
    cursor = conn.cursor()
    cursor.execute(sql)
    return cursor.fetchall()

def get_num_of_songs(conn):
    sql = ''' SELECT * from music'''
    cursor = conn.cursor()
    cursor.execute(sql)
    cursor.execute("SELECT * FROM music")
    return len(cursor.fetchall())

def update_song(conn, music):
    sql = ''' UPDATE music 
              SET file_name = ?
              WHERE id = ? '''

    cursor = conn.cursor()
    cursor.execute(sql, music)
    conn.commit()


# for displaying time of song playing
def song_time():
    '''
    need to restart the time when new song starts
    need to update the time without having to click play and stop
    '''
    current_song_time = pygame.mixer.music.get_pos() / 1000
    format_current_time = time.strftime("%M:%S", time.gmtime(current_song_time))
    status_bar.config(text=format_current_time)


def play_call_back():
    global is_paused
    global is_stopped
    if numOfSongs==0:
        print("There are no songs!")
        if is_paused==False:
            is_paused = True
            pygame.mixer.music.pause()
        if is_stopped==False:
            is_stopped = True
            stop_call_back()
        return 0
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

##    # calling from play so updates the time of the song every time it is paused and played, need to fix
##    status_bar.after(1000, song_time())


def stop_call_back():
    global is_stopped
    if not is_stopped:
        pygame.mixer.music.stop()
        is_stopped = True


def prev_call_back(music, numOfSongs):
    global count
    global is_paused
    global is_stopped
    is_paused = False
    is_stopped = True
    if numOfSongs==0:
        print("There are no songs!")
        return 0
    if count > 0:
        count -= 1
    else:
        count = (numOfSongs-1)
    stop_call_back()
    file = f'music\\{music[count][3]}'
    pygame.mixer.music.load(file)

    # update song info dict
    update_song_info(file)
    update_song_start_pos(0)  # set start position as 0

    # reset slider position to 0 and set slider max equal to length of song
    position_slider.configure(value=0, to=song_info_dict['length'])
    play_call_back()

    global music_list
    music_list.selection_clear(0, END)
    music_list.select_set(count)


def next_call_back(music, numOfSongs):
    global listbox_total_count
    global count
    global is_paused
    global is_stopped
    is_paused = False
    is_stopped = True
    if numOfSongs==0:
        print("There are no songs!")
        return 0
    if count < (numOfSongs-1):
        count += 1
    else:
        count = 0
    stop_call_back()
    file = f'music\\{music[count][3]}'
    pygame.mixer.music.load(file)

    # update song info dict
    update_song_info(file)
    update_song_start_pos(0)  # set start position as 0

    # reset slider position to 0 and set slider max equal to length of song
    position_slider.configure(value=0, to=song_info_dict['length'])

    play_call_back()

    global music_list
    music_list.selection_clear(0, END)
    music_list.select_set(count)

def play_selected(e):
    global music_list
    global is_paused
    global is_stopped
    global count
    is_paused = False
    is_stopped = True
    count = int(music_list.curselection()[0])
    print(music[count])
    file = f'music\\{music[count][-1]}'
    pygame.mixer.music.load(file)

    print(file)
    update_song_info(file)
    update_song_start_pos(0)
    position_slider.configure(value=0, to=song_info_dict['length'])

    play_call_back()

def play_after_shuffle(music):
    global listbox_total_count
    global count
    global is_paused
    global is_stopped
    is_paused = False
    is_stopped = True
    count = 0
    stop_call_back()
    file = f'music\\{music[count][3]}'
    pygame.mixer.music.load(file)

    # update song info dict
    update_song_info(file)
    update_song_start_pos(0)  # set start position as 0

    # reset slider position to 0 and set slider max equal to length of song
    position_slider.configure(value=0, to=song_info_dict['length'])

    play_call_back()

    global music_list
    music_list.selection_clear(0, END)
    music_list.select_set(count)


def update_song_info(file):
    print(file)  # file):#Sean
    audio = MP3(file)  # info about MP3 File
    tags = ID3(file)
    try:
        song_info_dict['Artist'] = tags['TPE1'].text[0]  # store Artist from MP3 Metadata Tag
    except:
        song_info_dict['Artist'] = 'Unknown'  # store Artist from MP3 Metadata Tag

    try:
        song_info_dict['Title'] = tags['TIT2'].text[0]  # store Song Title from MP3 Metadata Tag
    except KeyError:
        filename = file.split('\\')
        filename = filename[1].split('.')
        print(filename)
        song_info_dict['Title'] = filename[0]

    song_info_dict['length'] = audio.info.length  # find and store lenght of file, in seconds

    print(song_info_dict['Title'])


def update_song_start_pos(position):  # Sean
    song_info_dict[
        'start_pos'] = position  # must store song start position because pygame music uses relative position for MP3 Files.


def current_position():  # Sean
    try:
        realtivePosition = pygame.mixer.music.get_pos() / 1000  # get current relative song position from pygame, in seconds
        absolutePosition = song_info_dict[
                               'start_pos'] + realtivePosition  # find absolute position by adding relative positon to starting positon
        position_str = convert_seconds(absolutePosition)
        length = convert_seconds(song_info_dict['length'])  # length of song in h:mm:ss format

        # check if song has starded, if not return tupple (0:00, 0)
        if absolutePosition < 1:
            return ('0:00:00', 0)

        # if song is not at 0, but relative position is < 1, then song has ended. Return tupple(song length, length in seconds)
        elif realtivePosition < 0:
            return (length, song_info_dict['length'])

        # else return current position tupple
        else:
            return (position_str, absolutePosition)  # return tuple of (h:mm:ss, seconds)
    except:
        return ('0:00:00', 0)

def seek_position(seconds):  # Sean
    if numOfSongs==0:
        print("There are no songs!")
        return 0
    if seconds > song_info_dict['length']:  # if input is larger than length of song, play song from beginning
        pygame.mixer.music.rewind()
        pygame.mixer.music.play()
    else:
        pygame.mixer.music.play(
            start=seconds)  # else play song from desired starting position and update dictionary start position value
        song_info_dict['start_pos'] = seconds


def skip_forward_10():
    current = current_position()[1]
    new = current + 10
    if numOfSongs==0:
        print("There are no songs!")
        return 0
    if new < song_info_dict['length']:
        seek_position(new)

    print("Forward 10 Seconds")


def skip_backward_10():
    current = current_position()[1]
    new = current - 10
    if numOfSongs==0:
        print("There are no songs!")
        return 0
    if new > 0:
        seek_position(new)
    else:
        pygame.mixer.music.rewind()
        pygame.mixer.music.play()
        song_info_dict['start_pos'] = 0

    print("Backward 10 Seconds")


def shuffle_songs(conn, music, music_list):
    if numOfSongs==0:
        print("There are no songs!")
        return 0
    random.shuffle(music)
    print("Shuffle")
    music_list.delete(0,'end')
    for m in music:
        music_list.insert(END, m[1])
    play_after_shuffle(music)


def volume(x):
    pygame.mixer.music.set_volume(volumeSlider.get())
    current_volume = pygame.mixer.music.get_volume()


def update_position():  # update label showing file name, current position and song lenth
    """ update the label every second """

    global position_label  # update position label
    try:
        song_length = convert_seconds(song_info_dict['length'])
        position_label.configure(text=current_position()[0] + ' / ' + song_length)
    except:
        
        position_label.configure(text='No Song Loaded')

    global song_label  # update song Label

    try:
        song_label.configure(text='Now Playing: ' + song_info_dict['Title'])
    except:  # if no song is loaded, display ''
        song_label.configure(text='Add a Song!')

    # update slider position, ONLY IF MOUSE IS NOT CLICKING THE SLIDER!
    if not slider_mouse_clicked:
        position_slider.configure(value=current_position()[1])

    #Play next song on playlist at end of current song
    global music
    global numOfSongs
    global count
    for event in pygame.event.get():
        if event.type == MUSIC_END:
            if is_repeat:
                count -= 1
            next_call_back(music,numOfSongs)

    # schedule another timer
    position_label.after(100, update_position)  # makes a loop


def convert_seconds(seconds):
    # takes in a seconds value and returns a string in the form of h:mm:ss
    position = datetime.timedelta(seconds=seconds)  # convert to h:mm:ss.ms
    position_str = str(position).split(".")[0]  # drop microseconds and format as string
    return position_str


def slider_clicked(event):
    global slider_mouse_clicked
    slider_mouse_clicked = True


def slider_released(event):
    global slider_mouse_clicked
    slider_mouse_clicked = False

    # once mouse button is released, set slider to positon where the mouse was released
    seconds = position_slider.get()
    position_slider.configure(value=seconds)

    # then move song to the desired position
    seek_position(seconds)

'''
For questions see @Mikhail
Allows you to pick a song from any folder on your local machine.
Copies the song to the music folder if song is not already in folder
If artist field is blank, applies field as unkown
If title field is blank, copies file path minus the .mp3
calls create music function with title, artist, and filepath
music list also passed through argument to update total song count used for indexing
'''
def load_music(music_list):
    songs = filedialog.askopenfilenames(initialdir='music/', title="Choose A Song", filetype=(("Mp3 Files", "*.mp3",),))
    for song in songs:
        #  audio = MP3(song)  # info about MP3 File
        # shutil.copy(song , 'music/')


        tags = ID3(song)
        filename = song.split('/')
        filename = filename[-1]
        check = 'music/' + filename
        print(check)
        if os.path.isfile(check):
            print(f"{filename} already in music folder")
        else:
            print("Moving song to music folder")
            shutil.copy(song, 'music/')
        try:
            artist = tags['TPE1'].text[0]  # store Artist from MP3 Metadata Tag
        except KeyError:
            artist = "Unknown"
            tags["TPE1"] = TPE1(encoding=3, text=artist)
            tags.save(song)
        try:
            title = tags['TIT2'].text[0]  # store Song Title from MP3 Metadata Tag
        except KeyError:
            title_temp = filename.split(".")
            title = title_temp[0]
            tags["TIT2"] = TIT2(encoding=3, text=title)
        create_music(title, artist, filename, music_list)


def view():
    connect = sqlite3.connect('music.db')
    cursor_object = connect.cursor()
    cursor_object.execute("SELECT * FROM music")
    rows = cursor_object.fetchall()
    connect.close()
    print(rows)


def delete(connection):
    connect = sqlite3.connect('music.db')
    cursor_object = connect.cursor()
    # cursor_object.execute("DELETE FROM music WHERE title = ?", (title,))
    cursor_object.execute("DELETE FROM music")
    cursor_object.execute("SELECT * FROM music")
    print("Database music:\n")
    print(cursor_object.fetchall())
    music_list.delete(0,'end')
    music.clear()
    connect.commit()
    connect.close()
    global numOfSongs
    numOfSongs = get_num_of_songs(connection)
    print("number of songs", numOfSongs)
    play_call_back()
    song_info_dict.clear()
    update_position()

def update_count(music_list):
    global listbox_total_count
    listbox_total_count = music_list.size()
    return listbox_total_count

def close_program(root):
    root.destroy()
    pygame.mixer.music.unload()
    sys.exit()
    
def delete_all_songs(connection):
    sql = 'DELETE FROM music'
    c = connection.cursor()
    c.execute(sql)
    connection.commit()
    global numOfSongs
    numOfSongs = get_num_of_songs(connection)
    print("number of songs", numOfSongs)


def on_closing(connection):
    delete_all_songs(connection)





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
    global music
    music = get_all_music(connection)
    pygame.mixer.init()

    #set Pygame Music End Event
    pygame.init()
    global MUSIC_END
    MUSIC_END = pygame.USEREVENT+1
    pygame.mixer.music.set_endevent(MUSIC_END)

    

    global numOfSongs
    numOfSongs = get_num_of_songs(connection)
    try:
        file = f'music\\{music[0][3]}'
        update_song_info(file)
        update_song_start_pos(0)
        pygame.mixer.music.load(file)
        audio = MP3(file)  # info about MP3 File
        song_info_dict[
            'length'] = audio.info.length  # find and store lenght of file, in seconds, store in song_info_dict dictionary
    except IndexError:
        print("There are currently no songs in the MP3 player")
    root = Tk()
    root.geometry('500x600')
    root.resizable(False, False)

    global music_list
    music_list = Listbox(root, width=120)
    music_list.pack()
    

    # adding music lists in the list
    for m in music:
        music_list.insert(END, m[1])
    music_list.select_set(0)
    update_count(music_list)
    print(f"Showing all {listbox_total_count} songs")

    music_list.bind('<Double-Button-1>', play_selected)

    # play_btn = Button(root, text='play', command=play_call_back)
    # play_btn.pack()
    # stop_btn = Button(root, text='stop', command=stop_call_back)
    # stop_btn.pack()
    # prev_btn = Button(root, text='prev', command=lambda: prev_call_back(music, numOfSongs))
    # prev_btn.pack()
    # next_btn = Button(root, text='next', command=lambda: next_call_back(music, numOfSongs))
    # next_btn.pack()

    def change_repeat_icon():
        if is_repeat:
            repeat_btn.configure(image = repeat_once_img)
            repeat_btn['image'] = repeat_once_img
        else:
            repeat_btn.configure(image = repeat_img)
            repeat_btn['image'] = repeat_img

    def repeat():
        global is_repeat
        is_repeat = not is_repeat
        change_repeat_icon()


    # define player control: player control icons
    play_img = PhotoImage(file='Assets/icons/play_large.png')
    pause_img = PhotoImage(file='Assets/icons/pause_large.png')
    stop_img = PhotoImage(file='Assets/icons/stop.png')
    next_img = PhotoImage(file='Assets/icons/next.png')
    prev_img = PhotoImage(file='Assets/icons/prev.png')
    shuffle_img = PhotoImage(file='Assets/icons/shuffle.png')
    forward_img = PhotoImage(file='Assets/icons/FF.png')
    backward_img = PhotoImage(file='Assets/icons/FR.png')
    shuffle_active_img = PhotoImage(file='Assets/icons/shuffle_active.png')
    repeat_img = PhotoImage(file='Assets/icons/repeat.png')
    repeat_once_img = PhotoImage(file='Assets/icons/repeat_once.png')
    volume_img = ImageTk.PhotoImage(Image.open("Assets/icons/volume.png"))
    mute_img = ImageTk.PhotoImage(Image.open("Assets/icons/mute.png"))

    #  control btns
    control_btn_frame = Frame(root, width=600)
    control_btn_frame.pack()
    
    play_btn = Button(control_btn_frame, image=play_img, borderwidth=0, command=play_call_back)
    next_btn = Button(control_btn_frame, image=next_img, borderwidth=0, command=lambda: next_call_back(music, numOfSongs))
    prev_btn = Button(control_btn_frame, image=prev_img, borderwidth=0, command=lambda: prev_call_back(music, numOfSongs))
    shuffle_btn = Button(control_btn_frame, image=shuffle_img, borderwidth=0, command=lambda:shuffle_songs(connection, music, music_list)) 
    repeat_btn = Button(control_btn_frame, image=repeat_img, borderwidth=0, command=repeat)
    forward_btn = Button(control_btn_frame, image=forward_img, borderwidth=0, command=skip_forward_10)
    backward_btn = Button(control_btn_frame, image=backward_img, borderwidth=0, command=skip_backward_10)

    shuffle_btn.grid(row=0, column=0, padx=20, pady=30)
    prev_btn.grid(row=0, column=1, padx=20, pady=30)
    backward_btn.grid(row=0, column=2, padx=20, pady=30)
    play_btn.grid(row=0, column=3, padx=20, pady=30)
    forward_btn.grid(row=0, column=4, padx=20, pady=30)
    next_btn.grid(row=0, column=5, padx=20, pady=30)
    repeat_btn.grid(row=0, column=6, padx=20, pady=30)
    





    # Volume button
    # global volumeSlider
    # volumeLable = Label(root, text='Volume')
    # volumeLable.pack()
    # volumeSlider = Scale(root, from_=0.0, to=1.0, resolution=0.1, length=400, orient=HORIZONTAL, command=volume)
    # volumeSlider.pack()

    def mute_volume():
        global vol
        if volume_slider.get() > 0:
            vol = volume_slider.get()
            volume_slider.set(0)
            img = ImageTk.PhotoImage(Image.open("Assets/icons/mute.png"))
            volume_btn.configure(image=img)
            volume_img.image = img
        else:
            if vol <= 0: vol = 80
            volume_slider.set(vol)
            img = ImageTk.PhotoImage(Image.open("Assets/icons/volume.png"))
            volume_btn.configure(image=img)
            volume_img.image = img
        pygame.mixer.music.set_volume(volume_slider.get() / 100)
        volume_amount_lbl.configure(text=int(volume_slider.get()))

    def set_volume(e):
        global vol
        pygame.mixer.music.set_volume(volume_slider.get() / 100)
        volume_amount_lbl.configure(text=int(volume_slider.get()))
        if volume_slider.get() <= 0:
            img = ImageTk.PhotoImage(Image.open("Assets/icons/mute.png"))
            volume_btn.configure(image=img)
            volume_img.image = img
        else:
            img = ImageTk.PhotoImage(Image.open("Assets/icons/volume.png"))
            volume_btn.configure(image=img)
            volume_img.image = img

        # volume widget
    vol = 0

    volume_frame = Frame(root, width=100)
    volume_frame.pack()

    volume_btn = Button(volume_frame, bd=0, image=volume_img, command= mute_volume)
    volume_btn.grid(row=0, column=0)

    volume_amount_lbl = Label(volume_frame, text=int(pygame.mixer.music.get_volume() * 100))
    volume_amount_lbl.grid(row=0, column=2)



    volume_slider = Scale(volume_frame, orient=HORIZONTAL
                        , length=70,
                        bg='#333', troughcolor='#fff', sliderlength=10,
                        bd=0, showvalue=0,
                        command=set_volume)

    volume_slider.grid(row=0, column=1, padx=20)
    volume_slider.set(pygame.mixer.music.get_volume() * 100)
    
    # Show Current Positon
    global position_label
    try:
        song_length = convert_seconds(song_info_dict['length'])
        position_label = Label(text=f'0:00:00 / {song_length}')
        position_label.pack(expand=True)
        position_label.after(100, update_position)  # calls function after 1/10s
    except:
        
        position_label = Label(text='No Song Loaded')
        position_label.pack(expand=True)
        position_label.after(100, update_position)  # calls function after 1/10s

    # Now Playing Label
    global song_label
    try:
        song_label = ttk.Label(root, text=song_info_dict['Title'])
        song_label.pack()
    except:
        song_label = ttk.Label(root, text='Add a Song!')
        song_label.pack()

    # Position Slider
    global position_slider
    try:
        position_slider = ttk.Scale(root, from_=0, to=song_info_dict['length'], value=0, length=400)
        position_slider.pack(pady=20)
    except:
        position_slider = ttk.Scale(root, from_=0, to=100, value=0, length=400)
        position_slider.pack(pady=20)

    # bind mouse click and release events (only when clicking slider bar) to functions
    position_slider.bind('<Button-1>', slider_clicked)
    position_slider.bind('<ButtonRelease-1>', slider_released)

    # shuffle button
    # shuffle_btn = Button(root, text="shuffle", command=lambda: shuffle_songs(connection, music, music_list))
    # shuffle_btn.pack()

    # menu bar
    menubar = Menu(root)
    root.config(menu=menubar)
    FileMenu = Menu(menubar, tearoff=0)

    # File Menu
    menubar.add_cascade(label="File", menu=FileMenu)

    FileMenu.add_command(label="Add MP3 File(s)", command=lambda : load_music(music_list))
    FileMenu.add_command(label="Delete All Songs", command=lambda: delete(connection))
    FileMenu.add_command(label="Exit", command=lambda: close_program(root))


    list_box = Listbox()

   

    atexit.register(on_closing, connection)

    root.mainloop()


if __name__ == '__main__':
    main()

