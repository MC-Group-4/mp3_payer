from functions import *
from tkinter import *
import pygame


root = Tk()
root.title("Mission College Group 4 Mp3 Player")
#root.iconbitmap()
root.geometry("500x300")

# Init Mixer
pygame.mixer.init()


# Playlist screen
music_list = Listbox(root, bg='black',fg='gold', width=100)
music_list.pack(pady=20)

# Buttons
controls_house = Frame(root)
controls_house.pack()


# back_image = PhotoImage(file="C:\\Users\Mikha\\Downloads\\1x\\pause.png")
# forward_image = PhotoImage(file="C:\\Users\Mikha\\Downloads\\1x\\pause.png")
play_image = PhotoImage(file="C:\\Users\Mikha\\Downloads\\1x\\play.png")
pause_image = PhotoImage(file="C:\\Users\Mikha\\Downloads\\1x\\pause.png")
stop_image = PhotoImage(file="C:\\Users\Mikha\\Downloads\\1x\\stop.png")


# back_button = Button(controls_house, image=back_image,borderwidth=0)
# forward_button = Button(controls_house, image=forward_image,borderwidth=0)
play_button = Button(controls_house, image=play_image,borderwidth=0)
pause_button = Button(controls_house, image=pause_image,borderwidth=0)
stop_button = Button(controls_house, image=stop_image,borderwidth=0)

# back_button.grid(row=0, column=0, padx=10)
# forward_button.grid(row=0, column=1, padx=10)
play_button.grid(row=0, column=1, padx=10)
pause_button.grid(row=0, column=2, padx=10)
stop_button.grid(row=0, column=3, padx=10)


root.mainloop()