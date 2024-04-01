from gnews import GNews
from Levenshtein import distance

class GoogleNewsScraper:
    """
    Scrapes relevant news from Google News based on keywords and locations.
    """

    def __init__(self, keywords, locations):
        """
        Initializes GoogleNewsScraper with keywords and locations.

        Args:
            keywords (list): List of keywords.
            locations (list): List of locations.
        """
        self.keywords = keywords
        self.locations = locations

    def scrape_news(self):
        """
        Scrapes relevant news from Google News and returns formatted text.

        Returns:
            str: Formatted text of relevant news.
        """
        query = f"({' OR '.join(self.keywords)}) AND ({' OR '.join(self.locations)})"

        # Get news from Google
        google_news = GNews(language='spanish', period='1d', country='Colombia')
        news_entries = google_news.get_news(query)

        valid_entries = [entry for entry in news_entries if self._is_entry_valid(entry)]

        # Remove duplicates based on content similarity
        unique_entries = self._remove_duplicates(valid_entries)

        text = ''
        if unique_entries:
            text += 'Relevant news from the last day:\n'
            for entry in unique_entries:
                formatted_date = entry.get("published date", "")
                title = entry.get("title", "")
                text += f'{formatted_date} - {title}\n'

        return text

    def _is_entry_valid(self, entry):
        """
        Checks if a news entry is valid based on keywords and locations.

        Args:
            entry (dict): News entry.

        Returns:
            bool: True if entry is valid, False otherwise.
        """
        title = entry.get('title', '').lower()
        description = entry.get('description', '').lower()

        keyword_present = any(keyword in title or keyword in description for keyword in self.keywords)
        location_present = any(location in title or location in description for location in self.locations)

        return keyword_present and location_present

    def _remove_duplicates(self, entries, threshold=0.9):
        """
        Removes duplicate news entries based on content similarity.

        Args:
            entries (list): List of news entries.
            threshold (float): Similarity threshold for considering duplicates.

        Returns:
            list: List of unique news entries.
        """
        unique_entries = []

        for entry in entries:
            duplicate_found = any(self._is_duplicate(entry, existing_entry, threshold) for existing_entry in unique_entries)

            if not duplicate_found:
                unique_entries.append(entry)

        return unique_entries

    def _is_duplicate(self, entry1, entry2, threshold=0.9):
        """
        Checks if two news entries are duplicates based on content similarity.

        Args:
            entry1 (dict): First news entry.
            entry2 (dict): Second news entry.
            threshold (float): Similarity threshold for considering duplicates.

        Returns:
            bool: True if entries are duplicates, False otherwise.
        """
        title_distance = distance(entry1['title'].lower(), entry2['title'].lower()) / max(len(entry1['title']), len(entry2['title']))
        description_distance = distance(entry1['description'].lower(), entry2['description'].lower()) / max(len(entry1['description']), len(entry2['description']))

        return title_distance < threshold and description_distance < threshold
