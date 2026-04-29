import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils import *

data = get_data_by_api("powers")
print(f"共找到 {len(data)} 个状态数据，正在处理...")

pagedata = json.loads(site.pages[f"Data:Power.tabx"].text())
fields = pagedata['schema']['fields']
for i, field in enumerate(fields):
    if field['name'] == 'id':
        id_idx = i
    elif field['name'] == 'origin':
        origin_idx = i
    elif field['name'] == 'note':
        note_idx = i
power_data = {}
for row in pagedata['data']:
    power_id = row[id_idx]
    power_data[power_id] = {
        'origin': row[origin_idx],
        'note': row[note_idx], 
    }

for power in data:
    if power.get("description"):
        power["description"] = clean_text(power["description"], power.get("color")).replace("this creature", "该怪物").replace("[Amount]", "X")
    power["category"] = "power"
    power["id"] = power["id"].lower()
    power["image"] = f'{power["id"]}_power.png'
    power["page"] = power["name"]
    power["allow_negative"] = str(power["allow_negative"])
    power['origin'] = power_data.get(power['id'], {}).get('origin', '')
    power['note'] = power_data.get(power['id'], {}).get('note', '')

field_order = [
    "category",
    "id",
    "name",
    "description",
    "type",
    "stack_type",
    "allow_negative",
    "origin",
    "note",
    "image",
    "page",
]
result = [[power.get(field) for field in field_order] for power in data]

pagedata = json.dumps({
    "sources": f"导出数据自版本 {ver}",
    "schema": {
        "fields": process_fields(field_order),
    },
    "data": result,
}, ensure_ascii=False, indent=2)

# with open(f"powers_{ver}.json", "w", encoding="utf-8") as f:
#     f.write(pagedata)
site.pages["Data:Power.tabx"].save(pagedata, summary=f"导出数据自版本 {ver}")