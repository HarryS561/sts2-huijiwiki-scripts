from deprecated_utils import *

for event in tqdm(data['events']):
    event_name = event['name']
    page = site.pages[event_name]
    page_content = page.text()
    page_content = page_content.replace(r"{{{{事件导航框}}}}", r"{{事件导航框}}")
    page.save(page_content)
