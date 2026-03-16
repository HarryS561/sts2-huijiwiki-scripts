from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


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
            energy_icon = f"[[File:{self.color}_energy_icon.png|16px|link=能量]]" if self.color else ENERGY_ICON
            return Text(energy_icon * count)
        elif name == "star":
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
        # effect 模板内部不再嵌套颜色模板
        return flatten_text(node.child)

    if isinstance(node, Jitter):
        inner = unwrap_single(node.child)
        if isinstance(inner, Color):
            return f"{{{{抖动|{flatten_text(inner.child)}|{inner.color}}}}}"
        return f"{{{{抖动|{flatten_text(inner)}}}}}"

    if isinstance(node, Sine):
        inner = unwrap_single(node.child)
        if isinstance(inner, Color):
            return f"{{{{浮动|{flatten_text(inner.child)}|{inner.color}}}}}"
        return f"{{{{浮动|{flatten_text(inner)}}}}}"

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
            return f"{{{{抖动|{flatten_text(inner.child)}|{node.color}}}}}"

        if isinstance(inner, Sine):
            return f"{{{{浮动|{flatten_text(inner.child)}|{node.color}}}}}"

        return f"{{{{颜色|{node.color}|{render(inner)}}}}}"

    if isinstance(node, Jitter):
        inner = unwrap_single(node.child)

        if isinstance(inner, Color):
            return f"{{{{抖动|{flatten_text(inner.child)}|{inner.color}}}}}"

        return f"{{{{抖动|{flatten_text(inner)}}}}}"

    if isinstance(node, Sine):
        inner = unwrap_single(node.child)

        if isinstance(inner, Color):
            return f"{{{{浮动|{flatten_text(inner.child)}|{inner.color}}}}}"

        return f"{{{{浮动|{flatten_text(inner)}}}}}"

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
    ]

    for s in samples:
        print("IN :", s)
        print("OUT:", parse_tag(s))
        print("-" * 60)