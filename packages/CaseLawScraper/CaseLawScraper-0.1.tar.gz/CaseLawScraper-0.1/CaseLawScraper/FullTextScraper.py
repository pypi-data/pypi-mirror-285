import json
import requests
from bs4 import BeautifulSoup

class FullTextScraper:
    """A class to scrape the full text of judgments from the National Archives website."""

    def __init__(self, json_file_path):
        """Initializes the scraper with the path to the JSON file containing judgment links."""
        self.json_file_path = json_file_path

    def load_json(self):
        """Loads the JSON file containing judgment links.

        Returns:
            A dictionary with judgment details.
        """
        with open(self.json_file_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    def scrape_full_text(self, url):
        """Scrapes the full text from the given URL.

        Args:
            url: The URL of the judgment page.

        Returns:
            A string containing the full text of the judgment.
        """
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        judgment_body = soup.find("section", class_="judgment-body")
        if judgment_body:
            return judgment_body.get_text(separator=' ', strip=True)
        return ""

    def add_full_text_to_json(self, data):
        """Adds the full text to each judgment entry in the data dictionary.

        Args:
            data: A dictionary with judgment details.
        """
        for case_name, details in data.items():
            url = details['link']
            full_text = self.scrape_full_text(url)
            details['full_text'] = full_text

    def save_to_json(self, data, output_file_path):
        """Saves the updated data to a JSON file in a pretty-printed format.

        Args:
            data: The data to save.
            output_file_path: The path of the file to save the data to.
        """
        with open(output_file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def run(self, output_file_path):
        """Runs the scraper to add full text to the JSON data and saves it to a new file.

        Args:
            output_file_path: The path of the file to save the updated data to.
        """
        data = self.load_json()
        self.add_full_text_to_json(data)
        self.save_to_json(data, output_file_path)