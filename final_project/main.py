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
import download_song

db = Database()


current = 0
prev_pos = 0
song_current_pos = 0
timer_id = None
animate_id = None
is_paused = False
is_shuffled = False




# initialize pygame mixer
pygame.init()
pygame.mixer.init()

# set up a tkinter window
window = Tk()
window.geometry('800x600')
window.resizable(False, False)
window.configure(background='#8C84CF')


# setting up widigts 

menu_frame = Frame(window, bg='#E2DAFE', width=200, height=400)
menu_frame.place(x = 0, y = 0)

download_frame = Frame(window, bg='#8C84CF', width=600, height=400)

# music list frame
music_list_frame = Frame(window, width=600, height=400, bg='#8C84CF')
music_list_frame.place(x=200, y=0)

music_list_style = ttk.Style()
music_list_style.configure("Treeview", highlightthickness=0, bd=0, font=('Calibri', 10), pady=50) # Modify the font of the body
music_list_style.configure("Treeview", background="#8C84CF", foreground="#fff", fieldbackground="#8C84CF", selectbackground='red')
music_list_style.configure("Treeview.Heading", font=('Calibri', 10,'bold'), bg="#8C84CF", borderwidth=10) # Modify the font of the headings
# music_list_style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})]) # Remove the borders

music_list_style.map('Treeview', background = [('selected', 'black')])
music_list_style.map('Treeview', foreground = [('selected', '#fff')])

# treeview widget to list music
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



update_song_frame = Frame(music_list_frame, width=570, height=120, bg='#8C84CF')
update_song_frame.pack()




bottom_frame = Frame(window, bg='#E2DAFE', width=800, height=200)
bottom_frame.place(x=0, y=400)

cover_art_frame = Frame(bottom_frame, bg='#333', width=200, height=200)
cover_art_frame.place(x=0, y=0)

image = ImageTk.PhotoImage(Image.open("images/cover_art/default.png"))
cover_lbl = Label(cover_art_frame, image=image)
song_info_lbl = Label(cover_art_frame, bg= '#333', fg='#fff', text="", font=("Helvetica", 12))
cover_lbl.pack(padx=25, pady=25)
song_info_lbl.place(x=200, y=175)

controller = Frame(bottom_frame, bg='#E2DAFE', width=600, height=200)
controller.place(x=200, y=0, width=600, height=200)



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



volume_var = DoubleVar()
vol = 0
def set_volume(e):
    global volume_var
    global vol
    pygame.mixer.music.set_volume(volume_var.get() / 100)
    volume_amount_lbl.configure(text=int(volume_var.get()))
    if volume_var.get() <= 0:
        img = ImageTk.PhotoImage(Image.open("images/mute.png"))
        volume_icon_lbl.configure(image=img)
        volume_img.image = img
    else:
        img = ImageTk.PhotoImage(Image.open("images/volume.png"))
        volume_icon_lbl.configure(image=img)
        volume_img.image = img

def mute_volume():
    global volume_var
    global vol
    if volume_var.get() > 0:
        vol = volume_var.get()
        volume_var.set(0)
        img = ImageTk.PhotoImage(Image.open("images/mute.png"))
        volume_icon_lbl.configure(image=img)
        volume_img.image = img
    else:
        volume_var.set(vol)
        img = ImageTk.PhotoImage(Image.open("images/volume.png"))
        volume_icon_lbl.configure(image=img)
        volume_img.image = img
    pygame.mixer.music.set_volume(volume_var.get() / 100)
    volume_amount_lbl.configure(text=int(volume_var.get()))

volume_frame = Frame(controller, width=100, bg='#E2DAFE')
volume_frame.grid(row=2, column=0, padx=30, pady=30, sticky=E)
volume_img = ImageTk.PhotoImage(Image.open("images/volume.png"))
volume_icon_lbl = Button(volume_frame, bd=0, image=volume_img, bg='#E2DAFE', command= mute_volume)
volume_icon_lbl.grid(row=0, column=0)
volume_amount_lbl = Label(volume_frame, bg='#E2DAFE', text=int(pygame.mixer.music.get_volume() * 100))
volume_amount_lbl.grid(row=0, column=2)


