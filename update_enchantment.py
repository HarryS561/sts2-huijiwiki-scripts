from utils import *

print(f"共找到 {len(data['enchantments'])} 个附魔数据，正在处理...")

for enchantment in data['enchantments']:
    enchantment["category"] = "enchantment"
    enchantment["ver"] = ver
    enchantment["id"] = enchantment["id"].lower()
    enchantment["image"] = f'{enchantment["id"]}.png'

field_order = [
    "category",
    "ver",
    "id",
    "name",
    "description",
    "image",
]
result = [[enchantment.get(field) for field in field_order] for enchantment in data['enchantments']]

pagedata = json.dumps({
    "sources": f"导出数据自版本 {ver}",
    "schema": {
        "fields": process_fields(field_order),
    },
    "data": result,
}, ensure_ascii=False, indent=2)

# with open(f"enchantments_{ver}.json", "w", encoding="utf-8") as f:
#     f.write(pagedata)
site.pages["Data:Enchantment.tabx"].save(pagedata, summary=f"导出数据自版本 {ver}")

print(f"共找到 {len(data['afflictions'])} 个苦痛数据，正在处理...")

for affliction in data['afflictions']:
    affliction["category"] = "affliction"
    affliction["ver"] = ver
    affliction["id"] = affliction["id"].lower()
    affliction["image"] = f'{affliction["id"]}.png'

result = [[affliction.get(field) for field in field_order] for affliction in data['afflictions']]

pagedata = json.dumps({
    "sources": f"导出数据自版本 {ver}",
    "schema": {
        "fields": process_fields(field_order),
    },
    "data": result,
}, ensure_ascii=False, indent=2)

# with open(f"afflictions_{ver}.json", "w", encoding="utf-8") as f:
#     f.write(pagedata)
site.pages["Data:Affliction.tabx"].save(pagedata, summary=f"导出数据自版本 {ver}")