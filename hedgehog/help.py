"""
Provide information about available tools.
"""
import json
import textwrap

from . import init, Print, META_FILE


def main():
    init(
        lambda p, v: p.parse_args(v),
        logger=False,
        argp_kwargs=dict(description=__doc__),
    )
    cprint = Print.instance()
    with META_FILE.open() as fp:
        meta = json.load(fp)
    print("%(name)s v%(version)s\n\nURL: %(repository)s\n" % meta)
    for name in sorted(meta["scripts"]):
        cprint(f"{name}", "yellow")
        text = "\n".join(textwrap.wrap(meta["scripts"][name]["brief"], width=70))
        print(textwrap.indent(text, "  "), end="\n\n")


if __name__ == "__main__":
    main()
