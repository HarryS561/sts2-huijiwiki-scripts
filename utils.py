from mwclient import *
from mwparserfromhell import parse
import json
from tqdm import tqdm
import os
import shutil

with open('config.json','r', encoding='utf-8') as f:
    config = json.load(f)

site = Site('sts2.huijiwiki.com', custom_headers={
            'X-authkey': config["huijiwiki"]["X-authkey"]})
site.login(
    username = config["huijiwiki"]["username"],
    password = config["huijiwiki"]["password"],
)

ver = '0.98.1'

with open('C:/Program Files (x86)/Steam/steamapps/common/Slay the Spire 2/export/items.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

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

def clean_text(text: str):
    return text.replace("\n", "<br>").replace("[E]", "能量")