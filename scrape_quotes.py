import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import argparse
import logging
import time

# Base URL for the website
BASE_URL = "https://quotes.toscrape.com"

def scrape_page(page_url):
    response = requests.get(page_url)
    if response.status_code != 200:
        print(f"Failed to fetch {page_url}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    quote_elements = soup.find_all('div', class_='quote')
    quotes = []
    for element in quote_elements:
        text = element.find('span', class_='text').get_text(strip=True)
        author = element.find('small', class_='author').get_text(strip=True)
        tags = [tag.get_text(strip=True) for tag in element.find_all('a', class_='tag')]
        quotes.append({'Text': text, 'Author': author, 'Tags': ', '.join(tags)})

    return quotes

def scrape_quotes(output_file):
    all_quotes = []
    page_url = BASE_URL
    while page_url:
        print(f"Scraping: {page_url}")
        all_quotes.extend(scrape_page(page_url))

        soup = BeautifulSoup(requests.get(page_url).text, 'html.parser')
        next_button = soup.find('li', class_='next')
        page_url = BASE_URL + next_button.find('a')['href'] if next_button else None

    os.makedirs('dataset', exist_ok=True)
    df = pd.DataFrame(all_quotes)
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"Scraped {len(all_quotes)} quotes and saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape quotes and save to CSV.")
    parser.add_argument('-o', '--output', default='dataset/quotes.csv', help='Output CSV file path')
    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(filename='scraper.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    try:
        scrape_quotes(args.output)
        logging.info(f"Scraping completed. Data saved to {args.output}.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")

    # Optional: Introduce a delay between requests to avoid being blocked
    time.sleep(1)  # Sleep for 1 second between requests
