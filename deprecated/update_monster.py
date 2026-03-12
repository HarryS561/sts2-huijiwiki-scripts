from deprecated_utils import *

print(f"共找到 {len(data['creatures'])} 个生物数据，正在处理...")

creatures = [creature for creature in data['creatures'] if creature.get("type") != "Player"]

for creature in creatures[::-1]:
    creature["category"] = "creature"
    creature["id"] = creature["id"].lower()
    creature["image"] = f'{creature["id"]}.png'
    creature["minHP"] = str(creature["minHP"])
    creature["maxHP"] = str(creature["maxHP"])

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
result = [[creature.get(field) for field in field_order] for creature in creatures]

pagedata = json.dumps({
    "sources": f"导出数据自版本 {ver}",
    "schema": {
        "fields": process_fields(field_order),
    },
    "data": result,
}, ensure_ascii=False, indent=2)

# with open(f"creatures_{ver}.json", "w", encoding="utf-8") as f:
#     f.write(pagedata)
site.pages["Data:Monster.tabx"].save(pagedata, summary=f"导出数据自版本 {ver}")