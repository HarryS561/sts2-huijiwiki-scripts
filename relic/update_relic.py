import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils import *

data = get_data_by_api("relics")
print(f"共找到 {len(data)} 个遗物数据，正在处理...")

relic_to_ancient_name = {}
for item in get_data_by_api("events"):
    event_name = item.get("name", "UNKNOWN_EVENT")
    relics = item.get("relics")
    if not relics or not isinstance(relics, list):
        continue
    for r in relics:
        relic_to_ancient_name[r.lower()] = event_name

for relic in data:
    if relic.get("description"):
        relic["description_raw"] = clean_text(relic["description"], relic.get("pool"), False)
        relic["description"] = clean_text(relic["description"], relic.get("pool", ""))
    if relic.get("flavor"):
        relic["flavor"] = clean_text(relic["flavor"], relic.get("pool", ""))
    relic["category"] = "relic"
    relic["id"] = relic["id"].lower()
    relic["image"] = f'{relic["id"]}.png'
    if relic.get("pool"):
        if not pool_mapping.get(relic["pool"]):
            print(f"未找到pool中文名: {relic['pool']}")
        relic["pool"] = pool_mapping.get(relic["pool"], relic["pool"])
    if relic.get("rarity"):
        if not tier_mapping.get(relic["rarity"]):
            print(f"未找到tier中文名: {relic['rarity']}")
        relic["tier"] = tier_mapping.get(relic["rarity"], relic["rarity"])
    relic["ancient"] = relic_to_ancient_name.get(relic["id"], "")
    relic["page"] = relic["name"]

# 从 mapping 的值构建排序顺序
tier_order = list(tier_mapping.values())
pool_order = list(pool_mapping.values())
ancient_order = ["涅奥", "欧洛巴斯", "佩尔", "特兹卡塔拉", "诺奴佩普", "坦克斯", "瓦库", "达弗"]

def get_sort_key(relic):
    """根据指定规则生成排序键"""
    # tier 排序
    tier = relic.get("tier", "")
    try:
        tier_key = tier_order.index(tier)
    except ValueError:
        tier_key = len(tier_order)
    
    # pool 排序
    pool = relic.get("pool", "")
    try:
        pool_key = pool_order.index(pool)
    except ValueError:
        pool_key = len(pool_order)

    # ancient 排序
    ancient = relic.get("ancient", "")
    try:
        ancient_key = ancient_order.index(ancient)
    except ValueError:
        ancient_key = len(ancient_order)
    
    # unicode排序
    if relic["pool"] in ["通用", "事件"]:
        name = relic.get("name", "")
        collator_key = collator.getSortKey(name)
        # pinyin = " ".join(lazy_pinyin(name))
    # 角色专属的似乎在图鉴中是按id排的，怪
    else:
        collator_key = relic["id"]
    
    return (tier_key, pool_key, ancient_key, collator_key)

data = sorted(data, key=get_sort_key)

def starter(relic):
    if relic["tier"] == '初始':
        should = {
            "burning_blood": 0,
            "black_blood": 5,
            "ring_of_the_snake": 1,
            "ring_of_the_drake": 6,
            "divine_right": 2,
            "divine_destiny": 7,
            "bound_phylactery": 3,
            "phylactery_unbound": 8,
            "cracked_core": 4,
            "infused_core": 9,
        }
        return should.get(relic["id"], 99)
    else:
        return 999
data.sort(key=lambda relic: (starter(relic)))

for idx, relic in enumerate(data):
    relic["compendium_order"] = str(idx + 1)

for relic in data:
    if relic["id"] == "empty_cage":
        relic["description"] = "拾起时，选择移除{{颜色|gold|牌组}}中的{{颜色|blue|2}}张牌。"
    elif relic["id"] == "ninja_scroll":
        relic["description"] = "每场战斗开始时，将{{颜色|blue|3}}张{{颜色|gold|小刀}}加入你的{{颜色|gold|手牌}}。"

field_order = [
    "category",
    "id",
    "name",
    "pool",
    "tier",
    "description",
    "description_raw",
    "flavor",
    "ancient",
    "compendium_order",
    "image",
    "page",
]
result = [[relic.get(field) for field in field_order] for relic in data]

pagedata = json.dumps({
    "sources": f"导出数据自版本 {ver}",
    "schema": {
        "fields": process_fields(field_order),
    },
    "data": result,
}, ensure_ascii=False, indent=2)

# with open(f"relics_{ver}.json", "w", encoding="utf-8") as f:
#     f.write(pagedata)
site.pages["Data:Relic.tabx"].save(pagedata, summary=f"导出数据自版本 {ver}")