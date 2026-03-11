from mwclient import *
from mwparserfromhell import parse, nodes
import json
from tqdm import tqdm
import os
import shutil
import re

with open('config.json','r', encoding='utf-8') as f:
    config = json.load(f)

site = Site('sts2.huijiwiki.com', custom_headers={
            'X-authkey': config["huijiwiki"]["X-authkey"]})
site.login(
    username = config["huijiwiki"]["username"],
    password = config["huijiwiki"]["password"],
)

ver = '0.98.2'

data_path = "C:/Users/syw/Downloads/spire-codex/data"

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
tier_mapping = {
    "Starter": "初始",
    "Common": "普通",
    "Uncommon": "罕见",
    "Rare": "稀有",
    "Event": "事件",
    "Token": "衍生",
    "Ancient": "先古之民",
    "Shop": "商店",
    "None": "无",
}
pool_mapping = {
    "ironclad": "铁甲战士",
    "silent": "静默猎手",
    "defect": "故障机器人",
    "necrobinder": "亡灵契约师",
    "regent": "储君",
    "colorless": "无色",
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

def clean_text(text: str, color):
    if color and color != "" and color in color_mapping:
        text = text.replace("[E]", f"[[File:{color}_energy_icon.png|16px|link=]]")
    return text.replace("\n", "<br>").replace("[STAR]", "[[File:star_icon.png|16px|link=]]")

def del_tags(text):
    return re.sub(r'\[/?[a-z]+(?::\d+)?\]', '', text)