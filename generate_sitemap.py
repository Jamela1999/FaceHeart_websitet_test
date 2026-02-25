import json
import re
import os
import urllib.request
from bs4 import BeautifulSoup

BASE_URL = "https://next-sass-html.vercel.app"
DIR_PATH = "/Users/jamelasmac/website"

# Mapping human-readable page names to files
PAGE_NAMES = {
    "index.html": "Home Page",
    "digital-marketing.html": "Digital Marketing Home",
    "digital-marketing-about.html": "About Us",
    "digital-marketing-services.html": "Our Services",
    "digital-marketing-features.html": "Product Features",
    "digital-marketing-blog.html": "Blog & News",
    "digital-marketing-blog-details.html": "Blog Details",
    "digital-marketing-affiliates.html": "Affiliate Program",
    "digital-marketing-referral-program.html": "Referral Program",
    "digital-marketing-login.html": "Login",
    "digital-marketing-signup.html": "Sign Up",
    "digital-marketing-download.html": "Download",
    "digital-marketing-integration.html": "Integration",
    "digital-marketing-documentation.html": "Documentation",
    "digital-marketing-tutorial.html": "Tutorials",
    "digital-marketing-faq.html": "FAQ",
    "digital-marketing-case-study.html": "Case Studies",
    "digital-marketing-career.html": "Careers",
    "digital-marketing-contact.html": "Contact Us",
    "digital-marketing-error.html": "Error 404",
    "digital-marketing-pricing.html": "Pricing",
    "digital-marketing-terms.html": "Terms & Conditions",
    "digital-marketing-privacy.html": "Privacy Policy"
}

def download_missing_pages():
    print("Checking for missing pages...")
    # Read index.html to find linked pages
    index_path = os.path.join(DIR_PATH, 'index.html')
    if not os.path.exists(index_path):
        print(f"File {index_path} not found.")
        return []

    with open(index_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    pages_to_process = set(['index.html'])
    
    # Also add known pages from nav
    for a in soup.find_all('a', href=True):
        href = a['href']
        if href.endswith('.html') and not href.startswith('http'):
            # clean hash
            href = href.split('#')[0]
            if href:
                pages_to_process.add(href)
                PAGE_NAMES.setdefault(href, href.replace('.html', '').replace('-', ' ').title())
            
    # Also ensure we download pages in PAGE_NAMES
    for page in PAGE_NAMES.keys():
        pages_to_process.add(page)
                
    local_pages = []
    for page in pages_to_process:
        local_path = os.path.join(DIR_PATH, page)
        if not os.path.exists(local_path):
            url = f"{BASE_URL}/{page}"
            try:
                print(f"Downloading {page}...")
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req) as response:
                    html = response.read().decode('utf-8')
                    with open(local_path, 'w', encoding='utf-8') as f:
                        f.write(html)
                    local_pages.append(page)
            except Exception as e:
                print(f"Failed to download {page}: {e}")
        else:
            local_pages.append(page)
            
    return local_pages

def get_section_name(element):
    """Attempt to find a semantic wrapper parent for grouping."""
    curr = element.parent
    for _ in range(5): # Go up to 5 levels
        if not curr or curr.name == 'body':
            break
        # Semantic tags
        if curr.name in ['header', 'footer', 'nav']:
            return curr.name.title()
        if curr.name == 'section':
            cls = curr.get('class', [])
            if cls:
                return f"Section: {' '.join(cls[:2]).title()}"
            return "General Section"
        # Common structural classes or IDs
        cls = curr.get('class', [])
        if any(c in ['hero', 'banner', 'pricing', 'features', 'testimonial', 'faq'] for c in cls):
            return " ".join([c.title() for c in cls if c in ['hero', 'banner', 'pricing', 'features', 'testimonial', 'faq']])
        
        curr = curr.parent
        
    return "Main Body"

def process_html_pages(pages):
    tags_to_check = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'span', 'button', 'li', 'a', 'label', 'strong', 'em', 'b', 'i']
    
    # New structured map
    # content_map = { "Page Name": { "Section Name": { "txt-0001": { "text": "Hello", "tag": "h1" } } } }
    grouped_content_map = {}
    flat_id_set = set() # Avoid global ID duplicates
    
    counter = 1
    
    for page in pages:
        local_path = os.path.join(DIR_PATH, page)
        if not os.path.exists(local_path):
            continue
            
        with open(local_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
            
        page_title_readable = PAGE_NAMES.get(page, page)
        if page_title_readable not in grouped_content_map:
            grouped_content_map[page_title_readable] = {}
        
        for tag in soup.find_all(tags_to_check):
            # Skip if it is purely empty or a script inside
            if tag.find('script'): continue
            
            # Simple text node check to avoid grabbing giant wrapper spans
            # We want elements that contain mostly text
            text = tag.get_text(separator=' ', strip=True)
            if not text or len(text) > 300: # ignore massive text blocks probably an error
                continue
                
            # If no actual non-whitespace text directly inside or in children, ignore
            if text.strip():
                # Avoid assigning an ID to a parent if any child is also a valid tag with text
                has_valid_child = False
                for child in tag.find_all(tags_to_check):
                    if child.get_text(separator=' ', strip=True):
                        has_valid_child = True
                        break
                if has_valid_child:
                    continue

                content_id = tag.get('data-content-id')
                if not content_id:
                    content_id = f"txt-{counter:04d}"
                    tag['data-content-id'] = content_id
                    counter += 1
                elif content_id in flat_id_set:
                    # Regenerate if duplicated across pages
                    content_id = f"txt-{counter:04d}"
                    tag['data-content-id'] = content_id
                    counter += 1
                    
                flat_id_set.add(content_id)
                
                section_name = get_section_name(tag)
                
                if section_name not in grouped_content_map[page_title_readable]:
                    grouped_content_map[page_title_readable][section_name] = {}
                    
                grouped_content_map[page_title_readable][section_name][content_id] = {
                    "text": text,
                    "tag": tag.name,
                    "file": page
                }
                
        # Inject the sync scripts
        firebase_scripts = [
            ('script', {'src': 'https://www.gstatic.com/firebasejs/8.10.1/firebase-app.js'}),
            ('script', {'src': 'https://www.gstatic.com/firebasejs/8.10.1/firebase-database.js'}),
            ('script', {'src': 'assets/firebase-config.js'}),
            ('script', {'src': 'assets/sync.js'}),
        ]
        
        if soup.body:
            for tag_name, attrs in firebase_scripts:
                if not soup.find(tag_name, attrs):
                    new_tag = soup.new_tag(tag_name, **attrs)
                    soup.body.append(new_tag)
                    
        # Replace hrefs to next-sass-html.vercel.app with local
        for a in soup.find_all('a', href=True):
            if 'next-sass-html.vercel.app/' in a['href']:
                href = a['href'].replace('https://next-sass-html.vercel.app/', '')
                if href == '': href = 'index.html'
                a['href'] = href

        # Save back HTML
        print(f"Saving modified {page}...")
        with open(local_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))
            
    # Write the master JSON
    json_path = os.path.join(DIR_PATH, 'content.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(grouped_content_map, f, indent=4)
        
    print(f"Extraction complete! Formatted {counter - 1} text elements.")

if __name__ == "__main__":
    local_pages = download_missing_pages()
    process_html_pages(local_pages)
