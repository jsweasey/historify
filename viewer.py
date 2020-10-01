

with open('history.txt', 'r', encoding='utf_8') as x:
    data = x.read().splitlines()

clean_data = []
for line in data:
    clean_data.append(line.split("  "))

print(clean_data)

total_time_listened, total_time_paused = 0, 0
song_data_dict = {}

for entry in clean_data:
    if entry[2] not in list(song_data_dict.keys()):
        song_data_dict.update({entry[2]:[]})
    if entry[0] == 'START':

        if (i > 0) and clean_data[i-1][0] != 'END': #Removes entries which have no defined END
            if song_data_dict[clean_data[i-1][2]]['repeats'] < 2:
                song_data_dict.pop(clean_data[i-1][2])
            else:
                song_data_dict[clean_data[i-1][2]]['repeats'] -= 1

        song_data_dict[entry[2]]['repeats'] += 1
print(total_time_listened)
print(total_time_paused)
