import requests
from bs4 import BeautifulSoup
import re
from seekh_data_scraper.openstax_data_scraping.openstax_config import KEY_TERM, GROUP_2_TERMS

def group_urls(sitemap_urls):
    group_1_urls = []
    group_2_urls = []
    group_3_urls = []
    group_4_urls = []

    def extract_urls_from_sitemap(sitemap_url):
        response = requests.get(sitemap_url)
        soup = BeautifulSoup(response.content, "xml")
        loc_tags = soup.find_all("loc")
        for loc_tag in loc_tags:
            url = loc_tag.text.lower()
            if KEY_TERM.lower() in url:
                group_1_urls.append(loc_tag.text)
            elif any(term in url for term in GROUP_2_TERMS):
                group_2_urls.append(loc_tag.text)
            elif re.search(r"/chapter-\d+", url):
                group_4_urls.append(loc_tag.text)
            else:
                group_3_urls.append(loc_tag.text)

    for sitemap_url in sitemap_urls:
        extract_urls_from_sitemap(sitemap_url)

    return {
        'group_1': group_1_urls,
        'group_2': group_2_urls,
        'group_3': group_3_urls,
        'group_4': group_4_urls
    }