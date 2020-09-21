def getHandle():
    global spotify_handle
    spotify_handle = win32gui.FindWindow(None,'Spotify Premium')
    if spotify_handle != 0:
        t_playing = threading.Timer(0.1, printCurrent).start()
    else:
        t_handle = threading.Timer(0.1, getHandle).start()
