'''functions.py'''
import googlemaps
import sqlite3
import random
from flask import Blueprint, render_template, request, flash, jsonify, json
from math import radians, sin, cos, sqrt, atan2

functions = Blueprint('functions', __name__)

@functions.route('/find_restaurants', methods=['POST', 'GET'])
def find_restaurants():
    if request.method == 'POST':
        location = request.form.get("locationInput")
        distance = int(request.form.get("distance")) * 100
        price = int(request.form.get("price")) * 50
        rate = request.form.get("rate")
        if not rate:
            rate = 0
        rate = float(rate)
        if request.form.get("child_room"):
            child_room = True
        else:
            child_room=False
        ukrainian = request.form.get("1")
        italian = request.form.get("2")
        french = request.form.get("3")
        virmenish = request.form.get("4")
        streetfood = request.form.get("5")
        europian = request.form.get("6")
        fish = request.form.get("7")
        fastfood = request.form.get("8")
        asian = request.form.get("9")
        author = request.form.get("10")
        panasian = request.form.get("11")
        galician = request.form.get("12")
        georgian = request.form.get("13")
        japanish = request.form.get("14")
        american = request.form.get("15")
        eastern = request.form.get("16")
        kavkaz = request.form.get("17")
        home = request.form.get("18")
        westukrainian = request.form.get("19")
        mexican = request.form.get("20")
        world = request.form.get("21")
        polish = request.form.get("22")
        chinese = request.form.get("23")
        turkish = request.form.get("24")
        azerbaidjan = request.form.get("25")
        checz = request.form.get("26")
        fuzhn = request.form.get("27")
        irland = request.form.get("28")
        ancientslav = request.form.get("29")
        greece = request.form.get("30")
        exclusive = request.form.get("31")
        middlesea = request.form.get("32")
        ugorish = request.form.get("33")
        slavian = request.form.get("34")
        uzbek = request.form.get("35")
        latinoamerican = request.form.get("36")
        cuisines = [ukrainian, italian, french, virmenish, streetfood, europian, fish, fastfood, asian, author, panasian,
                    galician, georgian, japanish, american, eastern, kavkaz, home, westukrainian, mexican, world,
                    polish, chinese, turkish, azerbaidjan, checz, fuzhn, irland, ancientslav, greece, exclusive,
                    middlesea, ugorish, slavian, uzbek, latinoamerican]
        cuisine = []
        for i in cuisines:
            if i:
                cuisine.append(i)
    criterias = {'Distance': distance, "Price": price, 'Rate': rate, 'Cuisine': cuisine, 'Vegan': False, "Children room": child_room, "Dishes": [], "Isopen": True}
    finder = Find(criterias, location)
    sorted_restaurants = finder.sort_by_criterias()
    return sorted_restaurants

    # return jsonify([{'name': restaurant.name, 'distance': restaurant.criterias['Distance']} for restaurant in sorted_restaurants])

