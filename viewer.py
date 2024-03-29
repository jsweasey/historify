from blessed import Terminal
import threading as threading
import datetime as datetime
import time as time
import math as math
import psutil as psutil

#TO ADD:
#setting to removes entries under a certain length (e.g <5 secs)
total_time_listened, total_time_paused = 0, 0
term = Terminal()

def initData(fileloc:str):
    global total_time_paused, total_time_listened, song_data_dict, artist_data_dict, daily_stats_data_dict

    with open(fileloc, 'r', encoding='utf_8') as x:
        data = x.read().splitlines()

    clean_data = []
    for line in data:
        clean_data.append(line.split("  "))

    song_data_dict = {}

    for i,entry in enumerate(clean_data):
        if entry[2] not in list(song_data_dict.keys()):
            name = entry[2].split(' - ')
            if len(name) == 2:
                song_data_dict.update({entry[2]:{'key':entry[2],'song':name[1],'artist':name[0],'remix':False,'length':0,'total_listened':0.0,
                                             'total_paused':0.0,'repeats':0,'recent_play':''}})
            elif len(name) > 2:
                song_data_dict.update({entry[2]:{'key':entry[2],'song':name[1],'artist':name[0],'remix':True,'remix_info':name[2],
                                                'length':0,'total_listened':0.0,'total_paused':0.0,'repeats':0,'recent_play':''}})


        if entry[0] == 'START':

            if (i > 0) and clean_data[i-1][0] != 'END': #Removes entries which have no defined END
                if song_data_dict[clean_data[i-1][2]]['repeats'] < 2:
                    song_data_dict.pop(clean_data[i-1][2])
                else:
                    song_data_dict[clean_data[i-1][2]]['repeats'] -= 1

            song_data_dict[entry[2]]['repeats'] += 1
            song_data_dict[entry[2]]['recent_play'] = entry[1]
        if entry[0] == 'END':
            time_listened = (float(entry[3]) - float(entry[4]))
            time_paused = (float(entry[4]))
            song_data_dict[entry[2]]['total_listened'] += time_listened
            song_data_dict[entry[2]]['total_paused'] += time_paused
            total_time_listened += time_listened
            total_time_paused += time_paused


    artist_data_dict = {}

    for song in list(song_data_dict.keys()):
        artist = song_data_dict[song]['artist']
        if song_data_dict[song]['artist'] in list(artist_data_dict.keys()):
            if song_data_dict[song]['remix']:
                artist_data_dict[artist]['songs'].append([song_data_dict[song]['key'],song_data_dict[song]['song'],song_data_dict[song]['remix'],song_data_dict[song]['remix_info']])
            else:
                artist_data_dict[artist]['songs'].append([song_data_dict[song]['key'],song_data_dict[song]['song'],song_data_dict[song]['remix']])
            artist_data_dict[artist]['total_listened'] += song_data_dict[song]['total_listened']
            artist_data_dict[artist]['total_paused'] += song_data_dict[song]['total_paused']
            artist_data_dict[artist]['repeats'] += song_data_dict[song]['repeats']
            checktime_c = datetime.datetime.strptime(song_data_dict[song]['recent_play'], '%Y-%m-%d %H:%M:%S.%f')
            checktime_p = datetime.datetime.strptime(artist_data_dict[artist]['recent_play'][0], '%Y-%m-%d %H:%M:%S.%f')
            if checktime_c > checktime_p:
                artist_data_dict[artist]['recent_play'] = (song_data_dict[song]['recent_play'],song_data_dict[song]['song'])
        else:
            if song_data_dict[song]['remix']:
                artist_data_dict.update({song_data_dict[song]['artist']:{'name':song_data_dict[song]['artist'],'songs':[[song_data_dict[song]['key'],song_data_dict[song]['song'],song_data_dict[song]['remix'],song_data_dict[song]['remix_info']]],'total_listened':song_data_dict[song]['total_listened'],
                                                                   'total_paused':song_data_dict[song]['total_paused'],'repeats':song_data_dict[song]['repeats'],
                                                                   'recent_play':(song_data_dict[song]['recent_play'],song_data_dict[song]['song'])}})
            else:
                artist_data_dict.update({song_data_dict[song]['artist']:{'name':song_data_dict[song]['artist'],'songs':[[song_data_dict[song]['key'],song_data_dict[song]['song'],song_data_dict[song]['remix']]],'total_listened':song_data_dict[song]['total_listened'],
                                                                   'total_paused':song_data_dict[song]['total_paused'],'repeats':song_data_dict[song]['repeats'],
                                                                   'recent_play':(song_data_dict[song]['recent_play'],song_data_dict[song]['song'])}})

    #Daily stats, weekly stats, montly stats, yearly, specific days, daily timeline
    daily_stats_data_dict = {} #Entry will be a day's stats

    working_date = datetime.datetime.strptime(clean_data[0][1], '%Y-%m-%d %H:%M:%S.%f').date()

    temp_song_dict,temp_artist_dict = {},{}
    daily_t_t_l, daily_t_s_l, daily_t_a_l, daily_n_s_l = 0,0,0,0
    daily_m_l_s,daily_m_l_a = '',''
    daily_n_s_l_list = []

    for entry in clean_data:

        if datetime.datetime.strptime(clean_data[0][1], '%Y-%m-%d %H:%M:%S.%f').date() > working_date:
            daily_stats_data_dict.update({working_date:{'total_time_listened':daily_t_t_l,'total_songs_listened':daily_t_s_l,'total_artists_listened':daily_t_a_l,'most_listened_song':daily_m_l_s,
                                                  'most_listened_artist':daily_m_l_a,'total_new_songs_listened':daily_n_s_l,'new_songs_listened':daily_n_s_l_list,}})
            temp_song_dict,temp_artist_dict = {},{}
            daily_t_t_l, daily_t_s_l, daily_t_a_l, daily_n_s_l = 0,0,0,0
            daily_m_l_s,daily_m_l_a = '',''
            daily_n_s_l_list = []
            working_date = datetime.datetime.strptime(clean_data[0][1], '%Y-%m-%d %H:%M:%S.%f').date()

        if entry[0] == 'START':
            daily_t_s_l += 1
            if entry[2] not in list(temp_song_dict.keys()):
                daily_n_s_l += 1
                temp_song_dict.update({entry[2]:{'total_time_listened':0,'total_listens':1,'artist':entry[2].split(' - ')[0],}})
                daily_n_s_l_list.append(entry[2])
            else:
                temp_song_dict[entry[2]]['total_listens'] += 1
            if entry[2].split(' - ')[0] not in list(temp_artist_dict.keys()):
                daily_t_a_l += 1
                temp_artist_dict.update({entry[2].split(' - ')[0]:{'total_listens':1,'songs_listened':[entry[2]],'total_time_listened':0,}})
            else:
                temp_artist_dict[entry[2].split(' - ')[0]]['total_listens'] += 1
                if entry[2] not in temp_artist_dict[entry[2].split(' - ')[0]]['songs_listened']:
                    temp_artist_dict[entry[2].split(' - ')[0]]['songs_listened'].append(entry[2])

        elif entry[0] == 'PAUSE':
            pass
        elif entry [0] == 'RESUMED':
            pass
        elif entry[0] == 'END':
            daily_t_t_l += float(entry[3])
            temp_song_dict[entry[2]]['total_time_listened'] += float(entry[3])
            if daily_m_l_s == '' or temp_song_dict[entry[2]]['total_time_listened'] > temp_song_dict[daily_m_l_s]['total_time_listened']:
                daily_m_l_s = entry[2]
            temp_artist_dict[entry[2].split(' - ')[0]]['total_time_listened'] += float(entry[3])
            if daily_m_l_a == '' or temp_artist_dict[entry[2].split(' - ')[0]]['total_time_listened'] > temp_artist_dict[daily_m_l_a]['total_time_listened']:
                daily_m_l_a = entry[2].split(' - ')[0]

    if daily_t_s_l > 0 or daily_t_t_l > 0:
        daily_stats_data_dict.update({working_date:{'total_time_listened':daily_t_t_l,'total_songs_listened':daily_t_s_l,'total_artists_listened':daily_t_a_l,'most_listened_song':daily_m_l_s,
                                              'most_listened_artist':daily_m_l_a,'total_new_songs_listened':daily_n_s_l,'new_songs_listened':daily_n_s_l_list,}})
        temp_song_dict,temp_artist_dict = {},{}
        daily_t_t_l, daily_t_s_l, daily_t_a_l, daily_n_s_l = 0,0,0,0
        daily_m_l_s,daily_m_l_a = '',''
        daily_n_s_l_list = []