volume_slider = Scale(volume_frame, orient=HORIZONTAL,
                      variable=volume_var, length=70,
                      bg='#333', troughcolor='#fff', sliderlength=10,
                      bd=0, showvalue=0,
                      command=set_volume)

volume_var.set(pygame.mixer.music.get_volume() * 100)
volume_slider.grid(row=0, column=1, padx=20)



# get the current song information
try:
    with open('current.txt') as file:
        current_setting = file.readline()
    
except FileNotFoundError:
    print('no saved setting')
else:
    if current_setting != '':
        print(current_setting)
        current_setting = current_setting.split('-')
        current = int(current_setting[0])
        song_current_pos = int(current_setting[1])
        pygame.mixer.music.set_volume(float(current_setting[2]) / 100)

# fetch music from the DB
playlist = db.get_songs()
print(playlist)

# music lists
def update_playlist(playlist):
    music_list.delete(*music_list.get_children())
    if playlist:
        for i, song in enumerate(playlist):
            music_list.insert('', index='end', text='', iid=i, values = (i+1, song[1], song[5], time.strftime('%M:%S', time.gmtime(song[4]))))

update_playlist(playlist)



def load_song(cur):
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

load_song(current)

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

    if pygame.mixer.music.get_busy():
        slider_var.set(count)
        timer_lbl.configure(text=time.strftime('%M:%S', time.gmtime(count)))
        timer_id = window.after(1000, time_counter, count + 1)
        song_current_pos = count
        
    else:
        pygame.mixer.music.stop()
        timer_lbl.configure(text=time.strftime('%M:%S', time.gmtime(slider_var.get())))
        window.after_cancel(timer_id)
        next()



def change_play_icon():
    global is_paused

    if pygame.mixer.music.get_busy():
        play_btn.configure(image=pause_img)
        play_btn.image = pause_img
    else:
        play_btn.configure(image=play_img)
        play_btn.image = play_img


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
         animate_song_info()

    change_play_icon()


def next():
    global current
    global song_current_pos
    if current < len(playlist) - 1:
        current += 1
        pygame.mixer.music.unload()     
        song_current_pos = 0
        load_song(current)
        play(song_current_pos)
        prev_btn['state'] = 'normal'
    else:
        pygame.mixer.music.unload()
         
    if current == len(playlist) - 1:
        next_btn['state'] = 'disabled'
    else:
        next_btn['state'] = 'normal'


def prev():
    global current
    global song_current_pos

    if current >= 0:
        current -= 1
        pygame.mixer.music.unload()
        song_current_pos = 0
        load_song(current)
        play(song_current_pos)
        change_play_icon()
        next_btn['state'] = 'normal'
    
    if current == 0:
        prev_btn['state'] = 'disabled'
    else:
        prev_btn['state'] = 'normal'


def repeat():
    pass

def shuffle():
    global playlist
    global is_shuffled
    global current
    global prev_pos

    if not is_shuffled:
        prev_pos = current
        current_song = playlist[current][1]
        random.shuffle(playlist)
        for idx, song in enumerate(playlist):
            if song.count(current_song) > 0:
                current = idx
        is_shuffled = not is_shuffled
    else:
        playlist = db.get_songs()
        current = prev_pos
        is_shuffled = not is_shuffled
    update_playlist()
    music_list.focus(cur)
    music_list.selection_set(cur)
    

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

    if e.y > 18:
        selected_song = music_list.selection()[0]
        current = int(selected_song)
        if timer_id:
            window.after_cancel(timer_id)
        song_current_pos = 0
        load_song(current)

        if current > 0 and current < len(playlist) - 1:
            next_btn['state'] = 'normal'
            prev_btn['state'] = 'normal'
        elif current == 0:
            prev_btn['state'] = 'disabled'
            next_btn['state'] = 'normal'
        elif current == len(playlist) - 1:
            next_btn['state'] = 'disabled'    
            prev_btn['state'] = 'normal'    
        
        play(start=song_current_pos)




# define player control: player control icons
play_img = PhotoImage(file='images/play.png')
pause_img = PhotoImage(file='images/pause.png')
stop_img = PhotoImage(file='images/stop.png')
next_img = PhotoImage(file='images/next.png')
prev_img = PhotoImage(file='images/prev.png')
shuffle_img = PhotoImage(file='images/shuffle.png')
repeat_img = PhotoImage(file='images/repeat.png')

