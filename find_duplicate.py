from utils import *
import json
from collections import defaultdict

# 用于存储 id 和 name 的字典
id_map = defaultdict(list)
name_map = defaultdict(list)

# 遍历所有顶级类别
for category, items in data.items():
    if isinstance(items, list):  # 确保是列表
        for item in items:
            item_id = item.get("id")
            item_name = item.get("name")
            if item_id:
                id_map[item_id].append((category, item))
            if item_name:
                name_map[item_name].append((category, item))

# 检查重复的 id
print("重复 ID：")
for item_id, occurrences in id_map.items():
    categories = {category for category, _ in occurrences}
    if len(occurrences) > 1 and (len(categories) > 1 or (len(categories) == 1 and list(categories)[0] != "cards")):  # 如果跨类别重复或非cards类别内有多个重复
        print(f"ID: {item_id}")
        for category, item in occurrences:
            print(f"  Found in {category}: {item}")
        print()

# 检查重复的 name
print("重复 Name：")
for item_name, occurrences in name_map.items():
    categories = {category for category, _ in occurrences}
    if len(occurrences) > 1 and (len(categories) > 1 or (len(categories) == 1 and list(categories)[0] != "cards")):  # 如果跨类别重复或非cards类别内有多个重复
        print(f"Name: {item_name}")
        for category, item in occurrences:
            print(f"  {category}: {item}")
        print()