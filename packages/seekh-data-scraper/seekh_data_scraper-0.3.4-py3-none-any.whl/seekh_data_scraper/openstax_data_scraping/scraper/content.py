import requests
from bs4 import BeautifulSoup
import pandas as pd
from config import TERMS_TO_REMOVE, ADDITIONAL_SUMMARY_TERMS, SKIP_TITLES

def filter_urls(urls):
    filtered_urls = [url for url in urls if not any(url.lower().endswith(term) for term in TERMS_TO_REMOVE)]
    summary_urls = [url for url in urls if "summary" in url.lower() or any(term in url.lower() for term in ADDITIONAL_SUMMARY_TERMS)]
    return filtered_urls, summary_urls

def scrape_url_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    
    chapter_content = soup.find('div', class_="chapter-content-module")
    if not chapter_content:
        return None
    
    data_list = []
    seen_paragraphs = set()
    
    def extract_title(element):
        span = element.find('span', class_='os-subtitle-label')
        return span.get_text(strip=True) if span else element.get_text(strip=True)
    
    def add_unique_paragraphs(title, paragraphs):
        for p in paragraphs:
            if p["text"] not in seen_paragraphs:
                seen_paragraphs.add(p["text"])
                data_list.append({
                    "title": title,
                    "paragraph": p["text"],
                    "index": p["index"]
                })
    
    current_title = ""
    current_paragraphs = []
    
    for element in chapter_content.find_all(['h2', 'h3', 'p', 'div']):
        if element.name in ['h2', 'h3']:
            if element.text.strip() == "Link to Learning":
                continue
            
            if current_title and current_paragraphs:
                add_unique_paragraphs(current_title, current_paragraphs)
                current_paragraphs = []
            
            current_title = extract_title(element)
        
        elif element.name == 'p':
            term_span = element.find('span', {'data-type': 'term'})
            term_text = term_span.get_text(strip=True) if term_span else None
            current_paragraphs.append({
                "text": element.text.strip(),
                "index": term_text
            })
        
        elif element.name == 'div' and element.get('data-type') == 'note':
            if current_title and current_paragraphs:
                add_unique_paragraphs(current_title, current_paragraphs)
                current_paragraphs = []
            
            note_title = element.find('h2', class_='os-title')
            note_subtitle = element.find('h3', class_='os-subtitle')
            note_paragraphs = []
            
            if note_title and note_title.text.strip() != "Link to Learning":
                current_title = extract_title(note_title)
                if note_subtitle:
                    current_title += f": {extract_title(note_subtitle)}"
                
                for p in element.find_all('p'):
                    term_span = p.find('span', {'data-type': 'term'})
                    term_text = term_span.get_text(strip=True) if term_span else None
                    note_paragraphs.append({
                        "text": p.text.strip(),
                        "index": term_text
                    })
                
                add_unique_paragraphs(current_title, note_paragraphs)
            
            current_title = ""
    
    # Add the last section if it exists
    if current_title and current_paragraphs:
        add_unique_paragraphs(current_title, current_paragraphs)
    
    book_name = url.split("/")[4]
    last_part_of_url = url.split("/")[-1]
    data_dict = {
        "url": url,
        "book_name": book_name,
        "main_topic": last_part_of_url,
        "data": data_list
    }
    return data_dict

def scrape_content(urls, scrape=True):
    if not scrape:
        # If scrape is False, return empty data and summary URLs
        filtered_urls, summary_urls = filter_urls(urls)
        return [], summary_urls

    filtered_urls, summary_urls = filter_urls(urls)
    all_data = []
    for url in filtered_urls:
        content_data_json = scrape_url_data(url)
        if content_data_json:
            all_data.append(content_data_json)
        else:
            print(f"Warning: No content found for URL {url}")
    return all_data, summary_urls

def save_content(data, output_file):
    rows = []
    for item in data:
        if "data" not in item:
            print(f"Warning: 'data' key not found in item: {item}")
            continue
        for entry in item["data"]:
            rows.append({
                "Book Name": item["book_name"],
                "URL": item["url"],
                "Main Topic": item["main_topic"],
                "Title": entry["title"],
                "Paragraph": entry["paragraph"],
                "Index": entry["index"]
            })
    
    df = pd.DataFrame(rows)
    df.to_csv(output_file, index=False, encoding="utf-8")
    print(f"Scraped content saved to {output_file}")