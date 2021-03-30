from functions import *
from tkinter import *
import pygame
from tkinter import filedialog

global paused
paused = False


root = Tk()
root.title("Mikhail's ugly mp3 player test")
root.iconbitmap()
root.geometry("500x300")

# Init Mixer
pygame.mixer.init()

def load_music():
    music = filedialog.askopenfilename(initialdir='music/', title="Choose A Song", filetype=(("Mp3 Files", "*.mp3",),))
    music = music.split('/')[-1]
    music = music.replace(".mp3","")
    music_list.insert(END,music)

def load_lots_of_music():
    songs = filedialog.askopenfilenames(initialdir='music/', title="Choose A Song", filetype=(("Mp3 Files", "*.mp3",),))
    for song in songs:
        song = song.split('/')[-1]
        song = song.replace(".mp3", "")
        music_list.insert(END, song)

def play():
    song = music_list.get(ACTIVE)
    song = f'music/{song}.mp3'
    pygame.mixer.music.load(song)
    pygame.mixer.music.play(loops=0)

def stop():
    pygame.mixer.music.stop()
    music_list.selection_clear(ACTIVE)

def pause(is_paused):
    global paused
    paused = is_paused

    if paused:
        pygame.mixer.music.unpause()
        paused = False
    else:
        pygame.mixer.music.pause()
        paused = True



# Playlist screen
music_list = Listbox(root, bg='black',fg='gold', width=100, selectbackground="gray", selectforeground="black")
music_list.pack(pady=20)

# Buttons
controls_house = Frame(root)
controls_house.pack()


# back_image = PhotoImage(file="C:\\Users\Mikha\\Downloads\\1x\\pause.png")
# forward_image = PhotoImage(file="C:\\Users\Mikha\\Downloads\\1x\\pause.png")
play_image = PhotoImage(file="assets/play.png")
pause_image = PhotoImage(file="assets/pause.png")
stop_image = PhotoImage(file="assets/stop.png")


# back_button = Button(controls_house, image=back_image,borderwidth=0)
# forward_button = Button(controls_house, image=forward_image,borderwidth=0)
play_button = Button(controls_house, image=play_image,borderwidth=0, command=play)
pause_button = Button(controls_house, image=pause_image,borderwidth=0, command =lambda: pause(paused))
stop_button = Button(controls_house, image=stop_image,borderwidth=0, command=stop)

# back_button.grid(row=0, column=0, padx=10)
# forward_button.grid(row=0, column=1, padx=10)
play_button.grid(row=0, column=1, padx=10)
pause_button.grid(row=0, column=2, padx=10)
stop_button.grid(row=0, column=3, padx=10)

# Create Menu
my_menu = Menu(root)
root.config(menu=my_menu)

# add song mnenu
add_song_menu = Menu(my_menu)
my_menu.add_cascade(label="Add Songs", menu=add_song_menu)
add_song_menu.add_command(label="Add one song to playlist", command=load_music)

# add many songs
add_song_menu.add_command(label="Add many songs to playlist", command=load_lots_of_music)


root.mainloop()