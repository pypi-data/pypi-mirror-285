import os
import gzip
import logging
import pandas as pd
from warcio.archiveiterator import ArchiveIterator
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
import html
from urllib.parse import urlparse

# Setup logging to track progress and errors
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_warc(file_path):
    """
    Parses a WARC file and extracts titles and text content from HTML responses.
    
    Parameters:
    file_path (str): Path to the WARC file.

    Returns:
    list: A list of dictionaries containing the filename, title, text content, and URL.
    """
    records = []
    try:
        with gzip.open(file_path, 'rb') as stream:
            for record in ArchiveIterator(stream):
                warc_type = record.rec_headers.get_header('WARC-Type')
                logging.debug(f"Processing record with WARC-Type: {warc_type}")
                if record.rec_type == 'response':  # Process only response records
                    try:
                        http_headers = record.http_headers
                        if http_headers is None:
                            logging.warning(f"No HTTP headers found for record with WARC-Type: {warc_type} in file {file_path}")
                            logging.debug(f"Record headers: {record.rec_headers.headers}")
                            continue
                        status_code = http_headers.get_statuscode()
                        if status_code == '200':  # Process only successful responses
                            content_type = http_headers.get_header('Content-Type')
                            if content_type and 'text/html' in content_type:  # Process only HTML content
                                payload = record.content_stream().read().decode('utf-8', errors='ignore')
                                title = extract_title(payload)
                                text_content = extract_text_content(payload)
                                url = record.rec_headers.get_header('WARC-Target-URI')
                                if text_content and not fail_qa_check(text_content, url):
                                    records.append({
                                        'filename': os.path.basename(file_path),
                                        'title': title,
                                        'web_text_content': text_content,
                                        'url': url
                                    })
                                logging.debug(f"Processed record with URL: {url}, Title: {title}")
                            else:
                                logging.debug(f"Skipped non-HTML content type: {content_type}")
                        else:
                            logging.debug(f"Skipped non-200 status code: {status_code}")
                    except Exception as e:
                        logging.error(f"Error processing record in file {file_path}: {e}")
                else:
                    logging.debug(f"Skipped non-response record with WARC-Type: {warc_type}")
    except Exception as e:
        logging.error(f"Error processing file {file_path}: {e}")
    logging.info(f"Parsed {len(records)} records from file {file_path}")
    return records

def extract_title(html_content):
    """
    Extracts the title from HTML content and decodes HTML entities.

    Parameters:
    html_content (str): HTML content as a string.

    Returns:
    str: Extracted title or None if not found.
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        if soup.title and soup.title.string:
            return html.unescape(soup.title.string.strip())
    except Exception as e:
        logging.error(f"Error extracting title: {e}")
    return None

def extract_text_content(html_content):
    """
    Extracts text content from HTML, removing script and style elements.

    Parameters:
    html_content (str): HTML content as a string.

    Returns:
    str: Extracted text content.
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        for script in soup(['script', 'style']):  # Remove script and style elements
            script.decompose()
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        return text
    except Exception as e:
        logging.error(f"Error extracting text content: {e}")
    return None

def normalize_url(url):
    """
    Normalizes a URL by stripping common variants to determine if URLs are the same.

    Parameters:
    url (str): The URL to normalize.

    Returns:
    str: Normalized URL.
    """
    parsed_url = urlparse(url)
    path = parsed_url.path.rstrip('/').split('/')
    if len(path) > 1 and path[-1] == 'index':
        path = path[:-1]
    normalized_path = '/'.join(path)
    return f"{parsed_url.scheme}://{parsed_url.netloc}{normalized_path}"

def is_same_url(url1, url2):
    """
    Determines if two URLs are considered the same according to specified rules.

    Parameters:
    url1 (str): The first URL.
    url2 (str): The second URL.

    Returns:
    bool: True if URLs are considered the same, False otherwise.
    """
    return normalize_url(url1) == normalize_url(url2)

def fail_qa_check(text_content, url):
    """
    Checks if a webpage fails QA based on the given criteria.

    Parameters:
    text_content (str): The text content of the webpage.
    url (str): The URL of the webpage.

    Returns:
    bool: True if the webpage fails QA, False otherwise.
    """
    error_indicators = ["404", "network error", "site cannot be reached", "domain for sale", "domain expired", "domain not in use", "page no longer available", "page not found", "hello world", "lorem ipsum", "content totally unrelated"]
    if any(indicator in text_content.lower() for indicator in error_indicators):
        return True
    if len(text_content.strip()) == 0 or text_content.lower() == "index":
        return True
    if not text_content.strip():
        return True
    if "login" in text_content.lower() and len(text_content.strip()) < 100:
        return True
    if "flash player" in text_content.lower():
        return True
    known_domain_sellers = ["hostgator.sg", "hostasean.sg", "webhost.com.sg"]
    if any(seller in url for seller in known_domain_sellers):
        return False
    return False

def process_single_file(file_path):
    """
    Processes a single WARC file and extracts relevant data.

    Parameters:
    file_path (str): Path to the WARC file.

    Returns:
    list: A list of dictionaries containing the filename, title, text content, and URL.
    """
    records = parse_warc(file_path)
    return records

def deduplicate_records(records):
    """
    Deduplicates records based on URL rules.

    Parameters:
    records (list): List of records to deduplicate.

    Returns:
    list: Deduplicated list of records.
    """
    seen_urls = {}
    deduplicated_records = []
    for record in records:
        normalized_url = normalize_url(record['url'])
        if normalized_url in seen_urls:
            seen_urls[normalized_url]['web_text_content'] += "\n" + record['web_text_content']
        else:
            seen_urls[normalized_url] = record
            deduplicated_records.append(record)
    return deduplicated_records

def process_warc_files(folder_path, max_workers=4):
    """
    Processes all WARC files in a given folder using multithreading.

    Parameters:
    folder_path (str): Path to the folder containing WARC files.
    max_workers (int): Maximum number of worker threads.

    Returns:
    pd.DataFrame: DataFrame containing the extracted data from all WARC files.
    """
    data = []
    total_files = sum([len(files) for r, d, files in os.walk(folder_path)])
    logging.info(f"Total files to process: {total_files}")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.endswith('.warc.gz'):  # Process only WARC files
                    file_path = os.path.join(root, file)
                    futures.append(executor.submit(process_single_file, file_path))
        
        for i, future in enumerate(as_completed(futures), 1):
            try:
                data.extend(future.result())
                logging.info(f"Processed {i}/{total_files} files.")
            except Exception as e:
                logging.error(f"Error processing future: {e}")
    
    deduplicated_data = deduplicate_records(data)
    return pd.DataFrame(deduplicated_data)