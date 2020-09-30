

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

    if entry[0] == 'END':
        total_time_listened += (float(entry[3]) - float(entry[4]))
        total_time_paused += (float(entry[4]))

print(total_time_listened)
print(total_time_paused)
