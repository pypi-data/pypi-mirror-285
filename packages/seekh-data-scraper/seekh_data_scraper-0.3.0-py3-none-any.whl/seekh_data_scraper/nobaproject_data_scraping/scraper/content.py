import requests
from bs4 import BeautifulSoup
import pandas as pd
import seekh_data_scraper.nobaproject_data_scraping.noba_config as noba_config

def scrape_content(topics_df):
    result_df = pd.DataFrame()
    for _, row in topics_df.iterrows():
        module_name = row[noba_config.TOPIC_COL]
        url = row[noba_config.LINK_COL]
        scraped_data = _scrape_data(url, module_name)
        if scraped_data is not None:
            result_df = pd.concat([result_df, scraped_data], ignore_index=True)
    return result_df

def _scrape_data(url, module_name):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        content_section = soup.find("section", class_="content")
        if content_section:
            h1_texts, p_texts = [], []
            for element in content_section:
                if element.name == "h1":
                    h1_texts.append(element.text.strip())
                    p_texts.append([])
                elif element.name == "p":
                    if h1_texts:
                        p_texts[-1].append(element.text.strip())
                elif element.name == "ol":
                    if h1_texts:
                        p_texts[-1].extend([li.text.strip() for li in element.find_all("li")])
            data = []
            for h1, p_list in zip(h1_texts, p_texts):
                for p in p_list:
                    data.append({noba_config.MODULE_NAME_COL: module_name, noba_config.H1_COL: h1, noba_config.P_COL: p})
            return pd.DataFrame(data)
    return None