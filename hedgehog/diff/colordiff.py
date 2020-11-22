import re

from termcolor import colored


def color_diff_lines(lines):
    last = None
    for line in lines:
        if line.startswith("?"):
            assert last is not None
            yield colorize_line(last, line)
            last = None
            continue
        if last is not None:
            yield last
        last = line
    if last is not None:
        yield last


def colorize_line(line, guide):
    if len(line) < len(guide):
        raise ValueError("Input line is shorter than guide")
    if not guide.startswith("? ") or not re.match(r"[+-] ", line):
        raise ValueError("Wrong format of line or guide strings")
    pattern = re.compile(r"[+^-]+")
    out = []
    last_end = 0
    for m in pattern.finditer(guide, 2):
        out.append(line[last_end : m.start()])  # copy characters before match
        chars = line[m.start() : m.end()]
        last_end = m.end()
        out.append(colored(chars, **_get_color(m)))
    out.append(line[last_end:])
    return "".join(out)


def _get_color(match):
    char = match[0][0]
    if char == "^":
        return {"on_color": "on_yellow"}
    elif char == "+":
        return {"on_color": "on_green"}
    elif char == "-":
        return {"on_color": "on_red"}
    raise ValueError("Invalid match type")
