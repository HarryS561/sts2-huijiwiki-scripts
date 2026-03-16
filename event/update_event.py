from hashlib import new
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils import *

class EventWikiBot:
    QUEST_NAMES = ['多尼斯异鸟蛋', '灯火钥匙', '藏宝图', '历史课', '天选芝士', '污浊药水', '啄击', 
                   '坚韧之环', '石之剑', '发光水', '菲涅耳透镜', '开悟', '杀灭', '压扁', '花粉核心', 
                   '羽化', '究极打击', '究极防御', '棱镜碎片', '王室猛毒', '大蘑菇', '芳香蘑菇', '遗忘之魂']
    ENCHANTMENT_NAMES = [e["name"] for e in json.load(open("data/enchantments.json", encoding="utf-8"))]
    CURSE_NAMES = [e["name"] for e in json.load(open("data/cards.json", encoding="utf-8")) if e['rarity'] == 'Curse']
    EN_REPLACEMENTS = {
        (' Max HP', '最大生命值'), 
        ('one of your Relics', '你的1件随机遗物'),
        ('a random Relic', '1件随机遗物'),
        ('a random Card', '1张随机卡牌'),
        ('a random Potion', '1瓶随机药水'),
        ('a Potion', '1瓶随机药水'),
        ('Obtain ', '获得'),
        ('. 拾起时', '。拾起时'),
        ('Add Writhe', '将一张苦恼添加'),
        ('Potion', '药水'),
        ('Relic', '遗物'),
        (' Max', '最大生命值')
    }
    PREVENT_MODIFY = "<!--本条注释用于防止机器人更新这个事件-->"

    def __init__(self):
        self.events = get_data_by_api("events")
        # with open(events_file_path, 'r', encoding='utf-8') as f:
        #     self.events = json.load(f)
        self.events_by_id = {event['id']: event for event in self.events}
        self.missing_notes = []

    def _clean_text(self, text, addlink = False):
        if not text:
            return ''
        text = re.sub(r"\[/?[a-z]+(?::\d+)?\]", "", text)
        for orig, repl in self.EN_REPLACEMENTS:
            text = text.replace(orig, repl)
        if addlink:
            for quest_name in self.QUEST_NAMES:
                text = text.replace(quest_name, f'{{{{Card_link|{quest_name}}}}}')
            for curse_name in self.CURSE_NAMES:
                text = text.replace(curse_name, f'{{{{Card_link|{curse_name}}}}}')
            for enchantment_name in self.ENCHANTMENT_NAMES:
                text = text.replace(enchantment_name, f'[[附魔|{enchantment_name}]]')
        text = text.replace("\n\n", "\n").replace("\n", "<br />")
        return text

    def _extract_existing_notes(self, page_content):
        notes = {}
        
        try:
            wikicode = parse(page_content)
            
            for template in wikicode.filter_templates():
                if template.name.strip() == '事件选项':
                    level_param = template.get('层级')
                    option_param = template.get('选项')
                    note_param = template.get('备注')
                    
                    if level_param and option_param:
                        try:
                            level = int(str(level_param.value).strip())
                            option = str(option_param.value).strip()
                            note = str(note_param.value).strip() if note_param else ''
                            
                            if note:
                                notes[(level, option)] = note
                        except (ValueError, AttributeError):
                            continue
        
        except Exception as e:
            print(f"mwparserfromhell解析失败，使用正则表达式回退: {e}")
            return self._extract_existing_notes_regex_fallback(page_content)
        
        return notes
    
    def _extract_existing_notes_regex_fallback(self, page_content):
        notes = {}
        pattern = r'\{\{事件选项\s*\n\s*\|\s*层级\s*=\s*(\d+)\s*\n\s*\|\s*选项\s*=\s*([^\n]+)\s*\n(?:\s*\|\s*锁定\s*=\s*[^\n]*\n)?(?:\s*\|\s*详情\s*=\s*[^\n]*\n)?(?:\s*\|\s*结果\s*=\s*[^\n]*\n)?\s*\|\s*备注\s*=\s*([^\}]*)\s*\n\}\}'
        
        matches = re.findall(pattern, page_content, re.MULTILINE | re.DOTALL)
        for match in matches:
            level = int(match[0])
            option = match[1].strip()
            note = match[2].strip() if len(match) > 2 else ''
            if note:
                notes[(level, option)] = note
        
        return notes
    
    def _replace_options_content(self, text, new_content):
        code = parse(text)
        start = None
        last_template_end = None
        pos = 0
        for node in code.nodes:
            s = str(node)
            node_start = pos
            node_end = pos + len(s)
            # 找 ==选项==
            if isinstance(node, nodes.heading.Heading):
                if str(node.title).strip() == "选项":
                    start = node_end
            # 找 {{事件选项}}
            elif start is not None and isinstance(node, nodes.template.Template):
                if str(node.name).strip() == "事件选项":
                    last_template_end = node_end
            pos = node_end
        if start is None or last_template_end is None:
            return text
        return text[:start] + "\n" + new_content.strip() + text[last_template_end:]

    def _should_skip_update(self, page_content):
        return self.PREVENT_MODIFY in page_content

    def _generate_option_template(self, option, level, locked_desc, result_desc, existing_note=''):
        # Escape pipe characters in content
        title = self._clean_text(option.get('title', ''))
        description = self._clean_text(option.get('description', ''), addlink=True)
        locked_text = self._clean_text(locked_desc)
        result_text = self._clean_text(result_desc)

        parts = [
            '{{事件选项',
            f' |层级 = {level}'
        ]
        if title:
            parts.append(f' |选项 = {title}')
        if locked_text:
            parts.append(f' |锁定 = {locked_text}')
        if description:
            parts.append(f' |详情 = {description}')
        if result_text:
            parts.append(f' |结果 = {result_text}')
        parts.append(f' |备注 = {existing_note}')
        parts.append('}}')
        return '\n' + '\n'.join(parts)

    def _process_page_recursive(self, page, level, all_pages_map, existing_notes, visited_page_ids=None):
        if visited_page_ids is None:
            visited_page_ids = set()
        
        wikitext = ''
        if not page or not page.get('options'):
            return wikitext

        current_page_id = page.get('id')
        if current_page_id in visited_page_ids:
            return wikitext
        visited_page_ids.add(current_page_id)

        options = page['options']
        locked_descriptions = {}
        for opt in options:
            opt_id = opt.get('id', '')
            if opt_id.endswith('_LOCKED'):
                base_id = opt_id.replace('_LOCKED', '')
                locked_descriptions[base_id] = opt.get('description', '')

        for option in options:
            option_id = option.get('id')
            if not option_id or option_id.endswith('_LOCKED'):
                continue

            target_page = all_pages_map.get(option_id)
            result_description = target_page.get('description', '') if target_page else ''
            locked_description = locked_descriptions.get(option_id, '')
            
            option_title = option.get('title', '')
            existing_note = existing_notes.get((level, option_title), '')
            
            wikitext += self._generate_option_template(
                option,
                level,
                locked_description,
                result_description,
                existing_note
            )

            if target_page and target_page.get('options'):
                wikitext += self._process_page_recursive(target_page, level + 1, all_pages_map, existing_notes, visited_page_ids.copy())
        
        return wikitext

    def generate_event_wikitext(self, event_id, existing_page_content=''):
        event = self.events_by_id.get(event_id)
        if not event:
            return f"Event with ID '{event_id}' not found."

        if existing_page_content and self._should_skip_update(existing_page_content):
            return None

        existing_notes = {}
        if existing_page_content:
            existing_notes = self._extract_existing_notes(existing_page_content)

        wikitext = self._clean_text(event.get('description', ''))

        if not event.get('pages'):
            if event.get('options'):
                page_for_processing = {'id': 'dummy', 'options': event.get('options')}
                wikitext += self._process_page_recursive(page_for_processing, 1, {}, existing_notes)
            return wikitext

        all_pages_map = {p['id']: p for p in event['pages']}
        
        initial_page = all_pages_map.get('INITIAL')
        if not initial_page:
            if all_pages_map:
                initial_page = next(iter(all_pages_map.values()))
            else:
                return wikitext

        wikitext += self._process_page_recursive(initial_page, 1, all_pages_map, existing_notes)
        return wikitext

    def update_wiki_page(self, page_title, event_id):
        try:
            page = site.pages[page_title]
            
            existing_content = page.text()
            
            if not existing_content:
                print(f"页面不存在或为空: {page_title}")
                return False
            
            if self._should_skip_update(existing_content):
                print(f"跳过更新：页面包含防止更新的注释: {page_title}")
                return False
            
            new_content = self.generate_event_wikitext(event_id, existing_content)

            new_content = self._replace_options_content(existing_content, new_content)
            
            if new_content is None:
                print(f"跳过更新：页面包含防止更新的注释: {page_title}")
                return False
            
            page.edit(new_content, summary=f'更新事件数据 (版本 {ver})')
            return True
            
        except Exception as e:
            print(f"更新页面失败 {page_title}: {str(e)}")
            return False

    def print_missing_notes_report(self):
        if not self.missing_notes:
            print("没有发现丢失的备注。")
            return
        
        print("\n" + "="*30)
        print("丢失的备注报告")
        print("="*30)
        
        notes_by_page = {}
        for page_title, level, option, note in self.missing_notes:
            if page_title not in notes_by_page:
                notes_by_page[page_title] = []
            notes_by_page[page_title].append((level, option, note))
            
        for page_title, notes in notes_by_page.items():
            print(f"\n页面: {page_title}")
            for level, option, note in notes:
                print(f"  - 层级{level}, 选项'{option}': {note}")
        
        print("\n" + "="*30)

    def update_all_events(self):
        """
        批量更新所有事件页面
        
        Args:
            prefix: 页面标题前缀，默认为"事件:"
            batch_size: 每批处理的事件数量
            delay: 每批之间的延迟时间（秒）
        """
        success_count = 0
        skip_count = 0
        error_count = 0
        total_events = len(self.events)
        print(f"开始更新所有事件页面，共 {total_events} 个事件")
        
        for i, event in enumerate(self.events, 1):
            event_id = event.get('id')
            event_name = event.get('name', event_id)
            page_title = event_name
            
            print(f"[{i}/{total_events}] {event_name}", end="")

            if event.get('type') == 'Ancient':
                skip_count += 1
                print(f"  - 跳过更新")
                continue
            
            try:
                result = self.update_wiki_page(page_title, event_id)
                if result:
                    success_count += 1
                    print(f"  ✓ 成功更新")
                else:
                    skip_count += 1
                    print(f"  - 跳过更新")
                    
            except Exception as e:
                error_count += 1
                print(f"  ✗ 更新失败: {str(e)}")
        
        print("\n" + "="*50)
        print("批量更新完成")
        print("="*50)
        print(f"总事件数: {total_events}")
        print(f"成功更新: {success_count}")
        print(f"跳过更新: {skip_count}")
        print(f"更新失败: {error_count}")
        
        # 打印丢失的备注报告
        self.print_missing_notes_report()
        
        return {
            'total': total_events,
            'success': success_count,
            'skipped': skip_count,
            'errors': error_count
        }


if __name__ == '__main__':
    bot = EventWikiBot()
    bot.update_all_events()
    