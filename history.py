from win32 import win32gui
import threading as threading
from datetime import datetime
from blessed import Terminal

def enum_window_titles():
    def callback(handle, data):
        titles.append(win32gui.GetWindowText(handle))

    titles = []
    win32gui.EnumWindows(callback, None)
    return titles

titles = enum_window_titles()

prev = ''
played = []
current_song = (0,'',False,0) #(Start datetime, song info, if paused, total time paused(secs))
history_file_loc = 'history.txt'
last_10_songs = []
pause_at = ''
need_update = True

def init():
    term = Terminal()


def getHandle(init:bool):
    global spotify_handle
    global need_update

    spotify_handle = win32gui.FindWindow(None,'Spotify Premium')
    if spotify_handle != 0:
        if init:
            t_playing = threading.Timer(0.1, printCurrent).start()
            t_terminal = threading.Timer(0.1, terminalUpdate).start()
    else:
        if init:
            t_handle = threading.Timer(0.1, (lambda: getHandle(True))).start()
        if need_update:
            print(term.clear)
            print(term.move(13,0) + 'Is Spotify not open or currently playing? Make sure it is open and paused.')
            need_update = False


def printCurrent():
    global prev
    global played
    global current_song
    global last_10_songs
    global need_update
    global pause_at

    t_playing = threading.Timer(0.1, printCurrent).start()
    current = win32gui.GetWindowText(spotify_handle)
    if current == '':
        getHandle(False)
        if prev != '':
            length = datetime.now() - current_song[0]
            played.append('END  %s  %s  %s  %s' %(datetime.now(),current_song[1],(length).total_seconds(),current_song[3]))
            current_song = (0,'',False,0)
    else:
        if current == 'Spotify Premium':
            current = 'Paused'
            current_song = (current_song[0],current_song[1],True,current_song[3])
        if current != current_song[1] and current != 'Paused':
            if current_song[1] != '':
                length = datetime.now() - current_song[0]
                played.append('END  %s  %s  %s  %s' %(datetime.now(),current_song[1],(length).total_seconds(),current_song[3]))
                current_song = (0,'',False,0)
            if current != '':
                current_song = (datetime.now(), current, False, 0)
                last_10_songs.append(current_song[1])
                if len(last_10_songs) > 10:
                    last_10_songs.pop(0)
                if current != '':
                    played.append('START  %s  %s' %(current_song[0],current_song[1]))
                pause_at = ''
        elif current == 'Paused':
            if prev != 'Paused' and prev != '' and current_song[1] != '':
                current_song = (current_song[0],current_song[1],True,current_song[3])
                played.append('PAUSED  %s  %s' %(datetime.now(),current_song[1]))
                pause_at = datetime.now()
        elif current == current_song[1] and prev == 'Paused':
            pause_time = current_song[3]
            pause_time += (datetime.now() - pause_at).total_seconds()
            played.append('RESUMED  %s  %s  %s' %(datetime.now(),current_song[1],pause_time))
            current_song = (current_song[0],current_song[1], False, pause_time)
    with open(history_file_loc, 'a', encoding='utf_8') as x:
        for item in played:
            x.write('%s\n'%item)
        played.clear()
    if prev != current: need_update = True
    prev = current

def terminalUpdate():
    global current_song
    global last_10_songs
    global need_update

    t_terminal = threading.Timer(0.1, terminalUpdate).start()

    if need_update:
        print(term.clear)
        print(term.move(0,0) + 'Last 10 songs played:')
        for x in range(len(last_10_songs)):
            print(term.move(len(last_10_songs)-x,(1)) + ('%s. %s' %(len(last_10_songs)-x, last_10_songs[x])))
        if current_song[2] and current_song[1] != '':
            print(term.move_xy(0,12) + ('Currently playing: %s PAUSED' %current_song[1]))
        else:
            print(term.move_xy(0,12) + ('Currently playing: %s' %current_song[1]))

        need_update = False



term = Terminal()
getHandle(True)
