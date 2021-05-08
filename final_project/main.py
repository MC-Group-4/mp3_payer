from tkinter import *
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import messagebox
from PIL import ImageTk, Image
import pygame
import os
import shutil
import time
import random
from model import Song
from db import Database
from download_song import download_song
import json

db = Database()


current = 0
song_current_pos = 0   
timer_id = None
animate_id = None
is_paused = False
is_shuffled = False
is_repeat = False
shuffled_playlist = []
playlist = []



# initialize pygame mixer
pygame.init()
pygame.mixer.init()

# load saved settings
try:
    with open('current_settings.json') as file:
        current_settings = json.load(file)
    
except FileNotFoundError:
    print('no saved setting')
else:
    if current_settings != '':
        current = current_settings['current']
        song_current_pos = current_settings['song_current_pos']
        is_repeat = current_settings['is_repeat']
        is_shuffled = current_settings['is_shuffled']
        shuffled_playlist = current_settings['shuffled_playlist']
        pygame.mixer.music.set_volume(float(current_settings['volume']) / 100)


# fetch music from the DB
def fetch_songs():
    global playlist
    if is_shuffled:
        playlist = shuffled_playlist[:]
    else:
        playlist = db.get_songs()


# update music lists
def update_playlist(playlist):

    music_list.delete(*music_list.get_children())
    if playlist:
        for i, song in enumerate(playlist):
            music_list.insert('', index='end', text='', iid=i, values = (i+1, song[1], song[5], time.strftime('%M:%S', time.gmtime(song[4]))))
    
    music_list.focus(current)
    music_list.selection_set(current)


def load_current_song_info(cur): 
    global slider

    music_list.focus(cur)
    music_list.selection_set(cur)
          
    id, song_title, song_file, album , song_duration, artist_name, cover_art = playlist[cur]
  
    # song = os.path.join(base, song_file)
    song = f'music/{song_file}'
    pygame.mixer.music.load(song)

    timer_lbl.configure(text=time.strftime('%M:%S', time.gmtime(song_current_pos)))
    slider_var.set(song_current_pos)
    duration_lbl.configure(text=time.strftime('%M:%S', time.gmtime(song_duration)))
    img = ImageTk.PhotoImage(Image.open(f"images/cover_art/{cover_art}"))
    cover_lbl.configure(image=img)
    cover_lbl.image = img
    song_info_lbl.configure(text=f"{song_title} - {artist_name}")


    slider['to'] = song_duration


def animate_song_info(x=100):
    global animate_id
    if animate_id:
        window.after_cancel(animate_id)
    if pygame.mixer.music.get_busy():
        song_info_lbl.place(x=x, y=175)
        if x == -100:
            x = 100
        animate_id = window.after(200, animate_song_info, x-2)
    else:
        x = 0
        if animate_id:
            window.after_cancel(animate_id)


def time_counter(count=0):
    global timer_id
    global song_current_pos
    global current

    if pygame.mixer.music.get_busy():
        slider_var.set(count)
        timer_lbl.configure(text=time.strftime('%M:%S', time.gmtime(count)))
        timer_id = window.after(1000, time_counter, count + 1)
        song_current_pos = count
        
    else:
        pygame.mixer.music.stop()
        timer_lbl.configure(text=time.strftime('%M:%S', time.gmtime(slider_var.get())))
        window.after_cancel(timer_id)
        if is_repeat:
            current -= 1
        next()


def change_volume_icon():
    if pygame.mixer.music.get_volume() <= 0:
        volume_btn.configure(image=mute_img)
        volume_img.image = mute_img
    else:
        volume_btn.configure(image=volume_img)
        volume_img.image = volume_img



def change_play_icon():
    global is_paused

    if pygame.mixer.music.get_busy():
        play_btn.configure(image=pause_img)
        play_btn.image = pause_img
    else:
        play_btn.configure(image=play_img)
        play_btn.image = play_img

