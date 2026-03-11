from deprecated_utils import *

print(f"共找到 {len(data['potions'])} 个药水数据，正在处理...")

for potion in data['potions']:
    if potion.get("description"):
        potion["description"] = clean_text(potion["description"], potion.get("color"))
    potion["category"] = "potion"
    potion["id"] = potion["id"].lower()
    potion["image"] = f'{potion["id"]}.png'
    if potion.get("color"):
        if not color_mapping.get(potion["color"]):
            print(f"未找到color中文名: {potion['color']}")
        potion["color"] = color_mapping.get(potion["color"], potion["color"])
    if potion.get("tier"):
        if not tier_mapping.get(potion["tier"]):
            print(f"未找到tier中文名: {potion['tier']}")
        potion["tier"] = tier_mapping.get(potion["tier"], potion["tier"])
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
result = [[potion.get(field) for field in field_order] for potion in data['potions']]

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