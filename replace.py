from utils import *

replacements = [
    (r'card_link', r'卡牌'),
    (r'Card_link', r'卡牌'),
    (r'relic_link', r'遗物'),
    (r'Relic_link', r'遗物'),
    (r'potion_link', r'药水'),
    (r'Potion_link', r'药水'),
    (r'power_link', r'状态'),
    (r'Power_link', r'状态'),
]
category = None
template = None

def get_pages(template=None, category=None):
    if template and category:
        pages_using_template = {
            p.name for p in site.pages['Template:' + template].embeddedin()}
        res = list(p for p in site.categories[category] if p.name in pages_using_template)
        return res
    elif template:
        return list(site.pages['Template:' + template].embeddedin())
    elif category:
        return list(site.categories[category])
    return list(site.allpages())

if len(replacements) == 1:
    pages = [site.pages[item['title']] for item in site.search('_link')]
else:
    pages = get_pages(category=category, template=template)
for page in tqdm(pages):
    text = page.text()
    newtext = text
    for old, new in replacements:
        newtext = newtext.replace(old, new)
    if newtext != text:
        page.save(newtext, summary='批量替换文本')