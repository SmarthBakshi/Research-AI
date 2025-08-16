import time
import requests
import xml.etree.ElementTree as ET
from .config import ArxivConfig
from tenacity import retry, wait_exponential, stop_after_attempt

class ArxivClient:
    def __init__(self, config: ArxivConfig):
        self.config = config

    @retry(wait=wait_exponential(multiplier=1), stop=stop_after_attempt(3))
    def fetch(self, start: int = 0) -> str:
        query = f"cat:{' OR '.join(self.config.categories)}"
        params = {
            "search_query": query,
            "start": start,
            "max_results": self.config.per_request,
            "sortBy": "submittedDate",
            "sortOrder": "descending"
        }

        response = requests.get(self.config.base_url, params=params)
        response.raise_for_status()
        time.sleep(self.config.delay_seconds)
        return response.text

    def parse_metadata(self, raw_xml: str) -> list[dict]:
        # parse XML to dicts (basic for now)
        root = ET.fromstring(raw_xml)
        entries = []
        for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
            title = entry.find("{http://www.w3.org/2005/Atom}title").text
            published = entry.find("{http://www.w3.org/2005/Atom}published").text
            entries.append({
                "title": title.strip(),
                "published": published,
            })
        return entries
