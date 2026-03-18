from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import re

COLOR_TAGS = {
    "gold",
    "red",
    "blue",
    "green",
    "purple",
    "orange",
    "pink",
    "aqua",
}

ENERGY_MAPPING = {
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

ENERGY_ICON = "[[File:colorless_energy_icon.png|16px|link=能量]]"
STAR_ICON = "[[File:star_icon.png|16px|link=辉星]]"
BR_TAG = "<br/>"
BR_PATTERN = re.compile(r"<br\s*/?>", re.IGNORECASE)


class Node:
    pass


@dataclass
class Text(Node):
    value: str


@dataclass
class Seq(Node):
    items: list[Node]


@dataclass
class Color(Node):
    color: str
    child: Node


@dataclass
class Jitter(Node):
    child: Node


@dataclass
class Sine(Node):
    child: Node


@dataclass
class Bold(Node):
    child: Node


@dataclass
class Italic(Node):
    child: Node


@dataclass
class EffectRun:
    text: str
    color: Optional[str]
    bold: bool
    italic: bool


class Parser:
    def __init__(self, text: str, color: Optional[str] = None):
        self.text = text
        self.pos = 0
        self.color = ENERGY_MAPPING.get(color, "colorless")

    def eof(self) -> bool:
        return self.pos >= len(self.text)

    def peek(self) -> str:
        return "" if self.eof() else self.text[self.pos]

    def startswith(self, s: str) -> bool:
        return self.text.startswith(s, self.pos)

    def consume(self, n: int = 1) -> str:
        s = self.text[self.pos:self.pos + n]
        self.pos += n
        return s

    def parse(self) -> Node:
        return self._parse_until(None)

    def _parse_until(self, end_tag: Optional[str]) -> Node:
        items: list[Node] = []
        buf: list[str] = []

        def flush_text() -> None:
            if buf:
                items.append(Text("".join(buf)))
                buf.clear()

        while not self.eof():
            if end_tag is not None and self.startswith(f"[/{end_tag}]"):
                self.consume(len(f"[/{end_tag}]"))
                flush_text()
                return Seq(items)

            if self.peek() != "[":
                buf.append(self.consume())
                continue

            node = self._parse_tag()
            if node is None:
                buf.append(self.consume())
            else:
                flush_text()
                items.append(node)

        flush_text()
        return Seq(items)

    def _parse_tag(self) -> Optional[Node]:
        if self.peek() != "[":
            return None

        close = self.text.find("]", self.pos)
        if close == -1:
            return None

        raw_tag = self.text[self.pos + 1:close].strip()
        if raw_tag.startswith("/"):
            return None

        old_pos = self.pos
        self.pos = close + 1

        icon_node = self._parse_icon_tag(raw_tag)
        if icon_node is not None:
            return icon_node

        tag = raw_tag.lower()

        if tag in COLOR_TAGS:
            child = self._parse_until(tag)
            return Color(tag, child)

        if tag == "jitter":
            child = self._parse_until(tag)
            return Jitter(child)

        if tag == "sine":
            child = self._parse_until(tag)
            return Sine(child)

        if tag == "b":
            child = self._parse_until(tag)
            return Bold(child)

        if tag == "i":
            child = self._parse_until(tag)
            return Italic(child)

        self.pos = old_pos
        return None

    def _parse_icon_tag(self, raw_tag: str) -> Optional[Node]:
        tag = raw_tag.lower().strip()

        if ":" in tag:
            name, count_str = tag.split(":", 1)
            name = name.strip()
            count_str = count_str.strip()
        else:
            name = tag
            count_str = "1"

        if name not in {"energy", "star"}:
            return None

        try:
            count = max(0, int(count_str))
        except ValueError:
            count = 1

        if name == "energy":
            energy_icon = (
                f"[[File:{self.color}_energy_icon.png|16px|link=能量]]"
                if self.color
                else ENERGY_ICON
            )
            return Text(energy_icon * count)

        if name == "star":
            return Text(STAR_ICON * count)

        return None


def unwrap_single(node: Node) -> Node:
    while isinstance(node, Seq) and len(node.items) == 1:
        node = node.items[0]
    return node


def simplify(node: Node) -> Node:
    if isinstance(node, Seq):
        items = [simplify(x) for x in node.items]
        if len(items) == 1:
            return items[0]
        return Seq(items)

    if isinstance(node, Color):
        return Color(node.color, simplify(node.child))

    if isinstance(node, Jitter):
        return Jitter(simplify(node.child))

    if isinstance(node, Sine):
        return Sine(simplify(node.child))

    if isinstance(node, Bold):
        return Bold(simplify(node.child))

    if isinstance(node, Italic):
        return Italic(simplify(node.child))

    return node


def split_node_by_br(node: Node) -> list[Node]:
    """
    按 <br/> / <br> / <br /> 把节点拆成多段，同时尽量保留结构。
    """
    if isinstance(node, Text):
        parts = BR_PATTERN.split(node.value)
        return [Text(part) for part in parts]

    if isinstance(node, Seq):
        segments: list[list[Node]] = [[]]

        for item in node.items:
            subparts = split_node_by_br(item)
            segments[-1].append(subparts[0])

            for extra in subparts[1:]:
                segments.append([extra])

        return [simplify(Seq(seg)) for seg in segments]

    if isinstance(node, Color):
        parts = split_node_by_br(node.child)
        return [Color(node.color, part) for part in parts]

    if isinstance(node, Bold):
        parts = split_node_by_br(node.child)
        return [Bold(part) for part in parts]

    if isinstance(node, Italic):
        parts = split_node_by_br(node.child)
        return [Italic(part) for part in parts]

    if isinstance(node, Jitter):
        parts = split_node_by_br(node.child)
        return [Jitter(part) for part in parts]

    if isinstance(node, Sine):
        parts = split_node_by_br(node.child)
        return [Sine(part) for part in parts]

    return [node]


def wrap_bi_outside(text: str, has_bold: bool, has_italic: bool) -> str:
    if has_bold:
        text = f"'''{text}'''"
    if has_italic:
        text = f"''{text}''"
    return text


def merge_adjacent_runs(runs: list[EffectRun]) -> list[EffectRun]:
    merged: list[EffectRun] = []
    for run in runs:
        if not run.text:
            continue

        if (
            merged
            and merged[-1].color == run.color
            and merged[-1].bold == run.bold
            and merged[-1].italic == run.italic
        ):
            merged[-1].text += run.text
        else:
            merged.append(EffectRun(run.text, run.color, run.bold, run.italic))
    return merged


def collect_effect_runs(
    node: Node,
    current_color: Optional[str] = None,
    current_bold: bool = False,
    current_italic: bool = False,
) -> list[EffectRun]:
    """
    把一个节点拆成 effect 内部的若干 run。
    每个 run 记录：
    - text
    - color
    - bold
    - italic

    这样可以保证 b/i 永远放在 jitter/sine 外面，
    且当段内样式变化时会自动拆成多个 effect 片段。
    """
    node = unwrap_single(node)

    if isinstance(node, Text):
        return [EffectRun(node.value, current_color, current_bold, current_italic)]

    if isinstance(node, Seq):
        runs: list[EffectRun] = []
        for item in node.items:
            runs.extend(
                collect_effect_runs(
                    item,
                    current_color=current_color,
                    current_bold=current_bold,
                    current_italic=current_italic,
                )
            )
        return merge_adjacent_runs(runs)

    if isinstance(node, Bold):
        return collect_effect_runs(
            node.child,
            current_color=current_color,
            current_bold=True,
            current_italic=current_italic,
        )

    if isinstance(node, Italic):
        return collect_effect_runs(
            node.child,
            current_color=current_color,
            current_bold=current_bold,
            current_italic=True,
        )

    if isinstance(node, Color):
        return collect_effect_runs(
            node.child,
            current_color=node.color,
            current_bold=current_bold,
            current_italic=current_italic,
        )

    if isinstance(node, Jitter):
        nested = render_effect_segments(node.child, "抖动", color_override=current_color)
        return [EffectRun(nested, None, current_bold, current_italic)]

    if isinstance(node, Sine):
        nested = render_effect_segments(node.child, "浮动", color_override=current_color)
        return [EffectRun(nested, None, current_bold, current_italic)]

    raise TypeError(f"Unknown node type: {type(node)!r}")


def render_effect_run(effect_name: str, run: EffectRun) -> str:
    if not run.text:
        return ""

    if run.color is not None:
        effect_text = f"{{{{{effect_name}|{run.text}|{run.color}}}}}"
    else:
        effect_text = f"{{{{{effect_name}|{run.text}}}}}"

    return wrap_bi_outside(effect_text, run.bold, run.italic)


def render_effect_segments(
    child: Node,
    effect_name: str,
    color_override: Optional[str] = None,
) -> str:
    """
    将抖动/浮动内容按 <br/> 分段渲染：
    1. 每一行单独处理
    2. 行内再按 b / i / color 变化拆成多个 run
    3. 每个 run 单独变成一个 effect
    4. b/i 永远包在 effect 外面
    """
    segments = split_node_by_br(child)
    rendered_segments: list[str] = []

    for seg in segments:
        runs = collect_effect_runs(seg, current_color=color_override)
        rendered = "".join(render_effect_run(effect_name, run) for run in runs)
        rendered_segments.append(rendered)

    return BR_TAG.join(rendered_segments)


def flatten_text(node: Node) -> str:
    node = unwrap_single(node)

    if isinstance(node, Text):
        return node.value

    if isinstance(node, Seq):
        return "".join(flatten_text(x) for x in node.items)

    if isinstance(node, Bold):
        return f"'''{flatten_text(node.child)}'''"

    if isinstance(node, Italic):
        return f"''{flatten_text(node.child)}''"

    if isinstance(node, Color):
        return flatten_text(node.child)

    if isinstance(node, Jitter):
        return render_effect_segments(node.child, "抖动")

    if isinstance(node, Sine):
        return render_effect_segments(node.child, "浮动")

    raise TypeError(f"Unknown node type: {type(node)!r}")


def render(node: Node) -> str:
    node = unwrap_single(node)

    if isinstance(node, Text):
        return node.value

    if isinstance(node, Seq):
        return "".join(render(x) for x in node.items)

    if isinstance(node, Bold):
        return f"'''{render(node.child)}'''"

    if isinstance(node, Italic):
        return f"''{render(node.child)}''"

    if isinstance(node, Color):
        inner = unwrap_single(node.child)

        if isinstance(inner, Jitter):
            return render_effect_segments(inner.child, "抖动", node.color)

        if isinstance(inner, Sine):
            return render_effect_segments(inner.child, "浮动", node.color)

        return f"{{{{颜色|{node.color}|{render(inner)}}}}}"

    if isinstance(node, Jitter):
        return render_effect_segments(node.child, "抖动")

    if isinstance(node, Sine):
        return render_effect_segments(node.child, "浮动")

    raise TypeError(f"Unknown node type: {type(node)!r}")


def parse_tag(text: str, color: Optional[str] = None) -> str:
    tree = Parser(text, color).parse()
    tree = simplify(tree)
    return render(tree)


if __name__ == "__main__":
    samples = [
        "[jitter]CLANG![/jitter]",
        "[sine]swirling vortex[/sine]",
        "[red]blood[/red]",
        "[green]healed[/green]",
        "[red][jitter]穷凶极恶的虫群[/jitter][/red]",
        "[jitter][red]穷凶极恶的虫群[/red][/jitter]",
        "[red][sine]穷凶极恶的虫群[/sine][/red]",
        "[sine][red]穷凶极恶的虫群[/red][/sine]",
        "[b]bold[/b] and [i]italic[/i]",
        "[energy:2] Gain [star:1]",
        "[gold]A [blue]nested[/blue] test[/gold]",
        "[red][b]Big[/b] hit[/red]",
        "[jitter][b]震动粗体[/b] [star:2][/jitter]",
        "[jitter]第一行<br/>第二行[/jitter]",
        "[sine][red]第一行[/red]<br/>[blue]第二行[/blue][/sine]",
        "[red][jitter]第一行<br/>第二行[/jitter][/red]",
        "[jitter][b]第一行[/b]<br/>[i]第二行[/i][/jitter]",
        "[sine][b][i]同时格式[/i][/b][/sine]",
        "[red][jitter][b]第一行[/b]<br/>第二行[/jitter][/red]",
        "[jitter][b]震动粗体[/b] [star:2][/jitter]",
        "[sine]上一次吃饭是什么时候来着？<br />…等等，这股奇妙的香味是怎么回事？[/sine]",
    ]

    for s in samples:
        print("IN :", s)
        print("OUT:", parse_tag(s))
        print("-" * 60)