def change_next_prev_icons():
    if current > 0 and current < len(playlist) - 1:
        next_btn['state'] = 'normal'
        prev_btn['state'] = 'normal'
    elif current == 0:
        prev_btn['state'] = 'disabled'
        next_btn['state'] = 'normal'
    elif current == len(playlist) - 1:
        next_btn['state'] = 'disabled'    
        prev_btn['state'] = 'normal'

def change_repeat_icon():
    if is_repeat:
        repeat_btn.configure(image = repeat_once_img)
        repeat_btn['image'] = repeat_once_img
    else:
        repeat_btn.configure(image = repeat_img)
        repeat_btn['image'] = repeat_img

def change_shuffle_icon():
    if is_shuffled:
        shuffle_btn.configure(image = shuffle_active_img)
        shuffle_btn['image'] = shuffle_active_img
    else:
        shuffle_btn.configure(image = shuffle_img)
        shuffle_btn['image'] = shuffle_img

def set_volume(e):
    global volume_var
    global vol
    pygame.mixer.music.set_volume(volume_var.get() / 100)
    volume_amount_lbl.configure(text=int(volume_var.get()))
    if volume_var.get() <= 0:
        img = ImageTk.PhotoImage(Image.open("images/mute.png"))
        volume_btn.configure(image=img)
        volume_img.image = img
    else:
        img = ImageTk.PhotoImage(Image.open("images/volume.png"))
        volume_btn.configure(image=img)
        volume_img.image = img

def mute_volume():
    global volume_var
    global vol
    if volume_var.get() > 0:
        vol = volume_var.get()
        volume_var.set(0)
        img = ImageTk.PhotoImage(Image.open("images/mute.png"))
        volume_btn.configure(image=img)
        volume_img.image = img
    else:
        if vol <= 0: vol = 80
        volume_var.set(vol)
        img = ImageTk.PhotoImage(Image.open("images/volume.png"))
        volume_btn.configure(image=img)
        volume_img.image = img
    pygame.mixer.music.set_volume(volume_var.get() / 100)
    volume_amount_lbl.configure(text=int(volume_var.get()))

def play(start=song_current_pos):
    global is_paused
    global timer_id

    if timer_id:
        window.after_cancel(timer_id)
    if  pygame.mixer.music.get_busy() and not is_paused:
        pygame.mixer.music.pause()
        is_paused = not is_paused
    elif not pygame.mixer.music.get_busy() and not is_paused:
        pygame.mixer.music.play(start=start)
        time_counter(slider_var.get())
        animate_song_info()
    else:
         pygame.mixer.music.unpause()
         is_paused = not is_paused
         time_counter(slider_var.get())
        #  time_counter(pygame.mixer.music.get_pos())
         animate_song_info()

    change_play_icon()
    change_next_prev_icons()


def next():
    global current
    global song_current_pos
    if current < len(playlist) - 1:
        current += 1
        pygame.mixer.music.unload()     
        song_current_pos = 0
        load_current_song_info(current)
        play(song_current_pos)
        # prev_btn['state'] = 'normal'
    else:
        song_current_pos = 0
        load_current_song_info(current)
        change_play_icon()


def prev():
    global current
    global song_current_pos

    if current >= 0:
        current -= 1
        pygame.mixer.music.unload()
        song_current_pos = 0
        load_current_song_info(current)
        play(song_current_pos)
        change_play_icon()
        next_btn['state'] = 'normal'

def repeat():
    global is_repeat
    is_repeat = not is_repeat
    change_repeat_icon()

def shuffle():
    global playlist
    global is_shuffled
    global current
    global shuffled_playlist

    if not is_shuffled:
        current_song = playlist[current][1]
        random.shuffle(playlist)

        shuffled_playlist = playlist[:]

        for idx, song in enumerate(playlist):
            if song.count(current_song) > 0:
                current = idx

        is_shuffled = not is_shuffled
    else:
        current_song = playlist[current][1]
        playlist = db.get_songs()

        shuffled_playlist = []

        for idx, song in enumerate(playlist):
            if song.count(current_song) > 0:
                current = idx

        is_shuffled = not is_shuffled
    update_playlist(playlist)
    change_shuffle_icon()
    change_next_prev_icons()
    

