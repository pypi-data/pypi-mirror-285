from flask import Flask, request, jsonify
import logging
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.common.exceptions import WebDriverException, TimeoutException
from urllib.parse import urlparse
import os
import argparse

app = Flask(__name__)

def is_valid_url(url):
    """
    Validate the URL format.
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def scrape_static_content(url):
    """
    Scrape static content using requests and BeautifulSoup.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        return str(soup)
    except requests.RequestException as e:
        logging.error(f"Error fetching static content: {e}")
        return None

def is_dynamic_content(html_content):
    """
    Check for indicators of dynamic content in the HTML.
    """
    if "<script" in html_content or "application/json" in html_content or "window." in html_content:
        return True
    return False

def scrape_with_firefox(url,geckodriver_path):
    """
    Scrape dynamic content using Selenium and headless Firefox.
    """
    options = Options()
    options.headless = True
    service = Service(geckodriver_path)
    content = ""
    try:
        with webdriver.Firefox(service=service, options=options) as browser:
            browser.get(url)
            content = browser.page_source
    except (WebDriverException, TimeoutException) as e:
        logging.error(f"Error during dynamic web scraping: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        return content
    
def parse_tables(html_content, table_class=None):
    """
    Parse HTML content and extract tables, optionally filtering by class.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    if table_class:
        tables = soup.find_all('table', class_=table_class)
    else:
        tables = soup.find_all('table')

    table_list = []
    for table in tables:
        headers = []
        rows = []
        
        # Extract headers
        thead = table.find('thead')
        if thead:
            header_rows = thead.find_all('tr')
            for header_row in header_rows:
                headers = [header.text.strip() for header in header_row.find_all('th')]
        
        # Extract rows from tbody
        tbody = table.find('tbody')
        if tbody:
            body_rows = tbody.find_all('tr')
            for body_row in body_rows:
                cells = body_row.find_all(['td', 'th'])
                row_data = []
                for cell in cells:
                    # Check for colspan
                    colspan = cell.get('colspan')
                    if colspan:
                        row_data.extend([cell.text.strip()] * int(colspan))
                    else:
                        row_data.append(cell.text.strip())
                rows.append(row_data)
        
        table_list.append({'headers': headers, 'rows': rows})
    
    return table_list

@app.route('/scrape', methods=['GET'])
def scrape():
    """
    Scrape the given URL.
    """
    url = request.args.get('url')
    if not url or not is_valid_url(url):
        return jsonify({'message': 'Invalid or missing URL'}), 400

    soup = scrape_static_content(url)
    content = str(soup) if soup else None
    if not content or is_dynamic_content(content):
        content = scrape_with_firefox(url, app.config['GECKODRIVER_PATH'])

    if content:
        return jsonify({'content': content}), 200
    else:
        return jsonify({'message': 'Failed to scrape the content'}), 500

@app.route('/scrape-tables', methods=['GET'])
def scrape_tables():
    """
    Scrape the given URL and parse tables from the HTML content.
    """
    url = request.args.get('url')
    table_class = request.args.get('class')
    if not url or not is_valid_url(url):
        return jsonify({'message': 'Invalid or missing URL'}), 400

    soup = scrape_static_content(url)
    content = str(soup) if soup else None
    if not content or is_dynamic_content(content):
        content = scrape_with_firefox(url, app.config['GECKODRIVER_PATH'])

    if content:
        tables = parse_tables(content, table_class)
        return jsonify({'tables': tables}), 200
    else:
        return jsonify({'message': 'Failed to scrape the content'}), 500


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Flask web scraper.")
    parser.add_argument('--host', default='0.0.0.0', help='The host to run the Flask app on.')
    parser.add_argument('--port', type=int, default=5000, help='The port to run the Flask app on.')
    parser.add_argument('--geckodriver', default='/usr/local/bin/geckodriver', help='The path to the geckodriver executable.')
    args = parser.parse_args()

    app.config['GECKODRIVER_PATH'] = args.geckodriver

    app.run(debug=True, host=args.host, port=args.port)
