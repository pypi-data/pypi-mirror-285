from seekh_data_scraper.wikipedia_data_scraping.scraper.content import scrape_content_url, scrape_wikipedia_intro, scrape_see_also, scrape_images, save_data
from config import SCRAPING_MODULES


def main():
    for url in SCRAPING_MODULES['wikipedia']['site_url']:
        page_title, content_data = scrape_content_url(url)
        summary = scrape_wikipedia_intro(url)
        summary_data = {
            "url": url,
            "page_title": page_title,
            "summary": summary
        }

        see_also_data = scrape_see_also(url)
        
        image_data = scrape_images(url)

        save_data(page_title, content_data, summary_data, see_also_data, image_data)
        print(f"Data saved for: {page_title}")

if __name__ == "__main__":
    main()