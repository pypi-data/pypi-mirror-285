import requests
from bs4 import BeautifulSoup
import datetime
import json
import pandas as pd

class CaseInfoScraper:
  """Scrapes judgment information from the National Archives website."""

  def __init__(self, base_url):
    """Initializes the scraper with a base URL for search results and a string to prepend to hrefs."""
    prefix_string = "https://caselaw.nationalarchives.gov.uk/"
    self.base_url = base_url
    self.prefix_string = prefix_string

  def scrape_judgments(self, url):
    """Scrapes judgment information from a single page.

    Args:
      url: The URL of the search results page.

    Returns:
      A dictionary containing information for each judgment on the page, with case name as the key.
    """

    all_judgments_data = {}
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all containers holding judgment information
    judgements = soup.find_all("div", class_="results__result-list-container")

    for judgement in judgements:
      judgements_list = judgement.find("ul", class_="judgment-listing__list")
      for li in judgements_list.find_all("li"):
        data = {}

        # Extract judgment information
        anchor = li.find("a")
        data["link"] = self.prefix_string + anchor["href"]  # Prepend prefix string to href
        data["Name of the Case"] = anchor.text.strip()

        court_span = li.find("span", class_="judgment-listing__court")
        data["judgment-listing__court"] = court_span.text.strip()

        neutral_citation_span = li.find("span", class_="judgment-listing__neutralcitation")
        data["judgment-listing__neutralcitation"] = neutral_citation_span.text.strip()

        date_span = li.find("time", class_="judgment-listing__date")
        data["datetime"] = datetime.datetime.strptime(date_span["datetime"], "%d %b %Y, midnight")

        # Store data with case name as key
        case_name = data["Name of the Case"].strip()
        all_judgments_data[case_name] = data

    return all_judgments_data

  def scrape_all_judgments(self, num_pages):
    """Scrapes judgment information from all specified pages.

    Args:
      num_pages: The number of pages to scrape.

    Returns:
      A dictionary containing information for all judgments across all scraped pages, with case name as the key.
    """

    all_judgments_data = {}
    for page_number in range(1, num_pages + 1):
      url = f"{self.base_url}&page={page_number}"
      page_data = self.scrape_judgments(url)
      all_judgments_data.update(page_data)  # Combine data from all pages

    return all_judgments_data

  def save_to_json(self, data, file_path):
    """Saves the scraped data to a JSON file in a pretty-printed format.

    Args:
      data: The data to save.
      file_path: The path of the file to save the data to.
    """
    with open(file_path, 'w', encoding='utf-8') as f:
      json.dump(data, f, ensure_ascii=False, indent=4, default=str)