class Find:
    __restaurants = []
    __db_path = 'website/restaurants.db'
    # criterias_rate = {'distance': 0, 'rate': 1, 'price': 2}
    # criterias = {'Distance': 0, "Price": 0, 'Rate': 0, 'Cuisine': [], 'Vegan': False, "Children oom": False, "Dishes": [], "Isopen": True}
    def __init__(self, criterias_set: dict, adress: str) -> None:
        self.coordinates = Find.coordinates_find(adress)
        self.criterias_set = criterias_set

    @staticmethod
    def coordinates_find(adress):
        api_key = 'AIzaSyBfZU8rUJWOZxsgbBp1DXzgDKQs0_0bHF4'
        gmaps = googlemaps.Client(key=api_key)
        try:
            geocode_result1 = gmaps.geocode(adress)
            if geocode_result1:
                location = geocode_result1[0]['geometry']['location']
                latitude = location['lat']
                longitude = location['lng']
                coordinates = [latitude, longitude]
                return coordinates
            else:
                print("Could not find coordinates for the address.")
                return None
        except Exception as e:
            print("Error:", e)
            return None

    @staticmethod
    def track_distance(coordinates1, coordinates2):
        lat1 = radians(coordinates1[0])
        lon1 = radians(coordinates1[1])
        lat2 = radians(coordinates2[0])
        lon2 = radians(coordinates2[1])

        R = 6371

        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = R * c
        return distance*1000

    def find_distance(self):
        for i in Find.__restaurants:
            try:
                i.criterias['Distance'] = Find.track_distance(i.coordinates, self.coordinates)
            except:
                i.criterias['Distance'] = 10000

    def sort_by_criterias(self):
        self.find_distance()
        def sort_to_sort(listok):
            res=[]
            for i in listok:
                if isinstance(i.criterias['Rate'], float):
                    if (i.criterias['Price'] <= self.criterias_set['Price'] and
                        i.criterias['Distance'] <= self.criterias_set['Distance'] and
                        i.criterias['Rate'] >= self.criterias_set['Rate'] and
                        i.criterias['Vegan'] == self.criterias_set['Vegan'] and
                        i.criterias['Children room'] == self.criterias_set['Children room'] and
                        i.criterias['Isopen']):
                        res.append(i)
                else:
                    if (i.criterias['Price'] <= self.criterias_set['Price'] and
                        i.criterias['Distance'] <= self.criterias_set['Distance'] and
                        i.criterias['Vegan'] == self.criterias_set['Vegan'] and
                        i.criterias['Children room'] == self.criterias_set['Children room'] and
                        i.criterias['Isopen']):
                        res.append(i)
            return res
        list_for_sorting = [i for i in Find.__restaurants]
        list_for_sorting = sort_to_sort(list_for_sorting)
        for i in ['Price', 'Rate']:
            list_for_sorting.sort(key=lambda x:x.criterias[i], reverse = True)
        list_for_sorting.sort(key=lambda x:x.criterias['Distance'])
        list_for_sorting.sort(key=lambda x:sum(1 if i in self.criterias_set['Cuisine'] else 0 for i in x.criterias['Cuisine']), reverse=True)
        list_for_sorting.sort(key=lambda x:x.criterias['Rate'] == 'No rate')
        return [i.info for i in list_for_sorting]

    @staticmethod
    def retrieve_restaurants_from_db():
        connection = sqlite3.connect(Find.__db_path)
        cursor = connection.cursor()

        query = "SELECT * FROM restaurants"
        cursor.execute(query)
        records = cursor.fetchall()

        for record in records:
            restaurant = Restaurant(*record)
            if restaurant not in Find.__restaurants:
                Find.__restaurants.append(restaurant)

        connection.close()

class Restaurant:
    def __init__(self, name: str, adress: str, rating:float, link:float, cuisine:list, tel: str, open_time:str, price: int, image_path: str, child_room: int, long:float, lat:float) -> None:
        self.id = str(random.randint(10000, 99999)) + ''.join([str(ord(i)) for i in name])
        self.name = name
        self.contact_info = tel
        self.criterias = {'Distance': 0, "Price": price, 'Rate': rating if isinstance(rating, float) else 3, 'Cuisine': cuisine, 'Vegan': False, "Children room": bool(child_room), "Dishes": [], "Isopen": True}
        self.rate = rating
        self.coordinates = [long, lat]
        self.open_time = open_time
        self.link = link
        self.image = image_path
        self.info = {'Photo': image_path, 'Adress': adress, 'Name': name, 'Pirce': price, 'Link': link, 'Cuisine': cuisine, 'Open time': open_time, 'Contact': tel, 'Child_room': bool(child_room), 'Rating': rating}

    def __eq__(self, other):
        """
        Check if two restaurants are equal.
        """
        if not isinstance(other, Restaurant):
            return False
        
        return (self.name == other.name and
                self.coordinates == other.coordinates)
