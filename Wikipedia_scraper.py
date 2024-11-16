import requests
from bs4 import BeautifulSoup
import re

def scrape_academy_awards(url):
    """
    Scrapes Academy Award nominations and wins from a Wikipedia awards page.
    
    Args:
        url (str): URL to Wikipedia awards page in format:
                  https://en.wikipedia.org/wiki/List_of_awards_and_nominations_received_by_[Actor]
                  
    Returns:
        dict: Dictionary containing number of Academy Award nominations and wins
    """
    try:
        # Get page content
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the awards table in the infobox
        awards_table = soup.find('table', class_='infobox-subbox')
        if not awards_table:
            return {'nominations': 0, 'wins': 0}

        # Find Academy Awards row
        academy_row = None
        for row in awards_table.find_all('tr'):
            if row.find(string=re.compile('Academy Awards')):
                academy_row = row
                break

        if not academy_row:
            return {'nominations': 0, 'wins': 0}

        # Get wins and nominations from the row
        cells = academy_row.find_all(['td'])
        if len(cells) >= 2:
            wins = int(cells[0].get_text().strip())
            nominations = int(cells[1].get_text().strip())
            return {
                'nominations': nominations,
                'wins': wins
            }
        
        return {'nominations': 0, 'wins': 0}

    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
        return {'nominations': 0, 'wins': 0}

def get_actor_awards(actor_name):
    """
    Gets Academy Award stats for an actor from their Wikipedia awards page.
    
    Args:
        actor_name (str): Name of actor (e.g. "Brad_Pitt")
        
    Returns:
        dict: Dictionary with nomination and win counts
    """
    actor_name = actor_name.replace(" ", "_")
    url = f"https://en.wikipedia.org/wiki/List_of_awards_and_nominations_received_by_{actor_name}"
    return scrape_academy_awards(url)
