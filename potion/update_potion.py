import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils import *

data = get_data_by_api("potions")
print(f"共找到 {len(data)} 个药水数据，正在处理...")

for potion in data:
    if potion.get("description"):
        potion["description"] = clean_text(potion["description"], potion.get("color"))
    potion["category"] = "potion"
    potion["id"] = potion["id"].lower()
    potion["image"] = f'{potion["id"]}.png'
    if potion.get("pool"):
        if not pool_mapping.get(potion["pool"]):
            print(f"未找到pool中文名: {potion['pool']}")
        potion["color"] = pool_mapping.get(potion["pool"], potion["pool"])
    if potion.get("rarity"):
        # if not tier_mapping.get(potion["rarity"]):
        #     print(f"未找到tier中文名: {potion['rarity']}")
        potion["tier"] = tier_mapping.get(potion["rarity"], potion["rarity"])
    potion["page"] = potion["name"]

field_order = [
    "category",
    "ver",
    "id",
    "name",
    "color",
    "tier",
    "description",
    "image",
    "page",
]
result = [[potion.get(field) for field in field_order] for potion in data]

pagedata = json.dumps({
    "sources": f"导出数据自版本 {ver}",
    "schema": {
        "fields": process_fields(field_order),
    },
    "data": result,
}, ensure_ascii=False, indent=2)

# with open(f"potions_{ver}.json", "w", encoding="utf-8") as f:
#     f.write(pagedata)
site.pages["Data:Potion.tabx"].save(pagedata, summary=f"导出数据自版本 {ver}")