from utils import *

print(f"共找到 {len(data['cards'])} 张卡牌数据，正在处理...")

cards = {}
has_upgrades = set()
for card in data['cards']:
    new_card = dict(card)
    card_id = card.get("id", "").lower()
    upgraded = card.get("upgrades", 0)
    if upgraded == 1:
        has_upgrades.add(card_id)
        card_id += "_upgrade"
    new_card = {
        "category": "card",
        "ver": ver,
        "id": card_id,
        "name": card.get("name", ""),
        "color": card.get("color", ""),
        "rarity": card.get("rarity", ""),
        "type": card.get("type", ""),
        "cost": str(card.get("cost", "")),
        "description": card.get("description", ""),
        "upgrade": upgraded == 1 and "upgraded" or "cannotupgrade",
        "image": f'{card_id.lower()}.png',
    }
    cards[card_id] = new_card
for card in has_upgrades:
    base_id = card
    upgrade_id = card + "_upgrade"
    if base_id in cards and upgrade_id in cards:
        cards[base_id]["upgrade"] = upgrade_id

color_mapping = {
    "ironclad": "铁甲战士",
    "silent": "静默猎手",
    "defect": "故障机器人",
    "necrobinder": "亡灵契约师",
    "regent": "储君",
    "colorless": "无色",
    "event": "事件",
    "status": "状态",
    "curse": "诅咒",
    "quest": "任务",
    "token": "衍生",
}
rarity_mapping = {
    "Basic": "初始", 
    "Common": "普通",
    "Uncommon": "罕见",
    "Rare": "稀有",
    "Event": "事件",
    "Ancient": "先古之民",
    "Status": "状态",
    "Curse": "诅咒",
    "Quest": "任务",
    "Token": "衍生",
}
type_mapping = {
    "Attack": "攻击",
    "Skill": "技能",
    "Power": "能力",
    "Status": "状态",
    "Curse": "诅咒",
    "Quest": "任务",
}
cost_mapping = {
    "0": "零",
    "1": "一",
    "2": "二",
    "3": "三",
    "4": "四",
    "5": "五",
    "6": "六",
    "X": "X",
}
for card in cards.values():
    if card.get("color"):
        if not color_mapping.get(card["color"]):
            print(f"未找到color中文名: {card['color']}")
        card["color"] = color_mapping.get(card["color"], card["color"])
    if card.get("rarity"):
        if not rarity_mapping.get(card["rarity"]):
            print(f"未找到rarity中文名: {card['rarity']}")
        card["rarity"] = rarity_mapping.get(card["rarity"], card["rarity"])
    if card.get("type"):
        if not type_mapping.get(card["type"]):
            print(f"未找到type中文名: {card['type']}")
        card["type"] = type_mapping.get(card["type"], card["type"])
    if card.get("cost"):
        if not cost_mapping.get(card["cost"]):
            print(f"未找到cost中文名: {card['cost']}")
        card["cost"] = cost_mapping.get(card["cost"], card["cost"])
    if card["cost"] == "":
        card["cost"] = "无"
    if card.get("description"):
        card["description"] = clean_text(card["description"])
# 转成二维数组，按字段顺序输出
field_order = [
    "category",
    "ver",
    "id",
    "name",
    "color",
    "rarity",
    "type",
    "cost",
    "description",
    "upgrade",
    "image",
]
result = [[card.get(field) for field in field_order] for card in cards.values()]

pagedata = json.dumps({
    "sources": f"导出数据自版本 {ver}",
    "schema": {
        "fields": process_fields(field_order),
    },
    "data": result,
}, ensure_ascii=False, indent=2)

# with open(f"cards_{ver}.json", "w", encoding="utf-8") as f:
#     f.write(pagedata)
site.pages["Data:Card.tabx"].save(pagedata, summary=f"导出数据自版本 {ver}")