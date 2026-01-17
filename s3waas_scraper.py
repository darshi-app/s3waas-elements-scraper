import requests
from bs4 import BeautifulSoup
import json
import time
import urllib3
import re
from urllib.parse import urljoin

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_tab_content(soup, tab_names):
    """
    Finds content containers based on tab links matching specifically provided names.
    """
    found_content = {}
    
    # Normalize tab names for matching
    # We will check if any of our target keywords are in the link text
    
    # Find all anchors that might be tabs
    all_links = soup.find_all('a', href=True)
    
    for link in all_links:
        text = link.get_text(strip=True).lower()
        if not text: continue
        
        # Check if this link matches any of our target categories
        # using a regex search for better partial matching
        matched_category = None
        for cat in tab_names:
            if cat in text:
                matched_category = cat
                break
        
        if matched_category:
            target_id = link['href']
            
            # Ensure it's an internal ID link
            clean_id = None
            if target_id.startswith('#') and len(target_id) > 1:
                clean_id = target_id[1:] 
            elif '#' in target_id:
                clean_id = target_id.split('#')[1]
                
            if clean_id:
                content_div = soup.find(id=clean_id)
                
                if content_div:
                    items = []
                    
                    # Find all relevant links in this container
                    content_links = content_div.find_all('a', href=True)
                    
                    for item_link in content_links:
                        item_text = item_link.get_text(" ", strip=True)
                        item_url = item_link['href']
                        
                        # Filter noise
                        if item_text and len(item_text) > 3 and "read more" not in item_text.lower():
                            items.append({
                                "text": item_text,
                                "url": item_url
                            })
                    
                    # Store data
                    display_key = matched_category.title()
                    
                    if items:
                        if display_key not in found_content:
                             found_content[display_key] = items
                        else:
                            found_content[display_key].extend(items)

    return found_content

def resolve_pdf_link(session, base_url, link_url):
    """
    Visits a link to see if it leads to a PDF or a page containing a PDF.
    Returns the resolved PDF URL if found, otherwise None.
    """
    # 1. Check if the link itself is a document
    doc_exts = ('.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip')
    if link_url.lower().endswith(doc_exts):
        return link_url

    # 2. If it's a webpage, visit it to find the doc
    full_url = urljoin(base_url, link_url)
    try:
        # Polite delay for deep scraping
        time.sleep(0.5) 
        
        # Print for feedback
        # print(f"  Resolving: {full_url}")
        
        resp = session.get(full_url, verify=False, timeout=10)
        if resp.status_code == 200:
            sub_soup = BeautifulSoup(resp.content, 'html.parser')
            
            # Strategy: Look for "View" / "Download" links or any PDF link
            # Priority 1: Anchors with class 'icon-pdf' or similar which S3WaaS uses
            pdf_link = sub_soup.find('a', href=True, string=re.compile(r'View|Download', re.I))
            
            if not pdf_link:
                 # Priority 2: Any link ending in .pdf
                 pdf_link = sub_soup.find('a', href=re.compile(r'\.pdf$', re.I))
                 
            if pdf_link:
                return urljoin(full_url, pdf_link['href'])
                
    except Exception as e:
        # print(f"  Failed to resolve {full_url}: {e}")
        pass
        
    return None

def scrape_site(url):
    print(f"Scraping {url}...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    session = requests.Session()
    session.headers.update(headers)
    
    try:
        response = session.get(url, verify=False, timeout=20)
        if response.status_code != 200:
             print(f"Failed to load {url}: Status {response.status_code}")
             return {"error": f"Status {response.status_code}"}

        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Expanded keywords from user request
        categories = [
            "notice", "notification", "announcement", "tender", "contract", 
            "circular", "order", "vacancy", "recruitment", "press", "release", 
            "news", "update", "latest", "award", "bid"
        ]
        
        site_data = get_tab_content(soup, categories)
        
        # Post-processing: Deep Scraping to resolve PDFs
        for cat, items in site_data.items():
            print(f"  Processing {len(items)} items in {cat}...")
            count = 0
            for item in items:
                # Limit resolution to first 5 items per category per site to avoid huge delay during testing
                if count > 5: break 
                count += 1
                
                # Ensure absolute URL for the item first
                if not item['url'].startswith('http'):
                    item['url'] = urljoin(url, item['url'])
                
                # Try to resolve actual PDF
                pdf_url = resolve_pdf_link(session, url, item['url'])
                if pdf_url:
                    item['pdf_url'] = pdf_url
                    
        return site_data

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return {"error": str(e)}

def main():
    input_file = 'e:/darshi/s3waas-elements-scraper/s3waas_urls.json'
    output_file = 'e:/darshi/s3waas-elements-scraper/scraped_content.json'
    
    try:
        with open(input_file, 'r') as f:
            urls_data = json.load(f)
    except Exception as e:
        print(f"Could not read input file: {e}")
        return
        
    # Handle data format 
    urls = []
    if isinstance(urls_data, list):
        for item in urls_data:
            if isinstance(item, str):
                urls.append(item)
            elif isinstance(item, dict):
                urls.append(item.get('url', item.get('link', '')))
    elif isinstance(urls_data, dict):
         urls = list(urls_data.values())

    results = {}
    
    print(f"Starting Deep Scrape for {len(urls)} sites...")
    
    for url in urls:
        if not url: continue
        
        if not url.startswith('http'):
            url = 'https://' + url
            
        try:
            name = url.split('//')[1].split('.')[0].title()
        except:
            name = url
            
        data = scrape_site(url)
        results[name] = {
            "url": url,
            "data": data
        }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4)
        
    print(f"Deep Scraping complete. Saved to {output_file}")

if __name__ == "__main__":
    main()
