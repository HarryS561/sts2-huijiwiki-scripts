from utils import *

# replacements = [
#     (r'{{意图', r'{{行为树'),
#     (r'{{Intent_link', r'{{意图'),
#     (r'{{intent_link', r'{{意图'),
# ]
# category = None
# template = None

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

# if len(replacements) == 1:
# if False:
#     pages = [site.pages[item['title']] for item in site.search('_link')]
# else:
#     pages = get_pages(category=category, template=template)

# pages = set(list(site.pages['Template:意图'].embeddedin()))
# pages.union(set(list(site.pages['Template:Intent_link'].embeddedin())))
# pages = list(pages)

# for page in tqdm(pages):
#     text = page.text()
#     newtext = text
#     for old, new in replacements:
#         newtext = newtext.replace(old, new)
#     if newtext != text:
#         page.save(newtext, summary='批量替换文本')

NAVBOX = "{{怪物导航框}}"

def keep_last_navbox(text):
    parts = text.split(NAVBOX)

    # 0 或 1 个，不处理
    if len(parts) <= 2:
        return text

    # 只保留最后一个
    return "".join(parts[:-1]) + NAVBOX + parts[-1]


def main():
    for page in get_pages(template="怪物导航框"):
        try:
            # 跳过重定向
            if page.redirect:
                continue

            text = page.text()
            new_text = keep_last_navbox(text)

            # 有变化才保存
            if text != new_text:
                page.save(
                    new_text,
                    summary='清理重复怪物导航框，仅保留最后一个'
                )
                print(f'已清理: {page.name}')
                break

        except Exception as e:
            print(f'错误: {page.name} -> {e}')


if __name__ == "__main__":
    main()