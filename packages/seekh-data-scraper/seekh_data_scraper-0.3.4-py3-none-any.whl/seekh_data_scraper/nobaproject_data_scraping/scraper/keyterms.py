import requests
from bs4 import BeautifulSoup
import pandas as pd
import seekh_data_scraper.nobaproject_data_scraping.noba_config as noba_config


def scrape_keyterms(topics_df):
    result_df = pd.DataFrame()
    for _, row in topics_df.iterrows():
        module_name = row[noba_config.TOPIC_COL]
        url = row[noba_config.LINK_COL]
        scraped_data = _scrape_vocabulary_data(url, module_name)
        if scraped_data is not None:
            result_df = pd.concat([result_df, scraped_data], ignore_index=True)
    return result_df

def _scrape_vocabulary_data(url, module_name):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        vocabulary_dl = soup.find("dl", class_="noba-chapter-vocabulary")
        if vocabulary_dl:
            dt_tags = vocabulary_dl.find_all("dt")
            dd_tags = vocabulary_dl.find_all("dd")
            if len(dt_tags) == len(dd_tags):
                data = {
                    noba_config.MODULE_NAME_COL: [module_name] * len(dt_tags),
                    noba_config.TERM_COL: [dt.text.strip() for dt in dt_tags],
                    noba_config.DEFINITION_COL: [dd.text.strip() for dd in dd_tags]
                }
                return pd.DataFrame(data)
    return None