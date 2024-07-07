'''
Small module for formatting
from: resposnse-request messages formatted as Basic formatting syntax
to: HTML format

using markdown, pygments, html_sanitizer
for formatting text, complex code and HTML

safe mode is enabled
'''
import re
import markdown
from html_sanitizer.sanitizer import Sanitizer, DEFAULT_SETTINGS
from pygments import highlight
from pygments.lexers import get_lexer_by_name, get_all_lexers
from pygments.formatters.html import HtmlFormatter


def remove_empty_tags(html_text):
    """
    Remove empty tags from the Html text
    """
    return re.sub(r"<(\w+)>[\s\n\r]*</\1>", '', html_text)


def sanitize_text(text, full = False):
    """
    Sanitize the text by replacing significant tags with their HTML equivalents
    Sanitize the text by cleaning the text for whitespaces and unnecessary tags(optional) 
    """
    # Replace every <any text> with '<any text>'
    # For auto formatting any defusing html as text
    pattern = r'(<.*?>)'
    replacement = r' `\1` '
    safe_text = re.sub(pattern, replacement, text)

    if not full:
        return safe_text

    sanitizer = Sanitizer(settings = DEFAULT_SETTINGS)
    sanitized_text = sanitizer.sanitize(safe_text)

    return sanitized_text

def format_text(text):
    """
    Format the text using markdown
    and return it as HTML
    """
    text = sanitize_text(text)
    md = markdown.Markdown(
        safe_mode=True,
        extensions=[
            'markdown.extensions.extra', 
            'markdown.extensions.md_in_html', 
            'markdown.extensions.tables'
        ]
    )
    formatted_text = md.convert(text)

    return formatted_text


def get_lexer(code):
    """
    Gets the lexer of the written code block
    defaults to python if no language is specified.
    """
    default_lang = 'python'
    langs = [code.split('\n')[0], code.split(' ')[0]]

    lexer_names = [name.lower() for name, _, _, _ in list(get_all_lexers())]
    for lang in langs:
        if lang.lower() in lexer_names:
            return get_lexer_by_name(lang)

    return get_lexer_by_name(default_lang)

def format_code(code):
    """
    Highlight the code using Pygments 
    and return it as HTML
    """
    lexer = get_lexer(code)
    lang = lexer.name

    title_index = code.lower().find(lang.lower())
    title = code[title_index:title_index + len(lang)]
    code = code.replace(title, '', 1)

    formatter = HtmlFormatter(style='monokai', full=True, linenos=False)
    highlighted_code = highlight(code, lexer, formatter)

    #add class for pre, for css better formatting
    formatted_code = highlighted_code.replace(
        '<pre>', 
        f'<pre><div class="code-header"><span class="lang">{lang}</span></div>'
    )

    return formatted_code


def find_all_indexes(text, substring):
    """
    Find all indexes of a substring in a text
    """
    return [m.start() for m in re.finditer(substring, text)]

def html_format(text):
    """
    Convert basic syntax python text to HTML format
    """
    formatted = []
    code_indexes = find_all_indexes(text, '```')

    index = 0
    while code_indexes:
        start = code_indexes.pop(0) + 3
        end = code_indexes.pop(0) if code_indexes else len(text)

        text_block = text[index:start]
        code_block = text[start:end]

        formatted.append(format_text(text_block))
        formatted.append(format_code(code_block))

        index = end

    formatted.append(format_text(text[index:]))

    formatted = ''.join(formatted)
    formatted = remove_empty_tags(formatted).replace('```', '')

    return formatted
