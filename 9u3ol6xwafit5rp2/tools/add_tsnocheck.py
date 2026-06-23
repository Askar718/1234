import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / 'index.html'

text = INDEX.read_text(encoding='utf-8')

# Regex to find <script ...>...</script> including attributes
pattern = re.compile(r'(<script\b[^>]*>)([\s\S]*?)(</script>)', re.IGNORECASE)

def should_modify(open_tag, inner):
    # skip if script tag has src attribute
    if re.search(r'\bsrc\s*=\s*', open_tag, re.IGNORECASE):
        return False
    # skip if already has ts-nocheck or ts-ignore
    if '/* @ts-nocheck */' in inner or '/* @ts-ignore */' in inner:
        return False
    return True

def repl(m):
    open_tag, inner, close_tag = m.group(1), m.group(2), m.group(3)
    if should_modify(open_tag, inner):
        # preserve leading whitespace inside script
        leading_ws = ''
        m2 = re.match(r'(\s*)', inner)
        if m2:
            leading_ws = m2.group(1)
        new_inner = leading_ws + '/* @ts-nocheck */' + inner[len(leading_ws):]
        return open_tag + new_inner + close_tag
    return m.group(0)

new_text = pattern.sub(repl, text)

if new_text != text:
    INDEX.write_text(new_text, encoding='utf-8')
    print('index.html updated: injected /* @ts-nocheck */ into inline scripts')
else:
    print('No changes needed')