def skip_song(e):
    global is_paused
    pygame.mixer.music.pause()
    if timer_id:
        window.after_cancel(timer_id)
    value = slider_var.get()
    timer_lbl.configure(text=time.strftime('%M:%S', time.gmtime(value)))
    play(start=value)

def play_selected(e):
    global current
    global timer_id
    global is_paused
    global song_current_pos
    is_paused = False
    if e.y > 25:
        selected_song = music_list.selection()[0]
        current = int(selected_song)
        if timer_id:
            window.after_cancel(timer_id)
        song_current_pos = 0
        load_current_song_info(current)
       
        change_next_prev_icons()
        play(start=song_current_pos)


#********************************************************************************************************
# set up a tkinter window
window = Tk()
window.geometry('800x600')
window.resizable(False, False)
window.configure(background='#8C84CF')


# setting up widigts 

menu_frame = Frame(window, bg='#E2DAFE', width=200, height=400)
menu_frame.place(x = 0, y = 0)

# download window frame
download_frame = Frame(window, bg='#8C84CF', width=600, height=400)

# music list frame
music_list_frame = Frame(window, width=600, height=400, bg='#8C84CF')
music_list_frame.place(x=200, y=0)


bottom_frame = Frame(window, bg='#E2DAFE', width=800, height=200)
bottom_frame.place(x=0, y=400)

cover_art_frame = Frame(bottom_frame, bg='#333', width=200, height=200)
cover_art_frame.place(x=0, y=0)

# styling music list table
music_list_style = ttk.Style()
music_list_style.configure("Treeview", highlightthickness=0, bd=0, font=('Calibri', 10), pady=50) # Modify the font of the body
music_list_style.configure("Treeview", background="#8C84CF", foreground="#fff", fieldbackground="#8C84CF", selectbackground='red')
music_list_style.configure("Treeview.Heading", font=('Calibri', 10,'bold'), bg="#8C84CF", borderwidth=10) # Modify the font of the headings
music_list_style.map('Treeview', background = [('selected', 'black')])
music_list_style.map('Treeview', foreground = [('selected', '#fff')])

# setting up treeview widget for the list music
music_list = ttk.Treeview(music_list_frame, columns=("#", "Title", "Artist" ,"Duration"), height=10)

music_list.column("#0", width=0, minwidth=0)
music_list.column("#", width=50, minwidth=50, anchor=W)
music_list.column("Title", width=200, minwidth=150, anchor=W)
music_list.column("Artist", width=200, minwidth=150, anchor=W)
music_list.column("Duration", width=100, minwidth=80, anchor=W)

music_list.heading("#0", text="", anchor=W)
music_list.heading("#", text="#", anchor=W)
music_list.heading("Title", text="Title", anchor=W)
music_list.heading("Artist", text="Artist", anchor=W)
music_list.heading("Duration", text="Duration", anchor=W)

# scroll bar for the music list treeview
ttk.Style().configure("Vertical.TScrollbar", background="#8C84CF", darkcolor='red', lightcolor='blue', troughcolor='#000', bordercolor='#fff', arrowcolor='red')
sb = ttk.Scrollbar(music_list_frame, orient="vertical", command=music_list.yview, style="Vertical.TScrollbar")
sb.pack(side=RIGHT, fill=Y, expand=True)
music_list.configure(yscrollcommand=sb.set)

music_list.pack()

# update song info frame
update_song_frame = Frame(music_list_frame, width=570, height=120, bg='#8C84CF')
update_song_frame.pack()




cover_art_img = ImageTk.PhotoImage(Image.open("images/cover_art/default.png"))
cover_lbl = Label(cover_art_frame, image=cover_art_img)
song_info_lbl = Label(cover_art_frame, bg= '#333', fg='#fff', text="", font=("Helvetica", 12))
cover_lbl.pack(padx=25, pady=25)
song_info_lbl.place(x=200, y=175)

