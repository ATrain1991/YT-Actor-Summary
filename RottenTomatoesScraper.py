import requests
from bs4 import BeautifulSoup
from datetime import datetime
import HelperMethods
from Movie import Movie
import omdb_api

def get_actor_url_soup(actor_name):
        formatted_name = actor_name.lower().replace(' ', '_').replace('.', '').replace("'", "").replace('-','_')
        url = f'https://www.rottentomatoes.com/celebrity/{formatted_name}'
    
    # Fetch the page content
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to fetch data for {actor_name}. Status code: {response.status_code}")
            return None  
        else:
            print(f"Successfully fetched data for {actor_name}")
            return BeautifulSoup(response.text, 'html.parser')
def get_actor_portrait(actor_name):
    soup = get_actor_url_soup(actor_name)
    if not soup:
        return None

    import os
    images = soup.find_all('img')
    portrait_element = soup.find('img', alt=lambda alt: alt and 'portrait photo of' in alt.lower() and actor_name.lower() in alt.lower())
    if portrait_element:
        portrait_url = portrait_element['src']
        response = requests.get(portrait_url)
        if response.status_code == 200:
            output_folder = 'actor_portraits'
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            file_path = os.path.join(output_folder, f"{actor_name.replace(' ', '_').lower()}.jpg")
            with open(file_path, 'wb') as file:
                file.write(response.content)
            return file_path
        else:
            print(f"Failed to download portrait for {actor_name}. Status code: {response.status_code}")
            return None
    else:
        print(f"Failed to find portrait for {actor_name}")
        return None

def get_actor_birthdate(actor_name):
    # Update or add the birthdate to the actor in the database
        from datetime import datetime
        soup=get_actor_url_soup(actor_name)

        birthday_element = soup.find('p', class_='celebrity-bio__item', attrs={'data-qa': 'celebrity-bio-bday'})
        birthday_text = birthday_element.text.strip().split(':')[-1].strip()
        try:
            return datetime.strptime(birthday_text, '%b %d, %Y').date()
        except ValueError:
            print(f"Failed to parse birthday: {birthday_text}")

def scrape_actor_data(actor_name):
    # Format the actor name for the URL
    soup=get_actor_url_soup(actor_name)
    if not soup:
        return None
#remove tv section
    tv_section = soup.find('rt-text', string=lambda text: text and text.strip() == 'TV')
    if tv_section:
        # Remove everything after the TV section
        for element in tv_section.find_all_next():
            element.decompose()

    # Scrape movies data
    movies_data = []
    movie_id = 0
    for row in soup.select('tr[data-title]'):
        title = row.select_one('.celebrity-filmography__title a')
        title = title.text.strip() if title else None

        year_elem = row.select_one('.celebrity-filmography__year')
        year = year_elem.text.strip() if year_elem else None

        def get_positive_number(value):
            try:
                number = float(value)
                return number if number >= 0 else None
            except (ValueError, TypeError):
                return None

        tomatometer_elem = row.select_one('[data-tomatometer]')
        tomatometer = get_positive_number(tomatometer_elem['data-tomatometer']) if tomatometer_elem else None

        box_office_elem = row.select_one('.celebrity-filmography__box-office')
        box_office = get_positive_number(box_office_elem.text.strip()) if box_office_elem else None

        audience_score_elem = row.select_one('[data-audiencescore]')
        popcornmeter = get_positive_number(audience_score_elem['data-audiencescore']) if audience_score_elem else None

        credit_elem = row.select_one('.celebrity-filmography__credits')
        credit = credit_elem.text.strip() if credit_elem else None
        
        movies_data.append([
            movie_id,
            title,
            year,
            box_office,
            tomatometer,
            popcornmeter,
            credit
        ])
        movie_id += 1

    return movies_data

def scrape_actor_data2(actor_name):
    # Format the actor name for the URL
    soup=get_actor_url_soup(actor_name)
    if not soup:
        return None
#remove tv section
    tv_section = soup.find('rt-text', string=lambda text: text and text.strip() == 'TV')
    if tv_section:
        # Remove everything after the TV section
        for element in tv_section.find_all_next():
            element.decompose()

    # Scrape movies data
    movies_data = []
    for row in soup.select('tr[data-title]'):
        title = row.select_one('.celebrity-filmography__title a')
        title = title.text.strip() if title else None

        year_elem = row.select_one('.celebrity-filmography__year')
        year = year_elem.text.strip() if year_elem else None

        def get_positive_number(value):
            try:
                number = float(value)
                return number if number >= 0 else None
            except (ValueError, TypeError):
                return None

        tomatometer_elem = row.select_one('[data-tomatometer]')
        tomatometer = get_positive_number(tomatometer_elem['data-tomatometer']) if tomatometer_elem else 0

        box_office_elem = row.select_one('.celebrity-filmography__box-office')
        if box_office_elem:
            box_office = box_office_elem.text.strip()
            numeric_box_office = HelperMethods.get_float_from_box_office(box_office)
            if numeric_box_office and numeric_box_office < 1000:
                box_office = omdb_api.get_box_office_from_omdb(title)
        else:
            box_office = None

        audience_score_elem = row.select_one('[data-audiencescore]')
        popcornmeter = get_positive_number(audience_score_elem['data-audiencescore']) if audience_score_elem else 0

        credit_elem = row.select_one('.celebrity-filmography__credits')
        credit = credit_elem.text.strip() if credit_elem else None

        # Get movie poster path
        # cleaned_title = title.replace(':', '') if title else ''
        # poster_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), actor_name, f"{cleaned_title}.jpg")
        # if not os.path.exists(poster_path):
        #     print(f"Warning: Could not find poster at {poster_path}")
        #     poster_path = None

        # Create Movie object
        movie_obj = Movie(title, year, box_office, "", tomatometer, popcornmeter,credit)
        movies_data.append(movie_obj)

    return movies_data