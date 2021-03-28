'''Creating space for my functions to live that can easily be tested. You can also add your
functions to this file for one centralized location, totally up to you'''
from tkinter import *
import pygame
from tkinter import filedialog


def load_music():
    music = filedialog.askopenfilename(initialdir='music.db/', title="Choose a song", filetype=(("Mp3 Files", ".mp3",),))

def play_pause_music():
    pass

def stop_music():
    pass