def terminalStats():

    print(daily_stats_data_dict)


def terminalSongs():

    def terminalSongs_Info(song:str):
        song_info = song_data_dict[song]
        if song_info['remix']:
            stats = {'Song':song_info['song'],'Artist':song_info['artist'],'Remix':song_info['remix_info'],'Length':song_info['length'],
                    'Listened for':int(song_info['total_listened']//1),'Times played':song_info['repeats'],
                    'Time paused for':int(song_info['total_paused']//1),'Last time played':song_info['recent_play']}
        else:
            stats = {'Song':song_info['song'],'Artist':song_info['artist'],'Length':song_info['length'],
                    'Listened for':int(song_info['total_listened']//1),'Times played':song_info['repeats'],
                    'Time paused for':int(song_info['total_paused']//1),'Last time played':song_info['recent_play']}

        print(term.move_xy(0,9) + term.clear_eos)
        print(term.move_xy(0,10) + term.center(term.black_on_darkgreen(song)) + term.move_xy(2,10))
        for index,item in enumerate(list(stats.keys())):
            print(term.move_xy(2,11+index) + item + ': ')
            if item == 'Length' or item == 'Listened for' or item == 'Time paused for':
                print(term.move_xy(20,11+index) + '%s seconds' %stats[item])
            else:
                print(term.move_xy(20,11+index) + str(stats[item]))
        while True:
            input = term.inkey()
            if input.name == 'KEY_BACKSPACE': break

    def terminalArtists_Info(artist:str):

        def update_Artist_Info():
            i_c = 0
            print(term.move_xy(0,9) + term.clear_eos)
            print(term.move_xy(0,10) + term.center(term.black_on_darkgreen(artist)))
            for index,item in enumerate(list(stats.keys())):
                if item == 'Songs':
                    print(term.move_xy(2,11+index+i_c) + item + ': ')
                    if len(stats[item]) < 8:
                        for i in range(len(stats[item])):
                            if stats[item][i][2]:
                                if i == song_sel:
                                    print(term.move_xy(20,11+index+i) + term.black_on_white('%s - %s, %s seconds listened') %(stats[item][i][1],stats[item][i][3],int(song_data_dict[stats[item][i][0]]['total_listened'])//1))
                                else:
                                    print(term.move_xy(20,11+index+i) + term.white_on_black('%s - %s, %s seconds listened') %(stats[item][i][1],stats[item][i][3],int(song_data_dict[stats[item][i][0]]['total_listened'])//1))
                            else:
                                if i == song_sel:
                                    print(term.move_xy(20,11+index+i) + term.black_on_white('%s, %s seconds listened') %(stats[item][i][1],int(song_data_dict[stats[item][i][0]]['total_listened'])//1))
                                else:
                                    print(term.move_xy(20,11+index+i) + term.white_on_black('%s, %s seconds listened') %(stats[item][i][1],int(song_data_dict[stats[item][i][0]]['total_listened'])//1))
                            i_c = i
                    else:
                        songs_to_disp = []
                        for i_song in range(song_sel-6,song_sel):
                            if i_song > -1:
                                songs_to_disp.append(stats[item][i_song])
                        songs_to_disp.append(stats[item][song_sel])
                        for i_song in range(song_sel+1,song_sel+(8-len(songs_to_disp))):
                            if i_song < len(stats[item])-1:
                                songs_to_disp.append(stats[item][i_song])
                        for i in range(len(songs_to_disp)):
                            if songs_to_disp[i][2]:
                                if i == song_sel:
                                    print(term.move_xy(20,11+index+i) + term.black_on_white('%s - %s, %s seconds listened') %(songs_to_disp[i][1],songs_to_disp[i][3],int(song_data_dict[songs_to_disp[i][0]]['total_listened'])//1))
                                elif i == len(songs_to_disp)-1 and song_sel > i:
                                    print(term.move_xy(20,11+index+i) + term.black_on_white('%s, %s seconds listened') %(songs_to_disp[i][1],int(song_data_dict[songs_to_disp[i][0]]['total_listened'])//1))
                                else:
                                    print(term.move_xy(20,11+index+i) + term.white_on_black('%s - %s, %s seconds listened') %(songs_to_disp[i][1],songs_to_disp[i][3],int(song_data_dict[songs_to_disp[i][0]]['total_listened'])//1))
                            else:
                                if i == song_sel:
                                    print(term.move_xy(20,11+index+i) + term.black_on_white('%s, %s seconds listened') %(songs_to_disp[i][1],int(song_data_dict[songs_to_disp[i][0]]['total_listened'])//1))
                                elif i == len(songs_to_disp)-1 and song_sel > i:
                                    print(term.move_xy(20,11+index+i) + term.black_on_white('%s, %s seconds listened') %(songs_to_disp[i][1],int(song_data_dict[songs_to_disp[i][0]]['total_listened'])//1))
                                else:
                                    print(term.move_xy(20,11+index+i) + term.white_on_black('%s, %s seconds listened') %(songs_to_disp[i][1],int(song_data_dict[songs_to_disp[i][0]]['total_listened'])//1))
                            i_c = i

                else:
                    print(term.move_xy(2,11+index+i_c) + item + ': ')
                    if item == 'Listened for' or item == 'Time paused for':
                        print(term.move_xy(20,11+index+i_c) + '%s seconds' %stats[item])
                    else:
                        print(term.move_xy(20,11+index+i_c) + str(stats[item]))
        song_sel = 0
        artist_info = artist_data_dict[artist]
        stats = {'Artist':artist_info['name'],'Songs':artist_info['songs'],'Listened for':int(artist_info['total_listened']),
                 'Times played':artist_info['repeats'],'Time paused for':int(artist_info['total_paused']),'Last song played':artist_info['recent_play'][1],
                 'Last time played':artist_info['recent_play'][0]}

        update_Artist_Info()
        while True:
            input = term.inkey()
            if input.name == 'KEY_BACKSPACE':
                break
            elif input.name == 'KEY_UP':
                if song_sel > 0:
                    song_sel -= 1
                    update_Artist_Info()
            elif input.name == 'KEY_DOWN':
                if song_sel < len(stats['Songs'])-1:
                    song_sel += 1
                    update_Artist_Info()
            elif input.name == 'KEY_ENTER':
                terminalSongs_Info(stats['Songs'][song_sel][0])
                update_Artist_Info()

    def terminalSongs_Artist():

        def refreshLayout():
            print(term.move_xy(0,9) + term.clear_eos)
            if disp_sorted: disp_layout = sorted_layout
            else: disp_layout = layout
            x_show = []

            for x in range(columns):
                x_show.append((current_page*columns)+x)

            print(term.move_xy(2,term.height-2) + term.black_on_white('Page %s of %s') %(current_page+1,total_pages))

            for x_index,c in enumerate(x_show):
                if c < len(disp_layout):
                    for y_index,item in enumerate(disp_layout[c]):
                        if len(item['artist']) > 34:
                            to_print = item['artist'][:33] + '...'
                        else:
                            to_print = item['artist']
                        if x_index == sel_x and y_index == sel_y: print(term.move_xy(2+(column_width*x_index),9+y_index) + term.black_on_white(to_print))
                        else: print(term.move_xy(2+(column_width*x_index),9+y_index) + to_print)

        def updateLayout(dir:str):

            if dir == 'UP': n_sel_y,n_sel_x = sel_y+1,sel_x
            elif dir == 'DOWN': n_sel_y,n_sel_x = sel_y-1,sel_x
            elif dir == 'LEFT': n_sel_y,n_sel_x = sel_y,sel_x+1
            elif dir == 'RIGHT': n_sel_y,n_sel_x = sel_y,sel_x-1
            to_print_w = disp_layout[(current_page*columns)+n_sel_x][n_sel_y]['artist']
            to_print_b = disp_layout[(current_page*columns)+sel_x][sel_y]['artist']
            if len(disp_layout[n_sel_x][n_sel_y]['artist']) > (column_width-4): to_print_w = to_print_w[:33] + '...'
            if len(disp_layout[sel_x][sel_y]['artist']) > (column_width-4): to_print_b = to_print_b[:33] + '...'
            print(term.move_xy(2+(column_width*n_sel_x),9+(n_sel_y)) + term.white_on_black(to_print_w))
            print(term.move_xy(2+(column_width*sel_x),9+(sel_y)) + term.black_on_white(to_print_b))

        def sortArtists(sort_by:str,asc_or_desc:str):
            global sorted_layout

            def sortAlphabetical(e):
                return e['artist']

            def sortListenTime(e):
                return int(e['total_listened'])

            def sortMostRepeats(e):
                return e['repeats']

            def sortMostRecent(e):
                return e['recent_play']

            def sortMostSongs(e):
                return e['songs']

            sorted_layout,sorted_layout_u = [],[]
            for x,c in enumerate(layout):
                for y,item in enumerate(c):
                    sorted_layout_u.append(item)

            if sort_by == 'ALPHABETICAL':
                if asc_or_desc == 'ASC':
                    sorted_layout_u.sort(reverse=False,key=sortAlphabetical)
                elif asc_or_desc == 'DESC':
                    sorted_layout_u.sort(reverse=True,key=sortAlphabetical)
            elif sort_by == 'LISTEN_TIME':
                if asc_or_desc == 'ASC':
                    sorted_layout_u.sort(reverse=False,key=sortListenTime)
                elif asc_or_desc == 'DESC':
                    sorted_layout_u.sort(reverse=True,key=sortListenTime)
            elif sort_by == 'MOST_RECENT':
                if asc_or_desc == 'ASC':
                    sorted_layout_u.sort(reverse=False,key=sortMostRecent)
                elif asc_or_desc == 'DESC':
                    sorted_layout_u.sort(reverse=True,key=sortMostRecent)
            elif sort_by == 'MOST_SONGS':
                if asc_or_desc == 'ASC':
                    sorted_layout_u.sort(reverse=False,key=sortMostSongs)
                elif asc_or_desc == 'DESC':
                    sorted_layout_u.sort(reverse=True,key=sortMostSongs)
            elif sort_by == 'MOST_REPEATS':
                if asc_or_desc == 'ASC':
                    sorted_layout_u.sort(reverse=False,key=sortMostRepeats)
                elif asc_or_desc == 'DESC':
                    sorted_layout_u.sort(reverse=True,key=sortMostRepeats)

            x = 0
            temp_arr = []
            for index,item in enumerate(sorted_layout_u):
                if x == column_height-1:
                    sorted_layout.append(temp_arr)
                    temp_arr = []
                    x = 0
                temp_arr.append(item)
                x += 1
            if len(temp_arr) > 0: sorted_layout.append(temp_arr)

        def checkSort():
            s_sel = 0
            sort_options=[('ALPHABETICAL ↑','ALPHABETICAL','ASC'),('ALPHABETICAL ↓','ALPHABETICAL','DESC'),
                          ('LISTEN TIME ↑','LISTEN_TIME','ASC'),('LISTEN TIME ↓','LISTEN_TIME','DESC'),
                          ('MOST RECENT ↑','MOST_RECENT','ASC'),('MOST RECENT ↓','MOST_RECENT','DESC'),
                          ('MOST SONGS ↑','MOST_SONGS','ASC'),('MOST SONGS ↓','MOST_SONGS','DESC'),
                          ('MOST REPEATS ↑','MOST_REPEATS','ASC'),('MOST REPEATS ↓','MOST_SONGS','DESC'),
                          ('ORIGINAL','ORIGINAL','ORIGINAL')]
            print(term.move_xy(0,9) + term.clear_eos)
            while True:
                for i,option in enumerate(sort_options):
                    if i == s_sel: print(term.move_xy(2,10+i) + term.black_on_white(option[0]))
                    else: print(term.move_xy(2,10+i) + term.white_on_black(option[0]))

                input = term.inkey()
                if input.name == 'KEY_UP':
                    if s_sel > 0:
                        s_sel -= 1
                if input.name == 'KEY_DOWN':
                    if s_sel < len(sort_options)-1:
                        s_sel += 1
                if input.name == 'KEY_ENTER':
                    if s_sel == len(sort_options)-1:
                        to_disp = False
                    else:
                        sortArtists(sort_options[s_sel][1],sort_options[s_sel][2])
                        to_disp = True
                    break
                if input.name == 'KEY_BACKSPACE':
                    to_disp = disp_sorted
                    break
            return to_disp


        column_height = term.height - 11
        column_width = 38
        columns = (term.width-2) // column_width
        layout = []
        disp_sorted = False
        temp_arr = []
        sel_x,sel_y = 0,0
        current_page = 0

        x = 0
        for index,item in enumerate(list(artist_data_dict.keys())):
            if x == column_height-1:
                layout.append(temp_arr)
                temp_arr = []
                x = 0
            temp_arr.append({'artist':item,'total_listened':artist_data_dict[item]['total_listened'],'repeats':artist_data_dict[item]['repeats'],'recent_play':artist_data_dict[item]['recent_play'][0],'songs':len(artist_data_dict[item]['songs'])})
            x += 1
        if len(temp_arr) > 0: layout.append(temp_arr)

        if disp_sorted: disp_layout = sorted_layout
        else: disp_layout = layout

        total_pages = math.ceil(len(disp_layout)/columns)
        print(term.move_xy(2,7)+ term.bold('Total Artists: %s, Columns: %s,%s ') %(len(artist_data_dict.keys()),columns,column_height) + term.black_on_white('PRESS "s" TO SORT') )
        refreshLayout()

        while True:
            if disp_sorted: disp_layout = sorted_layout
            else: disp_layout = layout
            input = term.inkey()
            if input.name == 'KEY_UP':
                if sel_y > 0:
                    sel_y -= 1
                    updateLayout('UP')
            elif input.name == 'KEY_DOWN':
                if sel_y < len(disp_layout[(current_page*columns)+sel_x])-1:
                    sel_y += 1
                    updateLayout('DOWN')
            elif input.name == 'KEY_LEFT':
                if sel_x > 0:
                    sel_x -= 1
                    updateLayout('LEFT')
                elif sel_x == 0 and current_page > 0:
                    current_page -= 1
                    sel_x = columns-1
                    refreshLayout()
            elif input.name == 'KEY_RIGHT':
                if sel_x < columns-1 and (current_page*columns)+sel_x+1 < len(disp_layout) and len(disp_layout[sel_x+1]) > sel_y: #and sel_y < len(disp_layout[sel_x+1])
                    sel_x += 1
                    updateLayout('RIGHT')
                elif sel_x == columns-1 and current_page+1 < total_pages:
                    current_page += 1
                    sel_x = 0
                    if len((disp_layout[(current_page*columns)+sel_x]))-1 < sel_y:
                        sel_y = len((disp_layout[(current_page*columns)+sel_x]))-1
                    refreshLayout()
            elif input == 's' or input == 'S':
                disp_sorted = checkSort()
                print(term.move_xy(0,9) + term.clear_eos)
                refreshLayout()
            elif input.name == 'KEY_ENTER':
                terminalArtists_Info(disp_layout[(sel_x+(current_page*columns))][sel_y]['artist'])
                print(term.move_xy(0,9) + term.clear_eos)
                refreshLayout()
            elif input.name == 'KEY_BACKSPACE':
                print(term.move_xy(0,7) + term.clear_eos)
                break

    def terminalSongs_Songs():

        def refreshLayout():
            print(term.move_xy(0,9) + term.clear_eos)
            if disp_sorted: disp_layout = sorted_layout
            else: disp_layout = layout

            x_show = []

            for x in range(columns):
                x_show.append((current_page*columns)+x)

            print(term.move_xy(2,term.height-2) + term.black_on_white('Page %s of %s') %(current_page+1,total_pages))

            for x_index,c in enumerate(x_show):
                if c < len(disp_layout):
                    for y_index,item in enumerate(disp_layout[c]):
                        if len(item['song']) > 34:
                            to_print = item['song'][:33] + '...'
                        else:
                            to_print = item['song']
                        if x_index == sel_x and y_index == sel_y: print(term.move_xy(2+(column_width*x_index),9+y_index) + term.black_on_white(to_print))
                        else: print(term.move_xy(2+(column_width*x_index),9+y_index) + to_print)

        def updateLayout(dir:str):
            if disp_sorted: disp_layout = sorted_layout
            else: disp_layout = layout

            if dir == 'UP': n_sel_y,n_sel_x = sel_y+1,sel_x
            elif dir == 'DOWN': n_sel_y,n_sel_x = sel_y-1,sel_x
            elif dir == 'LEFT': n_sel_y,n_sel_x = sel_y,sel_x+1
            elif dir == 'RIGHT': n_sel_y,n_sel_x = sel_y,sel_x-1
            to_print_w = disp_layout[(current_page*columns)+n_sel_x][n_sel_y]['song']
            to_print_b = disp_layout[(current_page*columns)+sel_x][sel_y]['song']
            if len(disp_layout[n_sel_x][n_sel_y]['song']) > (column_width-4): to_print_w = to_print_w[:33] + '...'
            if len(disp_layout[sel_x][sel_y]['song']) > (column_width-4): to_print_b = to_print_b[:33] + '...'
            print(term.move_xy(2+(column_width*n_sel_x),9+(n_sel_y)) + term.white_on_black(to_print_w))
            print(term.move_xy(2+(column_width*sel_x),9+(sel_y)) + term.black_on_white(to_print_b))

        def sortArtists(sort_by:str,asc_or_desc:str):
            global sorted_layout

            def sortAlphabetical(e):
                return e['song']

            def sortListenTime(e):
                return int(e['total_listened'])

            def sortMostRepeats(e):
                return e['repeats']

            def sortMostRecent(e):
                return e['recent_play']

            sorted_layout,sorted_layout_u = [],[]
            for x,c in enumerate(layout):
                for y,item in enumerate(c):
                    sorted_layout_u.append(item)

            if sort_by == 'ALPHABETICAL':
                if asc_or_desc == 'ASC':
                    sorted_layout_u.sort(reverse=False,key=sortAlphabetical)
                elif asc_or_desc == 'DESC':
                    sorted_layout_u.sort(reverse=True,key=sortAlphabetical)
            elif sort_by == 'LISTEN_TIME':
                if asc_or_desc == 'ASC':
                    sorted_layout_u.sort(reverse=False,key=sortListenTime)
                elif asc_or_desc == 'DESC':
                    sorted_layout_u.sort(reverse=True,key=sortListenTime)
            elif sort_by == 'MOST_RECENT':
                if asc_or_desc == 'ASC':
                    sorted_layout_u.sort(reverse=False,key=sortMostRecent)
                elif asc_or_desc == 'DESC':
                    sorted_layout_u.sort(reverse=True,key=sortMostRecent)
            elif sort_by == 'MOST_REPEATS':
                if asc_or_desc == 'ASC':
                    sorted_layout_u.sort(reverse=False,key=sortMostRepeats)
                elif asc_or_desc == 'DESC':
                    sorted_layout_u.sort(reverse=True,key=sortMostRepeats)

            x = 0
            temp_arr = []
            for index,item in enumerate(sorted_layout_u):
                if x == column_height-1:
                    sorted_layout.append(temp_arr)
                    temp_arr = []
                    x = 0
                temp_arr.append(item)
                x += 1
            if len(temp_arr) > 0: sorted_layout.append(temp_arr)

        def checkSort():
            s_sel = 0
            sort_options=[('ALPHABETICAL ↑','ALPHABETICAL','ASC'),('ALPHABETICAL ↓','ALPHABETICAL','DESC'),
                          ('LISTEN TIME ↑','LISTEN_TIME','ASC'),('LISTEN TIME ↓','LISTEN_TIME','DESC'),
                          ('MOST RECENT ↑','MOST_RECENT','ASC'),('MOST RECENT ↓','MOST_RECENT','DESC'),
                          ('MOST REPEATS ↑','MOST_REPEATS','ASC'),('MOST REPEATS ↓','MOST_SONGS','DESC'),
                          ('ORIGINAL','ORIGINAL','ORIGINAL')]
            print(term.move_xy(0,9) + term.clear_eos)
            while True:
                for i,option in enumerate(sort_options):
                    if i == s_sel: print(term.move_xy(2,10+i) + term.black_on_white(option[0]))
                    else: print(term.move_xy(2,10+i) + term.white_on_black(option[0]))

                input = term.inkey()
                if input.name == 'KEY_UP':
                    if s_sel > 0:
                        s_sel -= 1
                if input.name == 'KEY_DOWN':
                    if s_sel < len(sort_options)-1:
                        s_sel += 1
                if input.name == 'KEY_ENTER':
                    if s_sel == len(sort_options)-1:
                        to_disp = False
                    else:
                        sortArtists(sort_options[s_sel][1],sort_options[s_sel][2])
                        to_disp = True
                    break
                if input.name == 'KEY_BACKSPACE':
                    to_disp = disp_sorted
                    break
            return to_disp

        column_height = term.height - 11
        column_width = 38
        columns = (term.width-2) // column_width
        layout = []
        temp_arr = []
        disp_sorted = False
        sel_x,sel_y = 0,0
        current_page = 0

        x = 0
        for index,item in enumerate(list(song_data_dict.keys())):
            if x == column_height-1:
                layout.append(temp_arr)
                temp_arr = []
                x = 0
            if song_data_dict[item]['remix']:
                temp_arr.append({'key':item,'song':('%s - %s')%(song_data_dict[item]['song'],song_data_dict[item]['remix_info']),'remix':song_data_dict[item]['remix_info'],'artist':song_data_dict[item]['artist'],'total_listened':song_data_dict[item]['total_listened'],'repeats':song_data_dict[item]['repeats'],'recent_play':song_data_dict[item]['recent_play']})
            else:
                temp_arr.append({'key':item,'song':song_data_dict[item]['song'],'artist':song_data_dict[item]['artist'],'total_listened':song_data_dict[item]['total_listened'],'repeats':song_data_dict[item]['repeats'],'recent_play':song_data_dict[item]['recent_play']})
            x += 1
        if len(temp_arr) > 0: layout.append(temp_arr)

        if disp_sorted: disp_layout = sorted_layout
        else: disp_layout = layout

        total_pages = math.ceil(len(disp_layout)/columns)
        print(term.move_xy(2,7) + term.bold('Total Songs: %s, Columns: %s,%s ') %(len(song_data_dict.keys()),columns,column_height) + term.black_on_white('PRESS "s" TO SORT'))

        refreshLayout()

        while True:
            if disp_sorted: disp_layout = sorted_layout
            else: disp_layout = layout
            input = term.inkey()
            if input.name == 'KEY_UP':
                if sel_y > 0:
                    sel_y -= 1
                    updateLayout('UP')
            elif input.name == 'KEY_DOWN':
                if sel_y < len(disp_layout[(current_page*columns)+sel_x])-1:
                    sel_y += 1
                    updateLayout('DOWN')
            elif input.name == 'KEY_LEFT':
                if sel_x > 0:
                    sel_x -= 1
                    updateLayout('LEFT')
                elif sel_x == 0 and current_page > 0:
                    current_page -= 1
                    sel_x = columns-1
                    refreshLayout()
            elif input.name == 'KEY_RIGHT':
                if sel_x < columns-1 and (current_page*columns)+sel_x+1 < len(disp_layout) and len(disp_layout[sel_x+1]) > sel_y: #and sel_y < len(disp_layout[sel_x+1])
                    sel_x += 1
                    updateLayout('RIGHT')
                elif sel_x == columns-1 and current_page+1 < total_pages:
                    current_page += 1
                    sel_x = 0
                    if len((disp_layout[(current_page*columns)+sel_x]))-1 < sel_y:
                        sel_y = len((disp_layout[(current_page*columns)+sel_x]))-1
                    refreshLayout()
            elif input == 's' or input == 'S':
                disp_sorted = checkSort()
                print(term.move_xy(0,9) + term.clear_eos)
                refreshLayout()
            elif input.name == 'KEY_ENTER':
                terminalSongs_Info(disp_layout[(sel_x+(current_page*columns))][sel_y]['key'])
                print(term.move_xy(0,9) + term.clear_eos)
                refreshLayout()
            elif input.name == 'KEY_BACKSPACE':
                print(term.move_xy(0,7) + term.clear_eos)
                break


    songs_options = ['By Artist', 'All Songs']
    sel = 0

    while True:
        menu_x = 2
        for index,item in enumerate(songs_options):
            if index == sel: print(term.move_xy(menu_x,5) + term.black_on_white(item))
            else: print(term.move_xy(menu_x,5) + term.white_on_black(item))
            menu_x += 2+len(item)
        exit_phrase = 'BACKSPACE TO EXIT'
        print(term.move_xy((term.width-len(exit_phrase)-2),5) + term.black_on_white(exit_phrase))
        input = term.inkey()
        if input.name == 'KEY_LEFT':
            if sel > 0: sel -= 1
        elif input.name == 'KEY_RIGHT':
            if sel < len(songs_options)-1: sel += 1
        elif input.name == 'KEY_ENTER':
            if sel == 0:
                terminalSongs_Artist()
            if sel == 1:
                terminalSongs_Songs()
        elif input.name == 'KEY_BACKSPACE':
            print(term.move_xy(0,5) + term.clear_eos)
            break


def terminalOptions():
    pass

def terminalMenu():
    global term
    title = 'Spotify History/Stats'
    menu_list = ['Stats','Songs','Search','Options','Quit']
    menu_dict = {0:terminalStats,1:terminalSongs,2:terminalOptions}
    menu_x = 2
    sel = 0
    to_r = ''

    print(term.move_xy(0,0) + term.clear_eol + term.center(term.darkgreen('Spotify History/Stats/; by Jack Sweasey; DEVELOPMENT;')))
    with term.cbreak():
        while True:
            menu_x = 2
            for index,item in enumerate(menu_list):
                if sel == index:
                    print(term.move_xy(menu_x,2) + term.black_on_darkgreen(item))
                else:
                    print(term.move_xy(menu_x,2) + term.white_on_black(item))
                menu_x += 2+(len(item))
            print(term.move_xy(0,3))
            for x in range(term.width): print(term.move_xy(x,3) + term.darkgreen('_'))

            input = term.inkey()
            if input.name == 'KEY_LEFT':
                if sel > 0: sel -= 1
            elif input.name == 'KEY_RIGHT':
                if sel < len(menu_list)-1: sel += 1
            elif input.name == 'KEY_ENTER':
                if menu_list[sel] == 'Quit':
                    to_r = 'BREAK'
                    break
                else:
                    menu_dict[sel]()


    return to_r

def terminalInfo():
    pass

def terminalHistoryCheck():
    global term

    while True:
        if 'python.exe' in (proc.info['name'] for proc in psutil.process_iter(['name'])):
            print(term.move_xy(0,0) + term.darkgreen('HISTORY RUNNING'))
        else:
            print(term.move_xy(0,0) + term.darkgreen('HISTORY NOT RUNNING'))
        time.sleep(0.5)

def terminalMain():
    global term
    to_clear = True
    print(term.home + term.on_black + term.clear)
    while True:
        r = terminalMenu()
        if r == 'BREAK':
            break

def terminalRun():
    t_check = threading.Thread(target=terminalHistoryCheck,name='t_check')
    t_terminal = threading.Thread(target=terminalMain,name='t_terminal')
    t_check.start()
    t_terminal.start()

initData('history.txt')
terminalRun()
