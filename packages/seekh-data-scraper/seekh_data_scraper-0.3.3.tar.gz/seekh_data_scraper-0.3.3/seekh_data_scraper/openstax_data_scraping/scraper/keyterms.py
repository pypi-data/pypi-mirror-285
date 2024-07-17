import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_keywords(urls):
    term_data = []
    for url in urls:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        dt_tags = soup.find_all("dt")
        dl_tags = soup.find_all("dl")
        
        book_name = url.split("/")[-3]
        for dt_tag, dl_tag in zip(dt_tags, dl_tags):
            term = dt_tag.text.strip()
            definition = dl_tag.text.strip()
            term_data.append((book_name, term, definition))
    
    return pd.DataFrame(term_data, columns=["Book Name", "Term", "Definition"])
