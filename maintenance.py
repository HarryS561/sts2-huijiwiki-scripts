from utils import *

def touch_all():
    for item in tqdm(list(site.search('创建缩略图出错'))):
        site.pages[item['title']].touch()

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

def get_param(template, index, default=''):
    try:
        return str(template.get(index).value).strip()
    except ValueError:
        return default

def repl():
    replacements = {
        r'[[Category:杀戮尖塔2图片]][[Category:状态与能力图标]]': r'[[Category:状态图像]]',
    }
    for page in tqdm(get_pages(category='杀戮尖塔2图片')):
        text = page.text()
        newtext = text
        for old, new in replacements.items():
            newtext = newtext.replace(old, new)
        if newtext != text:
            page.save(newtext, summary='批量替换文本')

def add_category_for_images():
    pagedata = json.loads(site.pages[f"Data:Monster.tabx"].text())
    fields = pagedata['schema']['fields']
    for i, field in enumerate(fields):
        if field['name'] == 'image':
            image_idx = i
    event_images = []
    for row in pagedata['data']:
        event_images.append(row[image_idx])
    for event_image in tqdm(event_images):
        page = site.pages['File:' + event_image]
        if page.exists and '[[Category:怪物图像]]' not in page.text():
            page.save('[[Category:怪物图像]]', summary='添加分类')
        elif not page.exists:
            print(f"文件不存在: {event_image}")