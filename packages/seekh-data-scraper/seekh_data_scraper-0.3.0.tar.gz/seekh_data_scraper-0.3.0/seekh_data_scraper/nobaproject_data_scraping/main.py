# main.py for noba

import os
import pandas as pd
from seekh_data_scraper.nobaproject_data_scraping.scraper.url_scraper import get_urls
from seekh_data_scraper.nobaproject_data_scraping.scraper.content import scrape_content
from seekh_data_scraper.nobaproject_data_scraping.scraper.keyterms import scrape_keyterms
from seekh_data_scraper.nobaproject_data_scraping.scraper.questions import scrape_questions
import seekh_data_scraper.nobaproject_data_scraping.noba_config as noba_config
from config import SCRAPING_MODULES

def create_data_folder():
    """Create the data folder if it doesn't exist."""
    module_name = 'nobaproject'
    data_folder = os.path.join(module_name, 'data')
    os.makedirs(data_folder, exist_ok=True)
    return data_folder

def main():
    # Create data folder
    data_folder = create_data_folder()

    # Get URLs
    site_url = SCRAPING_MODULES['nobaproject']['site_url']
    topics_df = get_urls(site_url)

    # Scrape content
    content_df = scrape_content(topics_df)
    content_file = os.path.join(data_folder, noba_config.CONTENT_FILE)
    content_df.to_csv(content_file, index=False)
    print(f"Content saved to {content_file}")

    # Scrape keyterms
    keyterms_df = scrape_keyterms(topics_df)
    keyterms_file = os.path.join(data_folder, noba_config.KEYTERMS_FILE)
    keyterms_df.to_csv(keyterms_file, index=False)
    print(f"Keyterms saved to {keyterms_file}")

    # Scrape questions
    questions_df = scrape_questions(topics_df)
    questions_file = os.path.join(data_folder, noba_config.QUESTIONS_FILE)
    questions_df.to_csv(questions_file, index=False)
    print(f"Questions saved to {questions_file}")

if __name__ == "__main__":
    main()
