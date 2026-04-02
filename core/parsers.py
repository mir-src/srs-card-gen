import re
import difflib

def render_cloze_front (text: str) -> str:
    pattern = r"\{\{c\d+::(.*?)\}\}"
    replacement = r"<span style='color: #89b4fa; font-weight: bold;'>[...]</span>"
    return re.sub(pattern, replacement, text)

def render_cloze_back(text: str) -> str:
    pattern = r"\{\{c\d+::(.*?)\}\}"
    replacement = r"<span style='color: #a6e3a1; font-weight: bold;'>\1</span>"
    return re.sub(pattern, replacement, text)

def check_type_answer(expected: str, user_input: str) -> str:
    matcher = difflib.SequenceMatcher(None, expected, user_input)
    html_result = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            # Correct letters (Green)
            html_result.append(f"<span style='color: #a6e3a1;'>{expected[i1:i2]}</span>")
        elif tag == 'replace':
            # Wrong letters typed (Red strikethrough) 
            html_result.append(f"<span style='color: #f38ba8; text-decoration: line-through;'>{user_input[j1:j2]}</span>")
            # Expected letters they missed/got wrong (Red)
            html_result.append(f"<span style='color: #f38ba8; font-weight: bold;'>{expected[i1:i2]}</span>")
        elif tag == 'delete':
            # Missed letters that the user forgot to type (Now Red!)
            html_result.append(f"<span style='color: #f38ba8; font-weight: bold;'>{expected[i1:i2]}</span>")
        elif tag == 'insert':
            # Extra letters the user shouldn't have typed (Red strikethrough)
            html_result.append(f"<span style='color: #f38ba8; text-decoration: line-through;'>{user_input[j1:j2]}</span>")
    
    return "".join(html_result)