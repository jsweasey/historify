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

prev = ''
played = []
current_song = ''
history_file_loc = 'history.txt'

def getHandle():
    global spotify_handle
    spotify_handle = win32gui.FindWindow(None,'Spotify Premium')
    if spotify_handle != 0:
        t_playing = threading.Timer(0.1, printCurrent).start()
    else:
        t_handle = threading.Timer(0.1, getHandle).start()


def printCurrent():
    global prev
    global played
    global current_song

    t_playing = threading.Timer(0.1, printCurrent).start()
    current = win32gui.GetWindowText(spotify_handle)
    if current == 'Spotify Premium': current = 'Paused'
    if current != current_song and current != 'Paused':
        if current_song != '': played.append('%s END %s' %(datetime.now(),current_song))
        current_song = current
        played.append('%s START %s' %(datetime.now(),current_song))
    elif current == 'Paused':
        if prev != 'Paused' and current_song != '':
            played.append('%s PAUSED %s' %(datetime.now(),current_song))
    elif current == current_song and prev == 'Paused':
        played.append('%s RESUMED %s' %(datetime.now(),current_song))
    if prev != current and current != 'Paused':
        print('%s NEW SONG %s'%(datetime.now(),current))
    else:
        print('%s  %s'%(datetime.now(),current))
    prev = current
    with open(history_file_loc, 'a') as x:
        for item in played:
            x.write('%s\n'%item)
        played.clear()


t_handle = threading.Timer(0.1, getHandle)
t_handle.start()