controller = Frame(bottom_frame, bg='#E2DAFE', width=600, height=200)
controller.place(x=200, y=0, width=600, height=200)




# define player control: player control icons
play_img = PhotoImage(file='images/play_large.png')
pause_img = PhotoImage(file='images/pause_large.png')
stop_img = PhotoImage(file='images/stop.png')
next_img = PhotoImage(file='images/next.png')
prev_img = PhotoImage(file='images/prev.png')
shuffle_img = PhotoImage(file='images/shuffle.png')
shuffle_active_img = PhotoImage(file='images/shuffle_active.png')
repeat_img = PhotoImage(file='images/repeat.png')
repeat_once_img = PhotoImage(file='images/repeat_once.png')
volume_img = ImageTk.PhotoImage(Image.open("images/volume.png"))
mute_img = ImageTk.PhotoImage(Image.open("images/mute.png"))

#  control btns
control_btn_frame = Frame(controller, width=600, bg='#E2DAFE')
control_btn_frame.grid(row=1, column=0)
play_btn = Button(control_btn_frame, image=play_img, borderwidth=0,bg='#E2DAFE', command=play)
next_btn = Button(control_btn_frame, image=next_img, borderwidth=0,bg='#E2DAFE', command=next)
prev_btn = Button(control_btn_frame, image=prev_img, borderwidth=0,bg='#E2DAFE', command=prev)
shuffle_btn = Button(control_btn_frame, image=shuffle_img, borderwidth=0,bg='#E2DAFE', command=shuffle) 
repeat_btn = Button(control_btn_frame, image=repeat_img, borderwidth=0,bg='#E2DAFE', command=repeat)

shuffle_btn.grid(row=0, column=0, padx=30, pady=30)
prev_btn.grid(row=0, column=1, padx=30, pady=30)
play_btn.grid(row=0, column=2, padx=30, pady=30)
next_btn.grid(row=0, column=3, padx=30, pady=30)
repeat_btn.grid(row=0, column=4, padx=30, pady=30)

# music slider

slider_var = IntVar()
timer_frame = Frame(controller, width=600, bg="#8C84CF")
timer_frame.grid(row=0, column=0)
timer_lbl = Label(timer_frame, background="#8C84CF")
timer_lbl.grid(row=0, column=0, padx=10, pady=10)

duration_lbl = Label(timer_frame, text='end', background="#8C84CF")
duration_lbl.grid(row=0, column=2, padx=10, pady=10)

ttk.Style(window).configure("myStyle.Horizontal.TScale", background="#8C84CF", foreground="#fff", fieldbackground="#8C84CF")

slider = ttk.Scale(timer_frame, orient=HORIZONTAL,
               variable=slider_var,length=475, style="myStyle.Horizontal.TScale")
slider.grid(row=0, column=1, padx=10, pady=10)

# volume widget
volume_var = DoubleVar()
vol = 0
volume_var.set(pygame.mixer.music.get_volume() * 100)

volume_frame = Frame(controller, width=100, bg='#E2DAFE')
volume_frame.grid(row=2, column=0, padx=30, pady=10, sticky=E)

volume_btn = Button(volume_frame, bd=0, image=volume_img, bg='#E2DAFE', command= mute_volume)
volume_btn.grid(row=0, column=0)

volume_amount_lbl = Label(volume_frame, bg='#E2DAFE', text=int(pygame.mixer.music.get_volume() * 100))
volume_amount_lbl.grid(row=0, column=2)



volume_slider = Scale(volume_frame, orient=HORIZONTAL,
                      variable=volume_var, length=70,
                      bg='#333', troughcolor='#fff', sliderlength=10,
                      bd=0, showvalue=0,
                      command=set_volume)

volume_slider.grid(row=0, column=1, padx=20)


#*********************************************************************************************************************************************



fetch_songs()
update_playlist(playlist)
load_current_song_info(current)
change_next_prev_icons()
change_shuffle_icon()
change_repeat_icon()
change_volume_icon()



# ****************************************************************

#EVENTS

