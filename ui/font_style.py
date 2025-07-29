import colorama

def italic(text: str):
    return colorama.ansi.code_to_chars(3) + text + colorama.ansi.code_to_chars(23)