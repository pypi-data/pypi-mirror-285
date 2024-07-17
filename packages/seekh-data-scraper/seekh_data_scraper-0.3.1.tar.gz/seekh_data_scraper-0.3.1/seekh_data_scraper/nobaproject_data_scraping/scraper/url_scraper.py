import requests
from bs4 import BeautifulSoup
import pandas as pd
import seekh_data_scraper.nobaproject_data_scraping.noba_config as noba_config


def get_urls(base_url):
    response = requests.get(base_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        topics = []
        links = []
        ul_tags = soup.find_all("ul", class_="noba-list")
        for ul in ul_tags:
            li_tags = ul.find_all("li")
            for li in li_tags:
                topic = li.find("h2", class_="noba-list-title").text.strip()
                link = "https://nobaproject.com" + li.find("a", class_="link")["href"]
                topics.append(topic)
                links.append(link)
        return pd.DataFrame({noba_config.TOPIC_COL: topics, noba_config.LINK_COL: links})
    else:
        raise Exception(f"Failed to retrieve the web page. Status code: {response.status_code}")