# play music by double clicking music list items
music_list.bind('<Double-Button-1>', play_selected)

# play song at a specific positon
slider.bind('<ButtonRelease-1>', skip_song)

def play_pause(e):
    play()

# play/pause music using the spacebar key
window.bind('<space>', play_pause)

# ****************************************************************

# update song title and artist name, delete songs from the music list
def delete_song(song):
    global playlist
    id = song[0]
    s = db.find_song_by_id(id)
    answer = messagebox.askyesno(title= "Delete Song", message=f"Are you sure you want to delete {s[1]}?")
    if answer:
        db.delete_song(id)
        # os.remove(f"./music/{song[2]}")
        fetch_songs()
        update_playlist(playlist)

        song_title_input.delete(0, END)
        artist_name_input.delete(0, END)
        
        song_title_input.place_forget()
        artist_name_input.place_forget()
        save_btn.place_forget()

def update_song(song):
    window.unbind('<space>')
    song_title_input.place(x=10, y=40)
    artist_name_input.place(x=180, y=40)

    song_title_lbl.place(x=9, y=15)
    artist_name_lbl.place(x=179, y=15)

    save_btn.place(x=10, y=65)

    delete_btn.place_forget()
    edit_btn.place_forget()

    song_title_input.insert(END, song[1])
    artist_name_input.insert(END, song[5])


def save(song):
    global playlist
    id = song[0]
    if len(song_title_input.get()) > 0 and len(artist_name_input.get()) > 0:
        artist_name = artist_name_input.get()
        song_title = song_title_input.get()

        for found_song in db.find_song_by_artist_name(artist_name):
            print(found_song)
            if found_song[-1] != 'default.png':
                print(found_song[5])
                print(found_song[-1])
                db.update_song_cover_art(id, found_song[-1])
        
        db.update_artist_name(artist_name, id)
        db.update_song_title(song_title, id)

        os.rename(f"./music/{song[2]}", f"./music/{song_title}.mp3") # this line has bugs (need to fix it)

        fetch_songs()
        update_playlist(playlist)
        change_next_prev_icons()

        song_title_input.delete(0, END)
        artist_name_input.delete(0, END)

        song_title_input.place_forget()
        artist_name_input.place_forget()
        song_title_lbl.place_forget()
        artist_name_lbl.place_forget()

        save_btn.place_forget()
    else:
        messagebox.showerror(message='Fileds cannot be empty')
   

delete_btn = Button(update_song_frame, text='Delete', bd=0, bg='#222', fg='#fff', padx=5, pady=5, width=10)
edit_btn = Button(update_song_frame, text='Edit', bd=0, bg='#222', fg='#fff', padx=5, pady=5, width=10)
save_btn = Button(update_song_frame, text='Save', bd=0, bg='#222', fg='#fff', padx=5, pady=5, width=10)
song_title_lbl = Label(update_song_frame, text='Song Title: ', bg='#8C84CF')
artist_name_lbl = Label(update_song_frame, text='Artist Name: ', bg='#8C84CF')
song_title_input = Entry(update_song_frame, bd=0, width=25)
artist_name_input = Entry(update_song_frame, bd=0, width=25)



def song_selected(e):
    song_id = int(music_list.selection()[0])

    if song_id != current:
        song_detail = playlist[song_id]
        song = db.find_song_by_id(song_detail[0])

        delete_btn.place(x=10, y=65)
        edit_btn.place(x=120, y=65)

        song_title_input.place_forget()
        artist_name_input.place_forget()
        song_title_lbl.place_forget()
        artist_name_lbl.place_forget()
        save_btn.place_forget()

        song_title_input.delete(0, END)
        artist_name_input.delete(0, END)
    else:
        delete_btn.place_forget()
        edit_btn.place_forget()



    delete_btn.configure(command=lambda: delete_song(song))
    edit_btn.configure(command=lambda: update_song(song))
    save_btn.configure(command=lambda: save(song))

music_list.bind('<<TreeviewSelect>>', song_selected)

# ****************************************************************

