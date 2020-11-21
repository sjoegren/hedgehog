import textwrap
import pytest

from termcolor import colored

from hedgehog.diff import colordiff


DIFF_LINES = textwrap.dedent(
    """\
    - line unique in 1
    - The quick brown fox jumps over the lazy dog.
    ?           ------                        ^^^^
    + The super-quick fox jumps over the lazy cat
    ?     ++++++                              ^^^
    - this line is only in 1 too..
    + extra line"""
).splitlines()


def diff_generator(lines=None):
    if lines is None:
        lines = DIFF_LINES
    for line in lines:
        yield line


def test_color_diff_lines():
    result = colordiff.color_diff_lines(diff_generator())
    lines = list(result)
    expected = textwrap.dedent(
        """\
        - line unique in 1
        - The quick {}fox jumps over the lazy {}
        + The {}quick fox jumps over the lazy {}
        - this line is only in 1 too..
        + extra line"""
    ).format(
        colored("brown ", on_color="on_red"),
        colored("dog.", on_color="on_yellow"),
        colored("super-", on_color="on_green"),
        colored("cat", on_color="on_yellow"),
    )
    assert "\n".join(lines) == expected


def test_colorize_line_shorter_than_guide():
    with pytest.raises(ValueError, match="Input line is shorter than guide"):
        colordiff.colorize_line("- foo", "? ^^^     ----")


@pytest.mark.parametrize(
    "line, guide",
    [
        ("foo", "bar"),
        ("foooooo", "? bar"),
        ("+ foo", "?bar"),
        ("- foo", "  bar"),
        ("? foo", "? bar"),
        ("  foo", "? bar"),
    ],
)
def test_colorize_line_bogus_input_lines(line, guide):
    with pytest.raises(ValueError, match="Wrong format of line or guide strings"):
        colordiff.colorize_line(line, guide)


def test_colorize_line():
    line_ = "- foo bar baz and deleted words endword\n"
    guide = "?     ^^^ +++     -------------        \n"
    out = colordiff.colorize_line(line_, guide)
    assert out == "- foo {} {} and {} endword\n".format(
        colored("bar", on_color="on_yellow"),
        colored("baz", on_color="on_green"),
        colored("deleted words", on_color="on_red"),
    )


def test_colorize_line_end_with_diff():
    line_ = "- foo\n"
    guide = "? ^^^\n"
    out = colordiff.colorize_line(line_, guide)
    assert out == "- {}\n".format(
        colored("foo", on_color="on_yellow"),
    )
