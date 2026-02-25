import json
import re
from bs4 import BeautifulSoup
import uuid

def process_html():
    with open('/Users/jamelasmac/website/index.html', 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')
    
    # We want to find elements that likely contain text content that should be editable
    # e.g., headings, paragraphs, buttons, span inside links or buttons
    tags_to_check = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'span', 'a', 'button', 'li']
    
    content_map = {}
    counter = 1
    
    for tag in soup.find_all(tags_to_check):
        # Skip elements that are empty or just whitespace
        text = tag.string
        if text and text.strip():
            # Only process if it doesn't already have a data-content-id
            if not tag.has_attr('data-content-id'):
                content_id = f"txt-{counter:04d}"
                tag['data-content-id'] = content_id
                content_map[content_id] = {
                    "text": text.strip(),
                    "tag": tag.name
                }
                counter += 1

    # Inject the sync script before the closing body tag
    sync_script_tag = soup.new_tag('script', src='assets/sync.js')
    if soup.body:
        # Check if already injected
        existing = soup.find('script', src='assets/sync.js')
        if not existing:
            soup.body.append(sync_script_tag)

    # Save modified HTML
    with open('/Users/jamelasmac/website/index.html', 'w', encoding='utf-8') as f:
        f.write(str(soup))
        
    # Save content mapping
    with open('/Users/jamelasmac/website/content.json', 'w', encoding='utf-8') as f:
        json.dump(content_map, f, indent=4)
        
    print(f"Processed {counter - 1} text elements.")

if __name__ == '__main__':
    process_html()
