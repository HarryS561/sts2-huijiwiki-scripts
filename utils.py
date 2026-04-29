from mwclient import *
from mwparserfromhell import parse, nodes
import json
from tqdm import tqdm
import os
import shutil
import re
from pypinyin import lazy_pinyin
import requests
import hashlib
import tempfile
import subprocess
from pathlib import Path
from tag_parser import parse_tag
from icu import Collator, Locale
collator = Collator.createInstance(Locale("zh@collation=pinyin"))

with open('config.json','r', encoding='utf-8') as f:
    config = json.load(f)

site = Site('sts2.huijiwiki.com', custom_headers={
            'X-authkey': config["huijiwiki"]["X-authkey"]})
site.login(
    username = config["huijiwiki"]["username"],
    password = config["huijiwiki"]["password"],
)

ver = '0.99.1'

with open('C:/Program Files (x86)/Steam/steamapps/common/Slay the Spire 2/export/items.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

color_mapping = {
    "ironclad": "铁甲战士",
    "silent": "静默猎手",
    "regent": "储君",
    "necrobinder": "亡灵契约师",
    "defect": "故障机器人",
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
    "7": "七",
    "8": "八",
    "9": "九",
    "X": "X",
}
tier_mapping = {
    "Starter": "初始",
    "初始遗物": "初始",
    "Common": "普通",
    "普通遗物": "普通",
    "Uncommon": "罕见",
    "罕见遗物": "罕见",
    "Rare": "稀有",
    "稀有遗物": "稀有",
    "Shop": "商店",
    "商店遗物": "商店",
    "Ancient": "先古之民",
    "先古遗物": "先古之民",
    "Event": "事件",
    "事件遗物": "事件",
    "Token": "衍生",
    "None": "无",
}
pool_mapping = {
    "colorless": "通用",
    "shared": "通用",
    "ironclad": "铁甲战士",
    "silent": "静默猎手",
    "regent": "储君",
    "necrobinder": "亡灵契约师",
    "defect": "故障机器人",
    "event": "事件",
}

def process_fields(indices: list):
    fields = []
    for idx in indices:
        fields.append({
            "name": idx,
            "type": "string",
            "title": {
                "en": idx,
                "zh": ""
            }
        })
    return fields

energy_mapping = {
    "ironclad": "ironclad",
    "silent": "silent",
    "defect": "defect",
    "necrobinder": "necrobinder",
    "regent": "regent",
    "colorless": "colorless",
    "event": "colorless",
    "status": "colorless",
    "curse": "colorless",
    "quest": "colorless",
    "token": "colorless",
}
def clean_text(text: str, color: str = "colorless", parsetag: bool = True):
    text = text.replace("\n", "<br>")
    if parsetag:
        text = parse_tag(text, color)
        if color and color != "" and color in energy_mapping:
            text = text.replace("[E]", f"[[File:{energy_mapping[color]}_energy_icon.png|16px|link=能量]]")
        text = text.replace("[STAR]", "[[File:star_icon.png|16px|link=辉星]]")
    else:
        text = text.replace("[E]", "能量").replace("[STAR]", "辉星")
        f = lambda s: re.sub(r'\[(energy|star):(\d+)\]',
                     lambda m: {'energy':'能量','star':'辉星'}[m[1]] * int(m[2]),
                     s)
        text = del_tags(f(text))
        text = text.replace("<br>", "")
    return text

def del_tags(text):
    return re.sub(r'\[/?[a-z]+(?::\d+)?\]', '', text)

def get_data_by_api(route):
    response = requests.get(f"https://spire-codex.com/api/{route}?lang=zhs")
    response.raise_for_status()
    return response.json()

def parse_tabx(page, key_field, value_fields=None):
    """
    通用 tabx 解析函数

    :param page: tabx的完整页面名（如 "Data:Monster.tabx"）
    :param key_field: 用作字典 key 的字段名（如 'id'）
    :param value_fields: 需要提取的字段列表（如 ['power', 'stage']）
                         如果为 None，则提取所有字段
    :return: dict
    """
    pagedata = json.loads(site.pages[page].text())
    fields = pagedata['schema']['fields']
    # 建立字段名 -> 索引映射
    field_index = {field['name']: i for i, field in enumerate(fields)}
    # 校验 key 是否存在
    if key_field not in field_index:
        raise ValueError(f"字段 {key_field} 不存在")
    # 如果没指定 value_fields，则默认取全部字段
    if value_fields is None:
        value_fields = list(field_index.keys())
    result = {}
    for row in pagedata['data']:
        key = row[field_index[key_field]]

        result[key] = {
            field: row[field_index[field]]
            for field in value_fields
            if field in field_index
        }
    return result

def diff_tabx_records(old_data, new_data):
    """
    比较两个 tabx 解析后的字典，返回所有有差异的 key（排序后）
    """
    diff_keys = []
    all_keys = set(old_data.keys()) | set(new_data.keys())
    for key in all_keys:
        if key not in old_data or key not in new_data:
            diff_keys.append(key)
        elif old_data[key] != new_data[key]:
            diff_keys.append(key)
    return sorted(diff_keys)

def update_card_images(ids: list[str]):
    base_path = 'C:/Program Files (x86)/Steam/steamapps/common/Slay the Spire 2/export/slay-the-spire-2'
    ids = [id.upper() for id in ids]
    print(ids)
    card_images = os.path.join(base_path, 'card-images')
    for filename in os.listdir(card_images):
        if filename.endswith('.png') and filename.replace('Plus1', '_UPGRADE').replace('.png', '') in ids:
            new_name = filename.lower().replace('plus1', '_upgrade')
            # if not ("文件:" + new_name.capitalize().replace('_', ' ')) in exist:
            if not False:
                print(f"正在上传 {filename} -> {new_name}")
                for attempt in range(1, 5):
                    try:
                        site.upload(os.path.join(card_images, filename), new_name, '[[分类:卡牌图像]]', True)
                        break
                    except APIError as e:
                        if e.code == "fileexists-no-change":
                            # 远端已经是完全相同的版本，不算真正失败
                            print(f"文件 {filename} 内容没变化，跳过上传")
                            break
                        elif e.code == "empty-file":
                            continue
                        else:
                            raise