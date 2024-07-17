# main.py

import os
import pandas as pd
from seekh_data_scraper.openstax_data_scraping.scraper.url_grouper import group_urls
from seekh_data_scraper.openstax_data_scraping.scraper.keyterms import scrape_keywords
from seekh_data_scraper.openstax_data_scraping.scraper.content import scrape_content, save_content
from seekh_data_scraper.openstax_data_scraping.scraper.summary import scrape_summary, save_summary
from seekh_data_scraper.openstax_data_scraping.scraper.questions import scrape_group_2_urls
from seekh_data_scraper.openstax_data_scraping.openstax_config import (DEFAULT_KEYWORD_OUTPUT, DEFAULT_CONTENT_OUTPUT, DEFAULT_QUESTIONS_OUTPUT, DEFAULT_SUMMARY_OUTPUT)
from config import SCRAPING_MODULES

def get_book_name(url):
    return url.split('/')[-1].split('.')[0]

def create_book_directory(book_name):
    book_dir = os.path.join('data', book_name)
    os.makedirs(book_dir, exist_ok=True)
    return book_dir

def check_file_exists(book_dir, filename):
    return os.path.exists(os.path.join(book_dir, filename))

def main():
    for sitemap_url in SCRAPING_MODULES['openstax']['site_url']:
        book_name = get_book_name(sitemap_url)
        book_dir = create_book_directory(book_name)
    
        url_groups = group_urls([sitemap_url])
        
        # Check and scrape keywords
        keyword_output = os.path.join(book_dir, DEFAULT_KEYWORD_OUTPUT)
        if not check_file_exists(book_dir, DEFAULT_KEYWORD_OUTPUT):
            keywords_df = scrape_keywords(url_groups['group_1'])
            keywords_df.to_csv(keyword_output, index=False)
            print(f"Keywords saved to {keyword_output}")
        else:
            print(f"Keywords file already exists for {book_name}")
        
        # Check and scrape content
        content_output = os.path.join(book_dir, DEFAULT_CONTENT_OUTPUT)
        if not check_file_exists(book_dir, DEFAULT_CONTENT_OUTPUT):
            content_data, summary_urls = scrape_content(url_groups['group_3'])
            save_content(content_data, content_output)
            print(f"Content saved to {content_output}")
        else:
            print(f"Content file already exists for {book_name}")
            # We still need summary_urls for later, so let's get them without scraping content
            _, summary_urls = scrape_content(url_groups['group_3'], scrape=False)
        
        # Check and scrape questions
        questions_output = os.path.join(book_dir, DEFAULT_QUESTIONS_OUTPUT)
        if not check_file_exists(book_dir, DEFAULT_QUESTIONS_OUTPUT):
            questions_df = scrape_group_2_urls(url_groups['group_2'])
            questions_df.to_csv(questions_output, index=False)
            print(f"Questions saved to {questions_output}")
        else:
            print(f"Questions file already exists for {book_name}")
        
        # Check and scrape summaries
        summary_output = os.path.join(book_dir, DEFAULT_SUMMARY_OUTPUT)
        if not check_file_exists(book_dir, DEFAULT_SUMMARY_OUTPUT):
            summary_data = scrape_summary(summary_urls + url_groups['group_4'])
            save_summary(summary_data, summary_output)
            print(f"Summary saved to {summary_output}")
        else:
            print(f"Summary file already exists for {book_name}")
        
        print(f"All data for {book_name} has been checked/scraped and saved.")

if __name__ == "__main__":
    main()