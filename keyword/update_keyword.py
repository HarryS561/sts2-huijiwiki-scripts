import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils import *

# data = json.load(open(os.path.join(data_path, "keywords.json"), 'r', encoding='utf-8'))

data = get_data_by_api("keywords")

for keyword in data:
    keyword["category"] = "keyword"
    keyword["id"] = keyword["id"].lower()
    keyword["description"] = del_tags(keyword["description"])
field_order = [
    "category",
    "id",
    "name",
    "description",
]
result = [[keyword.get(field) for field in field_order] for keyword in data]
pagedata = json.dumps({
    "sources": f"导出数据自版本 {ver}",
    "schema": { "fields": process_fields(field_order) },
    "data": result,
}, ensure_ascii=False)
site.pages["Data:Keyword.tabx"].save(pagedata, summary=f"导出数据自版本 {ver}")