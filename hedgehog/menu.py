from simple_term_menu import TerminalMenu


def confirm(question: str = None) -> bool:
    index = TerminalMenu(["[y] yes", "[n] no"], title=question).show()
    return index is not None and index == 0
