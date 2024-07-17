import requests
from bs4 import BeautifulSoup
import pandas as pd
import seekh_data_scraper.nobaproject_data_scraping.noba_config as noba_config


def scrape_questions(topics_df):
    result_df = pd.DataFrame()
    for _, row in topics_df.iterrows():
        module_name = row[noba_config.TOPIC_COL]
        url = row[noba_config.LINK_COL]
        scraped_data = _scrape_discussion_questions(url, module_name)
        if scraped_data is not None:
            result_df = pd.concat([result_df, scraped_data], ignore_index=True)
    return result_df

def _scrape_discussion_questions(url, module_name):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        h1_discussion = soup.find("h2", id="discussion-questions")
        if h1_discussion:
            li_tags = h1_discussion.find_next("ol").find_all("li")
            data = {
                noba_config.MODULE_NAME_COL: [module_name] * len(li_tags),
                noba_config.QUESTION_COL: [li.text.strip() for li in li_tags]
            }
            return pd.DataFrame(data)
    return None