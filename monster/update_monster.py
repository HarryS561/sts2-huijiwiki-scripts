import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils import *


pagedata = json.loads(site.pages[f"Data:Monster.tabx"].text())
fields = pagedata['schema']['fields']
for i, field in enumerate(fields):
    if field['name'] == 'id':
        id_idx = i
    elif field['name'] == 'tier':
        tier_idx = i
    elif field['name'] == 'power':
        power_idx = i
    elif field['name'] == 'stage':
        stage_idx = i
    elif field['name'] == 'note':
        note_idx = i
# 提取id和power、stage、note的对应关系
monster_data = {}
for row in pagedata['data']:
    monster_id = row[id_idx]
    monster_data[monster_id] = {
        'tier': row[tier_idx],
        'power': row[power_idx], 
        'stage': row[stage_idx],
        'note': row[note_idx]
    }

# data = json.load(open(os.path.join(data_path, "monsters.json"), 'r', encoding='utf-8'))

data = get_data_by_api("monsters")

for monster in data:
    monster["category"] = "monster"
    monster["id"] = monster["id"].lower()
    monster["image"] = f'{monster["id"]}.png'
    monster["minHP"] = str(monster["min_hp"])
    if monster['max_hp']:
        monster["maxHP"] = str(monster["max_hp"])
    else:
        monster["maxHP"] = monster["minHP"]
    if monster["min_hp_ascension"]:
        monster["ascenderminHP"] = str(monster["min_hp_ascension"])
    else:
        monster["ascenderminHP"] = monster["minHP"]
    if monster["max_hp_ascension"]:
        monster["ascendermaxHP"] = str(monster["max_hp_ascension"])
    else:
        monster["ascendermaxHP"] = monster["ascenderminHP"]
    monster['tier'] = monster_data.get(monster['id'], {}).get('tier', '')
    if not monster['tier']:
        monster['tier'] = ''
    monster['power'] = monster_data.get(monster['id'], {}).get('power', '')
    if not monster['power']:
        monster['power'] = ''
    monster['stage'] = monster_data.get(monster['id'], {}).get('stage', '')
    if not monster['stage']:
        monster['stage'] = ''
    monster['note'] = monster_data.get(monster['id'], {}).get('note', '')
    if monster['note'] == '' or not monster['note']:
        monster['note'] = '无'
    monster['page'] = monster['name']
    if monster['id'] == 'test_subject':
        monster['name'] = '实验体 #C8'
        monster['page'] = '实验体'
        monster['minHP'] = '100 / 200 / 300'
        monster['maxHP'] = monster['minHP']
        monster['ascenderminHP'] = '111 / 212 / 313'
        monster['ascendermaxHP'] = monster['ascenderminHP']

field_order = [
    "category",
    "id",
    "name",
    "image",
    "minHP",
    "maxHP",
    "ascenderminHP",
    "ascendermaxHP",
    "tier",
    "power",
    "stage",
    "note",
    "page",
]
result = [[monster.get(field) for field in field_order] for monster in data]
pagedata = json.dumps({
    "sources": f"导出数据自版本 {ver}",
    "schema": { "fields": process_fields(field_order) },
    "data": result,
}, ensure_ascii=False)
site.pages["Data:Monster.tabx"].save(pagedata, summary=f"导出数据自版本 {ver}")