#  control btns
control_btn_frame = Frame(controller, width=600, bg='#E2DAFE')
control_btn_frame.grid(row=1, column=0)
play_btn = Button(control_btn_frame, image=play_img, borderwidth=0,bg='#E2DAFE', command=play)
next_btn = Button(control_btn_frame, image=next_img, borderwidth=0,bg='#E2DAFE', command=next)
prev_btn = Button(control_btn_frame, image=prev_img, borderwidth=0,bg='#E2DAFE', command=prev)
repeat_btn = Button(control_btn_frame, image=repeat_img, borderwidth=0,bg='#E2DAFE', command=repeat)
shuffle_btn = Button(control_btn_frame, image=shuffle_img, borderwidth=0,bg='#E2DAFE', command=shuffle)


shuffle_btn.grid(row=0, column=0, padx=30, pady=30)
prev_btn.grid(row=0, column=1, padx=30, pady=30)
play_btn.grid(row=0, column=2, padx=30, pady=30)
next_btn.grid(row=0, column=3, padx=30, pady=30)
repeat_btn.grid(row=0, column=4, padx=30, pady=30)




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
        playlist = db.get_songs()
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
            if found_song[-1] != 'default.png':
                db.update_song_cover_art(id, song[-1])
        
        db.update_artist_name(artist_name, id)
        db.update_song_title(song_title, id)

        os.rename(f"./music/{song[2]}", f"./music/{song_title}.mp3")
        playlist = db.get_songs()
        update_playlist(playlist)

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
    print('searching')
    url = search_input.get()
    search_input.delete(0, END)
    try:
        download_song.download_song(url)
    except:
        messagebox.showerror(message="couldn't download song, please try again ")
    else:
        messagebox.showinfo(message="music has been downloaded successfuly")

    
def download_songs():

    music_list_frame.place_forget()
    download_frame.place(x=200, y=0)

search_input = Entry(download_frame, width=30)
search_input.place(x=20, y=20)

search_btn = Button(download_frame, text='Search', bd=0 ,bg='#222', fg='#fff', padx=10, pady=5, command=download)
search_btn.place(x=300, y=20)

def home():
    global current
    global playlist
    download_frame.place_forget()
    music_list_frame.place(x=200, y=0)
    playlist = db.get_songs()
    update_playlist(playlist)
    
download_btn = Button(menu_frame, bg='#222', fg='#fff', text='Download a song', bd=0, padx=10,pady=5, command=download_songs)
download_btn.place(x=10, y=10)
home_btn = Button(menu_frame, bg='#222', fg='#fff', text='Home', bd=0, padx=10, pady=5, command=home)
home_btn.place(x=10, y=50)

# ****************************************************************

#save currently playing song in a file
def save_on_window_close():
    pygame.mixer.music.pause()
    global current
    if is_shuffled:
        current = prev_pos
    print(f'{current} at {song_current_pos}')
    with open('current.txt', 'w') as file:
        file.write(f'{current}-{song_current_pos}-{volume_var.get()}')
    window.destroy()
window.protocol('WM_DELETE_WINDOW', save_on_window_close)

# ****************************************************************

# select a song from our computer
def open_file():
    files = fd.askopenfilenames(initialdir='./music', title='Select file', filetypes=(('mp3 files', '*.mp3'), ('all files', '*.*')))
    for file in files:
        print(file)
        song_file = file.split('/')[-1]
        song_title = song_file.split('.')[0]
        song = db.find_song_by_song_title(song_title)
        if song:
            print('song exists')
            messagebox.showwarning(message=f'"{song_file[:-4]}" is already in your playlist')
        else:
            if not os.path.exists(f"./music/{song_file}"):
                shutil.copy(file, f"./music/{song_file}")

            
            s = Song(song_title, song_file)
            db.add_song(s.get_song_title(), s.get_song_file(), s.get_song_duration(), s.artist.get_artist_name(), s.artist.get_cover_art())
            home()

menu = Menu(window)
filemenu = Menu(menu, tearoff=0)
filemenu.add_command(label='New', comman=open_file)
menu.add_cascade(label='File', menu=filemenu)
window.config(menu=menu)

# ****************************************************************

window.mainloop()