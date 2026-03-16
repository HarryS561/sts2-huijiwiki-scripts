import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils import *

pagedata = json.loads(site.pages[f"Data:Monster.tabx"].text())
fields = pagedata['schema']['fields']
for i, field in enumerate(fields):
    if field['name'] == 'name':
        name_idx = i
    elif field['name'] == 'stage':
        stage_idx = i
    elif field['name'] == 'tier':
        tier_idx = i
# 创建双重字典结构：stage -> tier -> 怪物名列表
monster_data = {}
for row in pagedata['data']:
    monster_name = row[name_idx]
    stage = row[stage_idx]
    tier = row[tier_idx]
    if stage not in monster_data:
        monster_data[stage] = {'普通': [], '精英': [], 'Boss': []}
    monster_data[stage][tier].append(f"[[{monster_name}]]")
navbox_child_stage = {}
for stage in monster_data:
    for tier in monster_data[stage]:
        monster_data[stage][tier] = sorted(monster_data[stage][tier], key=lambda x: lazy_pinyin(x))
        monster_data[stage][tier] = "、".join(monster_data[stage][tier])
    navbox_child_stage[stage] = f"""{{{{navbox|child
    |group1=普通
    |list1={monster_data[stage]['普通']}
    |group2=精英
    |list2={monster_data[stage]['精英']}
    |group3=Boss
    |list3={monster_data[stage]['Boss']}
    }}}}"""
    
res = f"""{{{{navbox
|title=事件
|listclass=hlist
|aboveclass=hlist
|groupstyle=
|group20=第一阶段
|list20={{{{navbox|child
  |group1=密林
  |list1={navbox_child_stage['密林']}
  |group2=暗港
  |list2={navbox_child_stage['暗港']}
  }}}}
|group30=第二阶段
|list30={{{{navbox|child
  |group1=巢穴
  |list1={navbox_child_stage['巢穴']}
  }}}}
|group50=第三阶段
|list50={{{{navbox|child
  |group1=荣耀
  |list1={navbox_child_stage['荣耀']}
  }}}}
|group70=待补充
|list70={navbox_child_stage['']}
}}}}
"""
with open("monster/navbox.txt", "w", encoding="utf-8") as f:
    f.write(res)