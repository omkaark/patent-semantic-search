import requests
from bs4 import BeautifulSoup
import concurrent.futures
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_links_from_sitemap(session):
    url = "https://patents.google.com/sitemap/"
    r = session.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    return [a['href'] for a in soup.find_all('a', href=True)]

def filter_links_by_year(links, year_set):
    return [link for link in links if any(str(year) in link for year in year_set)]

def get_detailed_patent_page_links(session, weekly_url):
    url = f"https://patents.google.com/sitemap/{weekly_url}"
    r = session.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    return [a['href'] for a in soup.find_all('a', href=True)]

def get_patent_links(session, detailed_page_url):
    r = session.get(f"https://patents.google.com/sitemap/{detailed_page_url}")
    soup = BeautifulSoup(r.content, 'html.parser')
    return [en_link['href'].split('/')[-2] for li in soup.find_all('li') if li.get_text(strip=True).startswith('US') and (en_link := li.find('a', string='en'))]

def write_links_to_file(file, links):
    for link in links:
        file.write(link + '\n')

def crawl_patents(start_year, end_year, file_path):
    year_set = set(range(start_year, end_year + 1))
    with requests.Session() as session:
        sitemap_links = fetch_links_from_sitemap(session)
        year_links = filter_links_by_year(sitemap_links, year_set)
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_url = {executor.submit(get_detailed_patent_page_links, session, weekly_url): weekly_url for weekly_url in year_links}
            for future in concurrent.futures.as_completed(future_to_url):
                detailed_page_urls = future.result()
                for detailed_page_url in detailed_page_urls:
                    patent_links = get_patent_links(session, detailed_page_url)
                    with open(file_path, 'a') as file:
                        write_links_to_file(file, patent_links)
                    logging.info(f"Links from {detailed_page_url} written to file.")

if __name__ == '__main__':
    start_year = int(input("Enter start year: "))
    end_year = int(input("Enter end year: "))
    file_path = f'run_artifacts/crawler-{start_year}-{end_year}.txt'
    crawl_patents(start_year, end_year, file_path)
    logging.info(f"Completed crawling. Data written to {file_path}")
