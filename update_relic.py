from utils import *

print(f"共找到 {len(data['relics'])} 个遗物数据，正在处理...")

pool_mapping = {
    "ironclad": "铁甲战士",
    "silent": "静默猎手",
    "defect": "故障机器人",
    "necrobinder": "亡灵契约师",
    "regent": "储君",
    "colorless": "无色",
}
tier_mapping = {
    "Starter": "初始",
    "Common": "普通",
    "Uncommon": "罕见",
    "Rare": "稀有",
    "Event": "事件",
    "Ancient": "先古之民",
    "Shop": "商店",
    "None": "无",
}
for relic in data['relics']:
    relic["category"] = "relic"
    relic["ver"] = ver
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
    if relic.get("description"):
        relic["description"] = clean_text(relic["description"])
    if relic.get("flavorText"):
        relic["flavorText"] = clean_text(relic["flavorText"])

field_order = [
    "category",
    "ver",
    "id",
    "name",
    "pool",
    "tier",
    "description",
    "flavorText",
    "image",
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