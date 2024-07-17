import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import csv
from seekh_data_scraper.wikipedia_data_scraping.wikipedia_config import BASE_DIR

def scrape_content_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    page_title = soup.find("title").text.strip()  
    page_title = page_title.replace(" - Wikipedia", "")

    content_div = soup.find("div", {"id": "mw-content-text"})

    titles_to_skip = set([
        "Alternative theories", "References", "Further reading", "Additional Reading",
        "External links", "Footnotes", "See also", "Scientific journals",
        "Citations", "Common subfields", "Sources", "Journals",
        "Explanatory notes", "Sources", "Applied fields", "Notes", "Bibliography",
        "International relations", "Historical publication",
        "Notable cell biologists", "Conferences", "Modern references",
        "Books", "Awards", "Gallery", "Notes and references", "Historical references"
    ])

    content_data = []
    current_subtitle = None

    for element in content_div.find_all(["h2", "h3", "p", "ul"]):
        if element.name in ["h2", "h3"]:
            heading_text = element.find("span", class_="mw-headline").text
            if heading_text not in titles_to_skip:
                current_subtitle = heading_text
        elif element.name == "p" or element.name == "ul":
            if current_subtitle:
                content = element.get_text(strip=True)
                content_data.append({
                    "url": url,
                    "content": content,
                    "topic": current_subtitle
                })

    return page_title, content_data

def scrape_wikipedia_intro(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        body_content = soup.find('div', class_='mw-body-content')
        scraped_content = ""
        for p in body_content.find_all('p'):
            formatted_parts = []
            for part in p.contents:
                if part.name in ['a', 'b', 'i']:
                    formatted_parts.append(part.get_text())
                elif part.name not in ['sup', 'span', 'small']:
                    formatted_parts.append(str(part))
            scraped_content += ''.join(formatted_parts)
            next_sibling = p.find_next_sibling()
            if next_sibling and next_sibling.find('span', class_='mw-headline'):
                break
        return scraped_content
    return ""

def scrape_see_also(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        see_also_h2 = soup.find("span", class_="mw-headline", text="See also")
        if see_also_h2:
            ul_tag = see_also_h2.find_next("ul")
            if ul_tag:
                see_also_data = []
                li_tags = ul_tag.find_all("li")
                for li_tag in li_tags:
                    a_tag = li_tag.find("a")
                    if a_tag:
                        link_text = a_tag.get_text()
                        href = a_tag.get("href")
                        full_url = "https://en.wikipedia.org" + href
                        see_also_data.append({"title": link_text, "href": full_url})
                return see_also_data
    return None

def save_data(page_title, content_data, summary_data, see_also_data, image_data):
    # Create directory for this page
    page_dir = os.path.join(BASE_DIR, page_title)
    os.makedirs(page_dir, exist_ok=True)

    # Save content.csv
    with open(os.path.join(page_dir, 'content.csv'), 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["url", "content", "topic"])
        writer.writeheader()
        writer.writerows(content_data)

    # Save summary.csv
    pd.DataFrame([summary_data]).to_csv(os.path.join(page_dir, 'summary.csv'), index=False)

    # Save see_also_links.csv
    if see_also_data:
        with open(os.path.join(page_dir, 'see_also_links.csv'), 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["title", "href"])
            writer.writeheader()
            writer.writerows(see_also_data)

    # Save images.csv
    if image_data:
        pd.DataFrame(image_data).to_csv(os.path.join(page_dir, 'images.csv'), index=False)

def scrape_images(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        images = soup.find_all('img')
        image_data = []
        for img in images:
            src = img.get('src', '')
            if src.startswith('//'):
                src = 'https:' + src
            alt = img.get('alt', '')
            image_data.append({
                'src': src,
                'alt': alt
            })
        return image_data
    return []