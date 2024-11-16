from dotenv import load_dotenv
import requests
import os
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time
load_dotenv(override=True)
api_key = os.getenv('OMDB_API_KEY')

def create_session():
    session = requests.Session()
    
    # Configure retry strategy
    retries = Retry(
        total=5,  # number of retries
        backoff_factor=1,  # wait 1, 2, 4, 8, 16 seconds between retries
        status_forcelist=[500, 502, 503, 504, 404],
        allowed_methods=["GET"]
    )
    
    # Add retry adapter to session
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))
    
    return session

def download_movie_posters_omdb(movie_titles, output_folder):
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    base_url = "http://www.omdbapi.com/"

    # Check if movie_titles is a single string or a list
    if isinstance(movie_titles, str):
        movie_titles = [movie_titles]

    for title in movie_titles:
        # Make a request to the OMDB API
        params = {
            'apikey': api_key,
            't': title,
            'plot': 'short',
            'r': 'json'
        }
        response = requests.get(base_url, params=params)
        movie_data = response.json()

        # Check if the movie was found and has a poster
        if movie_data.get('Response') == 'True' and movie_data.get('Poster') != 'N/A':
            poster_url = movie_data['Poster']
            
            # Get the image file name
            img_name = f"{title.replace(' ', '_').replace('/', '_').replace('?', '').replace(':', '')}.jpg"
            
            # Download the image
            img_data = requests.get(poster_url).content
            
            # Save the image
            try:
                with open(os.path.join(output_folder, img_name), 'wb') as handler:
                    handler.write(img_data)
                
                print(f"Downloaded: {img_name}")
                return True
            except Exception as e:
                print(f"Error downloading poster for {title}: {str(e)}")
                return False
        else:
            print(f"No poster found for: {title}")
            return False

def get_genre_from_omdb(movie_title):
    return get_movie_data(movie_title).get('Genre', None)

def get_director_from_omdb(movie_title):
    return get_movie_data(movie_title).get('Director', None)    
  
def get_title_from_omdb(movie_title):
    return get_movie_data(movie_title).get('Title', None)

def get_year_from_omdb(movie_title):
    return get_movie_data(movie_title).get('Year', None)

def get_rated_from_omdb(movie_title):
    return get_movie_data(movie_title).get('Rated', None)

def get_releaseDate_from_omdb(movie_title):
    return get_movie_data(movie_title).get('Released', None)

def get_runtime_from_omdb(movie_title):
    return get_movie_data(movie_title).get('Runtime', None)

def get_writer_from_omdb(movie_title):
    return get_movie_data(movie_title).get('Writer', None)

def get_actors_from_omdb(movie_title):
    return get_movie_data(movie_title).get('Actors', None)

def get_plot_from_omdb(movie_title):
    return get_movie_data(movie_title).get('Plot', None)

def get_language_from_omdb(movie_title):
    return get_movie_data(movie_title).get('Language', None)

def get_country_from_omdb(movie_title):
    return get_movie_data(movie_title).get('Country', None)

def get_awards_from_omdb(movie_title):
    return get_movie_data(movie_title).get('Awards', None)

def get_poster_url_from_omdb(movie_title):
    return get_movie_data(movie_title).get('Poster', None)

def get_ratings_from_omdb(movie_title):
    return get_movie_data(movie_title).get('Ratings', None)

def get_metascore_from_omdb(movie_title):
    return get_movie_data(movie_title).get('Metascore', None)

def get_imdb_rating_from_omdb(movie_title):
    return get_movie_data(movie_title).get('imdbRating', None)

def get_imdb_votes_from_omdb(movie_title):
    return get_movie_data(movie_title).get('imdbVotes', None)

def get_imdb_id_from_omdb(movie_title):
    return get_movie_data(movie_title).get('imdbID', None)

def get_type_from_omdb(movie_title):
    return get_movie_data(movie_title).get('Type', None)

def get_dvd_from_omdb(movie_title):
    return get_movie_data(movie_title).get('DVD', None)

def get_box_office_from_omdb(movie_title):
    return get_movie_data(movie_title).get('BoxOffice', None)

def get_production_from_omdb(movie_title):
    return get_movie_data(movie_title).get('Production', None)

def get_website_from_omdb(movie_title):
    return get_movie_data(movie_title).get('Website', None)

def get_movie_actors_from_omdb(movie_title):
    return get_movie_data(movie_title).get('Actors', None)


def get_movie_data(title, year=None, max_retries=3):
    base_url = "http://www.omdbapi.com/"
    api_key = os.environ.get('OMDB_API_KEY')
    
    if not api_key:
        raise ValueError("OMDB_API_KEY not found in environment variables")
    
    params = {
        'apikey': api_key,
        't': title,
        'type': 'movie'
    }
    
    if year:
        params['y'] = year
        
    session = create_session()
    
    for attempt in range(max_retries):
        try:
            response = session.get(base_url, params=params, timeout=10)
            response.raise_for_status()  # Raise an error for bad status codes
            
            data = response.json()
            if data.get('Response') == 'True':
                return data
            else:
                print(f"No data found for movie: {title} ({year if year else 'any year'})")
                return None
                
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error on attempt {attempt + 1}/{max_retries}: {str(e)}")
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
            
        except requests.exceptions.RequestException as e:
            print(f"Request failed on attempt {attempt + 1}/{max_retries}: {str(e)}")
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)
            
    return None

def get_box_office_from_omdb(movie_title):
    box_office = get_movie_data(movie_title).get('BoxOffice', None)
    if box_office:
        try:
            # Remove '$' and ',' from the string and convert to float
            return float(box_office.replace('$', '').replace(',', ''))
        except ValueError:
            print(f"Error converting box office value '{box_office}' to float")
            return -1
    return -1

def download_movie_posters(movie_titles, output_folder):
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    base_url = "http://www.omdbapi.com/"

    # Check if movie_titles is a single string or a list
    # if isinstance(movie_titles, str):
        # movie_titles = [movie_titles]

    for title in movie_titles:
        # Make a request to the OMDB API
        params = {
            'apikey': api_key,
            't': title,
            'plot': 'short',
            'r': 'json'
        }
        response = requests.get(base_url, params=params)

        # Check if the response is successful
        if response.status_code == 200:
            try:
                movie_data = response.json()
            except requests.exceptions.JSONDecodeError:
                print(f"Error decoding JSON for movie: {title}")
                continue
        else:
            print(f"Error fetching data for {title}: {response.status_code} - {response.text}")
            continue

        # Check if the movie was found and has a poster
        if movie_data.get('Response') == 'True' and movie_data.get('Poster') != 'N/A':
            poster_url = movie_data['Poster']
            
            # Get the image file name
            img_name = f"{title.replace(' ', '_').replace('/', '_').replace('?', '').replace(':', '')}.jpg"
            
            # Download the image
            img_data = requests.get(poster_url).content
            
            # Save the image
            try:
                with open(os.path.join(output_folder, img_name), 'wb') as handler:
                    handler.write(img_data)
                
                print(f"Downloaded: {img_name}")
                # return os.path.join(output_folder, img_name)
            except Exception as e:
                print(f"Error downloading poster for {title}: {str(e)}")
                return False
        else:
            print(f"No poster found for: {title}")
            return False
