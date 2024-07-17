import requests
from bs4 import BeautifulSoup
import json
from seekh_data_scraper.openstax_data_scraping.openstax_config import SKIP_TITLES

def scrape_summary_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    data_list = []
    
    summary_sections = soup.find_all('section', class_='summary')
    
    book_name = url.split("/")[4]
    last_part_of_url = url.split("/")[-1]
    
    for summary_section in summary_sections:
        # Extract the title
        title_element = summary_section.find('h2', {'data-type': 'document-title'})
        if title_element:
            title = title_element.find('span', class_='os-text').text.strip()
        else:
            title = "Summary"  # fallback title if not found
        
        # Extract paragraphs
        paragraphs = summary_section.find_all('p')
        
        para_texts = [p.text.strip() for p in paragraphs if p.text.strip()]
        
        if para_texts:
            data_list.append({
                "url": url,
                "book_name": book_name,
                "main_topic": last_part_of_url,
                "title": title,
                "paragraphs": para_texts
            })
    
    return data_list

def scrape_summary(urls):
    all_data = []
    for url in urls:
        summary_data_json = scrape_summary_page(url)
        all_data.extend(summary_data_json)
    
    merged_data = {}
    for data in all_data:
        main_topic = data["main_topic"]
        if main_topic not in merged_data:
            merged_data[main_topic] = {"data": {}, "url": data["url"], "book_name": data["book_name"], "main_topic": main_topic}
        
        title = data["title"]
        if title not in merged_data[main_topic]["data"]:
            merged_data[main_topic]["data"][title] = []
        
        merged_data[main_topic]["data"][title].extend(data["paragraphs"])
    
    # Convert the data dict back to a list format
    for main_topic in merged_data:
        merged_data[main_topic]["data"] = [{"title": title, "paragraphs": paragraphs} 
                                           for title, paragraphs in merged_data[main_topic]["data"].items()]
    
    return list(merged_data.values())

def save_summary(data, output_file):
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    print(f"Summary data saved to {output_file}")