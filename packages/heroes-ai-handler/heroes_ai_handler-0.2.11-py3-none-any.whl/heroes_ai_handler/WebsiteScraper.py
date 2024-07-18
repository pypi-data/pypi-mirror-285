import requests
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import undetected_chromedriver as uc
import time
import urllib.parse

from .FileHandler import FileHandler
from .DatabaseHandler import DatabaseHandler
from .Logger import Logger


LOGGER = Logger(
    name='WebsiteScraper',
    log_to_console=True,
)


class WebsiteScraper:
    def __init__(
            self,
            driver_method: str = 'requests',  # ['requests', 'selenium']
        ):
        self.driver_method = driver_method

        self.url_history = []
        self.output = []
        self.n_urls_scraped = 0

        if driver_method == 'selenium':
            self.setup_selenium()


    def append_to_urls_queue(
            self, 
            urls
        ):
        urls = list(urls)
        for url in urls:
            if url not in self.urls_queue and url not in self.url_history:
                self.urls_queue.append(url)


    def start_from_urls(
            self, 
            urls: list,
            dir_dst: str,
            file_handler: FileHandler,
            database_handler: DatabaseHandler,
            n_urls_scraped_max: int = None,
            clear_output_folder: bool = False,
            truncate_db_table_webpages: bool = False,
        ):
        # Clear output folder if desired
        if clear_output_folder:
            file_handler.delete_blobs_in_folder(dir_dst)

        # Clear output table if desired
        if truncate_db_table_webpages:
            database_handler.truncate_table('Webpages')

        self.urls_queue = urls
        self.n_urls_scraped_max = len(urls) if n_urls_scraped_max is None else n_urls_scraped_max

        LOGGER.info('>> Start scraping')

        while self.urls_queue:
            try:
                LOGGER.info('')
                LOGGER.info(f'> url [ {len(self.url_history) + 1} / {self.n_urls_scraped_max} ]')

                # Get next url from queue
                url = self.urls_queue[0]
                self.urls_queue.pop(0)

                # Scrape webpage
                scrape_succesful, url_redirected, raw_html = self.scrape_webpage(url)
                self.url_history.append(url)
                self.n_urls_scraped += 1
                
                # Get text from webpage when scrape was succesful
                text = ''
                if scrape_succesful == True:
                    # Append urls to the queue that have not been visited yet
                    unique_urls = self.get_all_unique_urls_from_webpage(url, raw_html)
                    self.append_to_urls_queue(unique_urls)

                    # Get all text from a webpage
                    text = self.get_text_from_webpage(raw_html)

                self.save_content_individual_webpage(url, url_redirected, scrape_succesful, text, dir_dst, file_handler, database_handler)

                LOGGER.info(f'Queue length: {len(self.urls_queue)}')

                # Break immidiately out of loop if the queue is empty
                if self.n_urls_scraped == self.n_urls_scraped_max:
                    LOGGER.info(f'Breaking loop: n_urls_scraped_max ({self.n_urls_scraped_max}) reached.')
                    break

            except Exception as e:
                LOGGER.error(f'Failed: {e}')

        if not self.urls_queue:
            LOGGER.info('Breaking loop: url queue is empty.')

        LOGGER.info('>> Finished scraping')


    def save_content_individual_webpage(
            self,
            url: str,
            url_redirected: str,
            scrape_succesful: bool,
            text: str,
            dir_dst: str,
            file_handler: FileHandler,
            database_handler: DatabaseHandler,
        ):

        # Generate output location
        id = database_handler.generate_id(url)
        file_path_dst = os.path.join(dir_dst, id + '.txt') if scrape_succesful else None

        # Upload to blob storage
        file_handler.upload_to_blob_storage(file_path_dst, text)

        # Upload to Database
        database_handler.upload_to_database_webpages(id, url, url_redirected, scrape_succesful, file_path_dst)


    def get_text_from_webpage(
            self, 
            raw_html: str
        ):
        soup = BeautifulSoup(raw_html, 'html.parser')
        text = soup.get_text()
        
        # Clean up the text by splitting it into lines, stripping whitespace, and joining the lines
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        cleaned_text = '\n'.join(chunk for chunk in chunks if chunk)

        return cleaned_text


    def scrape_webpage(
            self, 
            url: str,
            page_wait: float = 1.0,
        ):
        LOGGER.info(f'Going to url: {url}')
        
        if self.driver_method == 'requests':
            response = requests.get(url)
            status_code = response.status_code
            url_redirected = response.url
            time.sleep(page_wait)

            if status_code == 200:
                scrape_succesful = True
                raw_html = response.text
            else:
                scrape_succesful = False
                url_redirected = url
                raw_html = None

        if self.driver_method == 'selenium':
            try:
                self.driver.get(url)
                time.sleep(page_wait)

                scrape_succesful = True
                url_redirected = self.driver.current_url
                raw_html = self.driver.page_source
            except:
                scrape_succesful = False
                url_redirected = url
                raw_html = None

        LOGGER.info('Scrape succesful' if scrape_succesful else 'Scrape FAILED')

        return scrape_succesful, url_redirected, raw_html


    def get_all_unique_urls_from_webpage(
            self, 
            url: str, 
            raw_html: str
        ):
        soup = BeautifulSoup(raw_html, 'html.parser')

        unique_urls = set()
        url_netloc = urllib.parse.urlparse(url).netloc

        # Find all anchor tags with href attributes
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            # Resolve relative URLs
            full_url = urljoin(url, href)
            if url_netloc == urllib.parse.urlparse(full_url).netloc:
                unique_urls.add(full_url)
        
        return unique_urls


    def setup_selenium(
            self,
        ):
        try:
            LOGGER.info('Setting up Selenium driver')
            browser_width = 1000
            browser_height = 1000

            # Set up the Selenium webdriver
            options = uc.ChromeOptions()
            options.add_argument('--headless')
            driver = uc.Chrome(options=options)
            
            # Adjust window size
            driver.set_window_size(browser_width, browser_height)
            # Move window to upper left of screen
            driver.set_window_position(0, 0)
            self.driver = driver
            # return driver

        except Exception as e:
            LOGGER.error(f'Failed: {e}')