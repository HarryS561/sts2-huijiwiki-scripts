import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils import *

print(f"共找到 {len(data['cards'])} 张卡牌数据，正在处理...")

# cards_data_from_api = {card['id']: card for card in get_data_by_api('cards')}

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
        "id": card_id,
        "name": card.get("name", ""),
        "color": card.get("color", ""),
        "rarity": card.get("rarity", ""),
        "type": card.get("type", ""),
        "cost": str(card.get("cost", "")),
        "description": card.get("description", ""),
        # "compendium_order": str(cards_data_from_api.get(card_id.upper().replace("_UPGRADE", ""), {}).get('compendium_order', "")),
        "upgrade": upgraded == 1 and "已升级" or "不可升级_upgrade",
        "image": f'{card_id.lower()}.png',
    }
    if upgraded != 1:
        new_card["page"] = card.get("name", "")
    cards[card_id] = new_card
for card in has_upgrades:
    base_id = card
    upgrade_id = card + "_upgrade"
    if base_id in cards and upgrade_id in cards:
        cards[base_id]["upgrade"] = upgrade_id

for card in cards.values():
    if card.get("description"):
        card["description"] = clean_text(card["description"], card.get("color"))
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

# 从 mapping 的值构建排序顺序
color_order = list(color_mapping.values())
rarity_order = list(rarity_mapping.values())
type_order = list(type_mapping.values())
cost_order = list(cost_mapping.values())

def get_sort_key(card_id):
    """根据指定规则生成排序键"""
    card = cards.get(card_id.replace("_upgrade", ""))
    if not card:
        return (float('inf'), float('inf'), float('inf'), float('inf'), "")
    
    # color 排序
    color = card.get("color", "")
    try:
        color_key = color_order.index(color)
    except ValueError:
        color_key = len(color_order)
    
    # rarity 排序
    rarity = card.get("rarity", "")
    try:
        rarity_key = rarity_order.index(rarity)
    except ValueError:
        rarity_key = len(rarity_order)
    
    # type 排序
    type_ = card.get("type", "")
    try:
        type_key = type_order.index(type_)
    except ValueError:
        type_key = len(type_order)
    
    # cost 排序（X 视为 0）
    cost = card.get("cost", "")
    if cost == "零" or cost == "X":
        cost_key = 0
    else:
        try:
            cost_key = cost_order.index(cost)
        except ValueError:
            cost_key = len(cost_order)
    
    # 拼音排序
    name = card.get("name", "")
    pinyin = "".join(lazy_pinyin(name))
    
    return (color_key, rarity_key, type_key, cost_key, pinyin)

# 对卡牌进行排序
sorted_card_ids = sorted(cards.keys(), key=get_sort_key)

# 为每个卡牌分配 compendium_order
for idx, card_id in enumerate(sorted_card_ids):
    cards[card_id]["compendium_order"] = str(idx + 1)

# 转成二维数组，按字段顺序输出
field_order = [
    "category",
    "id",
    "name",
    "color",
    "rarity",
    "type",
    "cost",
    "description",
    "upgrade",
    "compendium_order",
    "image",
    "page",
]
result = [[cards[card_id].get(field) for field in field_order] for card_id in sorted_card_ids]

pagedata = json.dumps({
    "sources": f"导出数据自版本 {ver}",
    "schema": {
        "fields": process_fields(field_order),
    },
    "data": result,
}, ensure_ascii=False, indent=2)

# with open(f"cards_{ver}.json", "w", encoding="utf-8") as f:
#     f.write(pagedata)

old_data_parsed = parse_tabx("Data:Card.tabx", "id")
site.pages["Data:Card.tabx"].save(pagedata, summary=f"导出数据自版本 {ver}")
new_data_parsed = parse_tabx("Data:Card.tabx", "id")
diff = diff_tabx_records(old_data_parsed, new_data_parsed)
update_card_images(diff)