# download songs from youtube
def download():
    global shuffled_playlist
    downloading = Label(download_frame, text='downloading...')
    
    window.unbind('<space>')


    print('searching')
    song_title = search_song_title_input.get()
    search_song_title_input.delete(0, END)

    artist_name = search_artist_name_input.get()
    search_artist_name_input.delete(0, END)
    try:
        song = download_song(song_title, artist_name)
        downloading.place_forget()
    except:
        messagebox.showerror(message="couldn't download song, please try again ")
        downloading.place_forget()
    else:
        print(song)
        shuffled_playlist.append(song)
        downloading.place_forget()
        messagebox.showinfo(message="music has been downloaded successfuly")

    
def download_songs():

    music_list_frame.place_forget()
    download_frame.place(x=200, y=0)
    window.unbind('<space>')

search_song_title_lbl = Label(download_frame, bg="#8C84CF",text="Song Title: ")
search_song_title_input = Entry(download_frame, width=30)
search_song_title_lbl.place(x=20, y=20)
search_song_title_input.place(x=20, y=45)

search_artist_name_lbl = Label(download_frame, bg="#8C84CF",text="Artist Name: ")
search_artist_name_input = Entry(download_frame, width=30)
search_artist_name_lbl.place(x=220, y=20)
search_artist_name_input.place(x=220, y=45)

download_btn = Button(download_frame, text='Download', bd=0 ,bg='#222', fg='#fff', padx=10, pady=1, command=download)
download_btn.place(x=420, y=45)

def home():
    global current
    global playlist
    download_frame.place_forget()
    music_list_frame.place(x=200, y=0)
    fetch_songs()
    update_playlist(playlist)
    change_next_prev_icons()
    
download_btn = Button(menu_frame, bg='#222', fg='#fff', text='Download a song', bd=0, padx=10,pady=5, command=download_songs)
download_btn.place(x=10, y=10)
home_btn = Button(menu_frame, bg='#222', fg='#fff', text='Home', bd=0, padx=10, pady=5, command=home)
home_btn.place(x=10, y=50)

# ****************************************************************

#save currently playing song in a file
def save_on_window_close():
    global current
    pygame.mixer.music.pause()
    current_settings = {
        'current' : current,
        'song_current_pos': song_current_pos,
        'volume': volume_var.get(),
        'is_repeat': is_repeat,
        'is_shuffled': is_shuffled,
        'shuffled_playlist': shuffled_playlist
    }

    with open('current_settings.json', 'w') as file:
        json.dump(current_settings, file, indent=4)
    window.destroy()
window.protocol('WM_DELETE_WINDOW', save_on_window_close)

# ****************************************************************

# select a song from our computer
def open_file():
    global shuffled_playlist
    files = fd.askopenfilenames(initialdir='./music', title='Select file', filetypes=(('mp3 files', '*.mp3'), ('all files', '*.*')))
    for file in files:
        song_file = file.split('/')[-1]
        song_title = song_file.split('.')[0]
        song = db.find_song_by_song_title(song_title)
        print(song_title, song_file)
        if song:
            print('song exists')
            messagebox.showwarning(message=f'"{song_file[:-4]}" is already in your playlist')
        else:
            if not os.path.exists(f"./music/{song_file}"):
                shutil.copy(file, f"./music/{song_file}")
            try:
                s = Song(song_title, song_file)
            except:
                messagebox.showerror(title='wrong format', message="the file format is not supported.\ncan't sync to MPEG frame")
            else:
                db.add_song(s.get_song_title(), s.get_song_file(), s.get_song_duration(), s.artist.get_artist_name(), s.artist.get_cover_art())
                found_song = db.find_song_by_song_title(s.get_song_title())
                shuffled_playlist.append(found_song)
                home()

menu = Menu(window)
filemenu = Menu(menu, tearoff=0)
filemenu.add_command(label='New', comman=open_file)
menu.add_cascade(label='File', menu=filemenu)
window.config(menu=menu)

# ****************************************************************

window.mainloop()