from deprecated_utils import *

event_map = {event['id']: event['name'] for event in data['events']}
with open('temp.json', 'r', encoding='utf-8') as f:
    temp = json.load(f)
temp_data = {}
for k, v in temp.items():
    if v not in temp_data:
        temp_data[v] = []
    temp_data[v].append(event_map.get(k, k))

for category, events in temp_data.items():
    print(f"\n{category}:")
    for event in sorted(events):
        print(f"[[{event}]]、", end="")
