from pathlib import Path
import re
from bs4 import BeautifulSoup, Tag


def slugify(text):
    s = re.sub(r"\s+", "-", text.strip().lower())
    s = re.sub(r"[^a-z0-9\-]+", "", s)
    s = re.sub(r"\-+", "-", s).strip("-")
    return s or "section"


def text_content(node):
    return " ".join(node.stripped_strings)


def visible_heading_text(tag):
    parts = []
    for child in tag.children:
        if isinstance(child, Tag) and 'anchor-link' in child.get('class', []):
            continue
        parts.append(child.get_text(strip=True) if hasattr(child, 'get_text') else str(child).strip())
    return ' '.join([part for part in parts if part])


source = Path('rn-staff-manual-2026.html').read_text('utf-8')
soup = BeautifulSoup(source, 'html.parser')

for box in soup.select('div.iq-box'):
    new_block = soup.new_tag('div', **{'class': 'qa-block'})
    header = box.find('div', class_='iq-header')
    if header:
        meta = soup.new_tag('div', **{'class': 'qa-meta'})
        for span in header.find_all('span'):
            classes = span.get('class', [])
            label_text = span.get_text(strip=True)
            if 'iq-level' in classes:
                level_key = slugify(label_text.split()[0])
                badge = soup.new_tag('span', **{'class': f'badge-level {level_key}'})
                badge.string = label_text
                meta.append(badge)
            else:
                label = soup.new_tag('span', **{'class': 'qa-label'})
                label.string = label_text
                meta.append(label)
        if meta.contents:
            new_block.append(meta)
    q = box.find('div', class_='iq-q')
    a = box.find('div', class_='iq-a')
    if q:
        q_block = soup.new_tag('div', **{'class': 'qa-question'})
        q_block.extend(q.contents)
        new_block.append(q_block)
    if a:
        a_block = soup.new_tag('div', **{'class': 'qa-answer'})
        a_block.extend(a.contents)
        new_block.append(a_block)
    box.replace_with(new_block)

for span in soup.select('span.iq-level'):
    text_val = span.get_text(strip=True)
    if text_val:
        level_key = slugify(text_val.split()[0])
        span['class'] = ['badge-level', level_key]
        span.string = text_val

for tag in soup.find_all(['h2', 'h3']):
    heading_text = text_content(tag)
    if not heading_text:
        continue
    slug = slugify(heading_text)
    tag['id'] = slug
    for a in tag.find_all('a', class_='anchor-link'):
        a.decompose()
    anchor = soup.new_tag('a', href=f'#{slug}', **{'aria-label': 'Permalink', 'class': 'anchor-link'})
    anchor.string = '¶'
    tag.append(anchor)

for pre in soup.find_all('pre'):
    parent = pre.parent
    if parent.name == 'div' and 'code-block' in parent.get('class', []):
        continue
    wrapper = soup.new_tag('div', **{'class': 'code-block'})
    topbar = soup.new_tag('div', **{'class': 'code-block__topbar'})
    badge = soup.new_tag('span', **{'class': 'code-block__badge'})
    badge.string = 'Text'
    button = soup.new_tag('button', **{'aria-label': 'Copy code', 'class': 'copy-btn', 'type': 'button'})
    button.string = '📋'
    topbar.extend([badge, button])
    wrapper.append(topbar)
    pre.replace_with(wrapper)
    wrapper.append(pre)

for table in soup.find_all('table'):
    parent = table.parent
    if parent.name == 'div' and 'table-responsive-custom' in parent.get('class', []):
        continue
    wrapper = soup.new_tag('div', **{'class': 'table-responsive-custom'})
    table.replace_with(wrapper)
    wrapper.append(table)

sidebar_items = []
right_toc_items = []
for tag in soup.find_all(['h2', 'h3']):
    if not tag.get('id'):
        continue
    label = visible_heading_text(tag)
    if not label:
        continue
    href = f'#{tag["id"]}'
    if tag.name == 'h2':
        sidebar_items.append((label, href))
    css_class = 'toc-link'
    if tag.name == 'h3':
        css_class += ' toc-sub'
    right_toc_items.append((label, href, css_class))

sidebar_html = ''.join(f'          <a class="sidebar-link" href="{href}">{label}</a>\n' for label, href in sidebar_items)
right_toc_html = ''.join(f'          <a class="{css_class}" href="{href}">{label}</a>\n' for label, href, css_class in right_toc_items)

body = soup.body
if body is None:
    raise SystemExit('No body found in source')
content_html = ''.join(str(child) for child in body.contents if not (getattr(child, 'name', None) == 'script' and child.get('src') == '_scripts.js'))

