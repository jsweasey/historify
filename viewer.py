

#TO ADD:
#setting to removes entries under a certain length (e.g <5 secs)
total_time_listened, total_time_paused = 0, 0
song_data_dict = {}

def initData(fileloc:str):
    global total_time_paused, total_time_listened, song_data_dict
    
    with open(fileloc, 'r', encoding='utf_8') as x:
        data = x.read().splitlines()

    clean_data = []
    for line in data:
        clean_data.append(line.split("  "))

    for i,entry in enumerate(clean_data):
        if entry[2] not in list(song_data_dict.keys()):
            name = entry[2].split(' - ')
            song_data_dict.update({entry[2]:{'song':name[1],'artist':name[0],'length':0,'total_listened':0.0,'total_paused':0.0,'repeats':0}})
        if entry[0] == 'START':

            if (i > 0) and clean_data[i-1][0] != 'END': #Removes entries which have no defined END
                if song_data_dict[clean_data[i-1][2]]['repeats'] < 2:
                    song_data_dict.pop(clean_data[i-1][2])
                else:
                    song_data_dict[clean_data[i-1][2]]['repeats'] -= 1

            song_data_dict[entry[2]]['repeats'] += 1
        if entry[0] == 'END':
            time_listened = (float(entry[3]) - float(entry[4]))
            time_paused = (float(entry[4]))
            song_data_dict[entry[2]]['total_listened'] += time_listened
            song_data_dict[entry[2]]['total_paused'] += time_paused
            total_time_listened += time_listened
            total_time_paused += time_paused

initData('history.txt')

print(song_data_dict)
print(total_time_listened)
print(total_time_paused)
