from utils import *

print(f"共找到 {len(data['events'])} 个事件数据，正在处理...")

def parse_event_options(options):
    """
    解析 options 数组，支持：
    1. 普通选项: title, effect
    2. 带锁定选项: 锁定, effect_locked, title, effect

    返回:
    {
        "option1_title": ...,
        "option1_effect": ...,
        "option2_effect_locked": ...,
        "option2_title": ...,
        "option2_effect": ...
    }
    """
    result = {}
    i = 0
    option_index = 1
    while i < len(options):
        if options[i] == "锁定": # 当前选项带锁定提示
            if i + 3 >= len(options):
                raise ValueError(f'非法数据：第 {option_index} 个选项的"锁定"结构不完整')
            result[f"option{option_index}_effect_locked"] = options[i + 1]
            result[f"option{option_index}_title"] = options[i + 2]
            result[f"option{option_index}_effect"] = options[i + 3]
            i += 4
            option_index += 1
        else: # 普通选项
            if i + 1 >= len(options):
                raise ValueError(f"非法数据：第 {option_index} 个选项缺少 effect")
            result[f"option{option_index}_title"] = options[i]
            result[f"option{option_index}_effect"] = options[i + 1]
            i += 2
            option_index += 1

    return result

parsed_options_keys = set()
for event in data['events']:
    event["category"] = "event"
    event["ver"] = ver
    event["id"] = event["id"].lower()
    event["image"] = f'{event["id"]}.png'
    if event['id'] == "lost_wisp":
        event["image"] = "lost_wisp_(event).png"
    if event.get("description"):
        event["description"] = clean_text(event["description"])
    parsed_options = parse_event_options(event.get("options", []))
    if event["id"] == "zen_weaver":
        parsed_options["option2_effect_locked"] = "金币不足。"
        parsed_options["option3_effect_locked"] = "金币不足。"
    event.update(parsed_options)
    parsed_options_keys.update(parsed_options.keys())

field_order = [
    "category",
    "ver",
    "id",
    "name",
    "description",
    "image",
]
field_order += sorted(parsed_options_keys)
result = [[event.get(field) for field in field_order] for event in data['events']]

pagedata = json.dumps({
    "sources": f"导出数据自版本 {ver}",
    "schema": {
        "fields": process_fields(field_order),
    },
    "data": result,
}, ensure_ascii=False, indent=2)

# with open(f"events_{ver}.json", "w", encoding="utf-8") as f:
#     f.write(pagedata)
site.pages["Data:Event.tabx"].save(pagedata, summary=f"导出数据自版本 {ver}")