final_html = """<!doctype html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
    <title>Staff React Native Field Manual 2026</title>
    <link rel=\"preconnect\" href=\"https://fonts.googleapis.com\" />
    <link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin />
    <link href=\"https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;650;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap\" rel=\"stylesheet\" />
    <link href=\"https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css\" rel=\"stylesheet\" integrity=\"sha384-ENjdO4Dr2bkBIFxQpeoY9Iu7AMLZc2xno1pB2iZYG3zv2RjO4DQBvYQ7S8ar4k+N\" crossorigin=\"anonymous\" />
    <link rel=\"stylesheet\" href=\"_theme.css\" />
    <style>
      .main .toc {
        background: var(--bg2);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 2rem;
        margin: 3rem auto;
        max-width: 1200px;
        position: relative;
      }

      .main .toc::before {
        content: 'TABLE OF CONTENTS';
        display: block;
        font-size: 10px;
        letter-spacing: 0.2em;
        color: var(--accent);
        margin-bottom: 1.5rem;
        font-weight: 700;
      }

      .main .toc-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
        gap: 0.5rem;
      }

      .main .toc a {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 8px 12px;
        color: var(--text2);
        text-decoration: none;
        border-radius: 6px;
        font-size: 12px;
        transition: all 0.2s;
        border: 1px solid transparent;
      }

      .main .toc a:hover {
        color: var(--accent);
        background: rgba(0,212,255,0.05);
        border-color: rgba(0,212,255,0.2);
      }

      .main .toc a .toc-num {
        font-size: 10px;
        color: var(--accent2);
        font-weight: 700;
        min-width: 24px;
        font-family: var(--font-head);
      }
    </style>
  </head>
  <body class="staff-manual">
    <div id=\"reading-progress\"></div>
    <header class=\"navbar-custom\">
      <div class=\"navbar-inner\">
        <a class=\"navbar-brand\" href=\"index.html\">
          <span class=\"brand-mark\">RN</span>
          <span class=\"brand-label\">Docs</span>
        </a>
        <nav class=\"navbar-links\" aria-label=\"Primary navigation\">
          <a class=\"navbar-link\" href=\"index.html\">Home</a>
          <a class=\"navbar-link\" href=\"rn_interview_field_manual.html\">Interview</a>
          <a class=\"navbar-link\" href=\"rn_interview_supplement.html\">DSA</a>
          <a class=\"navbar-link\" href=\"rn-staff-manual-2026.html\">Staff Manual</a>
        </nav>
        <button id=\"drawer-toggle\" class=\"navbar-toggler\" type=\"button\" aria-label=\"Open navigation\">
          <svg width=\"20\" height=\"20\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"M4 7h16M4 12h16M4 17h16\"/></svg>
        </button>
      </div>
    </header>
    <div class=\"app-shell d-flex align-items-start\">
      <aside class=\"sidebar\" aria-label=\"Sidebar navigation\">
        <div class=\"sidebar-section\">
          <label>Sections</label>
{sidebar_html}        </div>
      </aside>
      <main class=\"main\" role=\"main\">
{content_html}
      </main>
      <aside class=\"toc\" aria-label=\"Table of contents\">
{right_toc_html}      </aside>
    </div>
    <button id=\"contents-btn\" type=\"button\" aria-label=\"Open contents\">
      Contents
    </button>
    <div id=\"mobile-drawer\" class=\"mobile-drawer\" aria-hidden=\"true\">
      <div class=\"drawer-header\">
        <strong>Navigation</strong>
        <button id=\"drawer-close\" class=\"drawer-close\" type=\"button\" aria-label=\"Close navigation\">✕</button>
      </div>
      <div class=\"p-3\">
{sidebar_html}      </div>
    </div>
    <div id=\"drawer-overlay\" class=\"overlay\" aria-hidden=\"true\"></div>
    <div id=\"mobile-toc-drawer\" class=\"mobile-toc-drawer\" aria-hidden=\"true\">
      <div class=\"drawer-header\">
        <strong>Contents</strong>
        <button class=\"drawer-close\" type=\"button\" aria-label=\"Close contents\">✕</button>
      </div>
      <div class=\"p-3\">
{right_toc_html}      </div>
    </div>
    <div id=\"toc-overlay\" class=\"overlay\" aria-hidden=\"true\"></div>
    <button id=\"back-to-top\" type=\"button\" aria-label=\"Back to top\">
      ↑
    </button>
    <footer class=\"container-fluid\">
      <div class=\"footer-links\">
        <a href=\"index.html\">Home</a>
        <a href=\"rn_engineering_reference_2025.html\">Engineering Reference</a>
        <a href=\"rn_interview_field_manual.html\">Interview Field Manual</a>
        <a href=\"rn_interview_supplement.html\">Interview Supplement</a>
        <a href=\"rn-staff-manual-2026.html\">Staff Manual</a>
      </div>
    </footer>
    <script src=\"_scripts.js\"></script>
  </body>
</html>
"""

final_html = final_html.replace('{sidebar_html}', sidebar_html).replace('{right_toc_html}', right_toc_html).replace('{content_html}', content_html)
Path('rn-staff-manual-2026.transformed.html').write_text(final_html, 'utf-8')
print('h2 count', len(sidebar_items))
print('toc count', len(right_toc_items))
