from deprecated_utils import *

print(f"共找到 {len(data['relics'])} 个遗物数据，正在处理...")

for relic in data['relics']:
    if relic.get("description"):
        relic["description"] = clean_text(relic["description"], relic.get("pool", ""))
    if relic.get("flavorText"):
        relic["flavorText"] = clean_text(relic["flavorText"], relic.get("pool", ""))
    relic["category"] = "relic"
    relic["id"] = relic["id"].lower()
    relic["image"] = f'{relic["id"]}.png'
    if relic.get("pool"):
        if not pool_mapping.get(relic["pool"]):
            print(f"未找到pool中文名: {relic['pool']}")
        relic["pool"] = pool_mapping.get(relic["pool"], relic["pool"])
    if relic.get("tier"):
        if not tier_mapping.get(relic["tier"]):
            print(f"未找到tier中文名: {relic['tier']}")
        relic["tier"] = tier_mapping.get(relic["tier"], relic["tier"])
    relic["page"] = relic["name"]

field_order = [
    "category",
    "id",
    "name",
    "pool",
    "tier",
    "description",
    "flavorText",
    "image",
    "page",
]
result = [[relic.get(field) for field in field_order] for relic in data['relics']]

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