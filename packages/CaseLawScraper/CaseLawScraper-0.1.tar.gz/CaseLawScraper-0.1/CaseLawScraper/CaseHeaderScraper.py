import requests
from bs4 import BeautifulSoup
import json
import json

class CaseHeaderScraper:
    """A class to scrape judgment information from the National Archives website."""

    def __init__(self, base_url):
        """Initializes the scraper with a base URL for search results."""
        self.base_url = base_url

    def scrape_judgment_urls(self, num_pages):
        """Scrapes judgment URLs from the National Archives website.

        Args:
            num_pages: The number of pages to scrape.

        Returns:
            A list of modified URLs for each judgment.
        """
        res = []
        for page in range(1, num_pages + 1):
            # Construct the URL for the current page
            url = f"{self.base_url}?query=&page={page}"
            # Fetch the page content
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            job_elements = soup.find_all("div", class_="results__result-list-container")
            
            for job_element in job_elements:
                links = job_element.find_all("a")
                for link in links:
                    link_url = link["href"]
                    res.append(link_url)

        string_to_add = 'https://caselaw.nationalarchives.gov.uk/'
        filtered_list = [item for item in res if "query" not in item]
        modified_list = [string_to_add + item for item in filtered_list]
        
        return modified_list

    def judgment_Dlink(self, modified_list):
        """Scrapes download links and other details from the specified URLs.

        Args:
            modified_list: A list of modified URLs to scrape.

        Returns:
            A list of dictionaries containing download link and other details for each judgment.
        """
        judgment_details = []

        for url in modified_list:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find all containers holding judgment information
            judgments = soup.find_all("div", class_="judgment-toolbar__container")
            
            for judgment in judgments:
                data = {}
                
                # Extract title of the case
                title_element = judgment.find("h1", class_="judgment-toolbar__title")
                if title_element:
                    data["title"] = title_element.text.strip()
                
                # Extract judgment reference
                reference_element = judgment.find("p", class_="judgment-toolbar__reference")
                if reference_element:
                    data["judgment_reference"] = reference_element.text.strip()
                
                # Extract download link
                download_element = judgment.find("a", class_="judgment-toolbar-buttons__option--pdf")
                if download_element and "href" in download_element.attrs:
                    data["download_link"] = download_element["href"]
                
                # Add the data to the list if it contains valid data
                if data:
                    judgment_details.append(data)
        
        return judgment_details

    def scrape_header_info(self, modified_list):
        """Scrapes header information from the specified URLs.
        
        Args:
            modified_list: A list of modified URLs to scrape.
            
        Returns:
            A dictionary containing header information for each judgment.
        """
        header_info_dict = {}

        for url in modified_list:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find the judgment article
            judgment_article = soup.find("article", class_="judgment")
            
            if not judgment_article:
                continue
            
            data = {}
            
            # Extract all text within all headers with class="judgment-header"
            all_headers = judgment_article.find_all("header", class_="judgment-header")
            all_header_text = " ".join([header.get_text(separator=' ', strip=True) for header in all_headers])
            data["all_header_text"] = all_header_text

            # Extract specific information from the first header
            if all_headers:
                header_element = all_headers[0]

                # Extract judgment title
                title_element = header_element.find("p")
                if title_element:
                    data["title"] = title_element.text.strip()

                # Extract neutral citation number
                citation_element = header_element.find("div", class_="judgment-header__neutral-citation")
                if citation_element:
                    data["neutral_citation"] = citation_element.text.replace('Neutral Citation Number: ', '').strip()

                # Extract case number
                case_number_element = header_element.find("div", class_="judgment-header__case-number")
                if case_number_element:
                    data["case_number"] = case_number_element.text.replace('Case No: ', '').strip()

                # Extract court name
                court_element = header_element.find("div", class_="judgment-header__court")
                if court_element:
                    data["court"] = court_element.text.strip()

                # Extract location
                location_elements = header_element.find_all("p", class_="judgment-header__pr-right")
                if location_elements:
                    data["location"] = " ".join([element.text.strip() for element in location_elements])

                # Extract judgment date
                date_element = header_element.find("div", class_="judgment-header__date")
                if date_element:
                    data["date"] = date_element.text.replace('Date: ', '').strip()

            # Add data to dictionary with URL as key
            header_info_dict[url] = data
        
        return header_info_dict

    def save_to_json(self, data, file_path):
        """Saves the scraped data to a JSON file in a pretty-printed format.

        Args:
            data: The data to save.
            file_path: The path of the file to save the data to.
        """
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4, default=str)