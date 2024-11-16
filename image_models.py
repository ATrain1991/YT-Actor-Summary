class PlaceImage:
    def __init__(self, image_path, x_pos, y_pos, width, height):
        self.image_path = image_path
        self.x = x_pos
        self.y = y_pos
        self.width = width
        self.height = height
    def get_tuple(self):
        # Returns (image_path, x_pos, y_pos, width, height) for movie poster
        return (self.image_path, self.x, self.y, self.width, self.height)
    
class Poster(PlaceImage):
    def __init__(self, path, x, y, width, height):
        super().__init__(path, x, y, width, height)

class FilmStrip:
    def __init__(self, main_image_path, first_text, box_office_text, third_text, fourth_text, poster_path, tomato_path, popcorn_path, box_office):
        self.main_image_path = main_image_path # main image path
        self.first_text = first_text # date
        self.second_text = box_office_text # box office
        self.third_text = third_text # tomato score
        self.fourth_text = fourth_text # popcorn score
        self.poster_path = poster_path # poster image path
        self.tomato_path = tomato_path # tomato meter image path
        self.popcorn_path = popcorn_path # popcorn meter image path