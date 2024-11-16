from datetime import datetime

import image_resize
import omdb_api


def get_float_from_box_office(box_office):
    if box_office is None or box_office == '' or box_office == '-':
        print("Box office is None, empty, or '-'")
        return 0.0
    if isinstance(box_office, (float, int)):
        print(f"Box office is already a float: {box_office}")
        return box_office
    else:
        box_office = box_office.replace('$','').replace(',','')
        if 'B' in box_office:
            print(f"Box office is in billions: {box_office}")
            return float(box_office.replace('B','')) * 1e9
        if 'M' in box_office:
            print(f"Box office is in millions: {box_office}")
            return float(box_office.replace('M','')) * 1e6
        elif 'K' in box_office:
            print(f"Box office is in thousands: {box_office}")
            return float(box_office.replace('K','')) * 1e3
        else:
            print(f"Box office is in dollars: {box_office}")
            return float(box_office)
def inflation_safe_year(year):
    current_year = datetime.now().year
    return int(year) if year and year.isdigit() and int(year) < current_year else current_year
def download_posters(actor,poster_movies= None):
    Master_api_key = "66f234c0"  # Replace with your actual OMDB API key
    # Download posters for the movies
    if poster_movies is None:
        poster_movies = actor.movies
    omdb_api.download_movie_posters(Master_api_key, poster_movies, actor.name)
    image_resize.resize_root_poster_folder(actor.name, actor.name)