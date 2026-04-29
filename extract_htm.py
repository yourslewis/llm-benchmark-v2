from bs4 import BeautifulSoup
import re

with open('/tmp/design_doc.htm', 'r', encoding='utf-8', errors='ignore') as f:
    soup = BeautifulSoup(f, 'html.parser')

# Remove style, script, meta tags
for tag in soup(['style', 'script', 'meta', 'link']):
    tag.decompose()

text = soup.get_text('\n', strip=True)
# Collapse multiple blank lines
text = re.sub(r'\n{3,}', '\n\n', text)
# Write to file
with open('/tmp/design_doc.txt', 'w') as f:
    f.write(text)
print(f"Extracted {len(text)} chars")
