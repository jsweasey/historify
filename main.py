from win32 import win32gui
import threading as threading
from datetime import datetime

def enum_window_titles():
    def callback(handle, data):
        titles.append(win32gui.GetWindowText(handle))

    titles = []
    win32gui.EnumWindows(callback, None)
    return titles

titles = enum_window_titles()
def getHandle():
    global spotify_handle
    spotify_handle = win32gui.FindWindow(None,'Spotify Premium')
    if spotify_handle != 0:
        t_playing = threading.Timer(0.1, printCurrent).start()
    else:
        t_handle = threading.Timer(0.1, getHandle).start()
