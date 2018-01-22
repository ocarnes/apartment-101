# from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import requests
import datetime
import re
import os
import numpy as np
import spacy
from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS
from string import punctuation
from sklearn.model_selection import train_test_split
nlp = spacy.load('en')

def listing_scraper(url):
    page = requests.get(url).content
    soup = BeautifulSoup(page, 'html.parser')

    units = soup.findAll('a', {'class':"placardTitle js-placardTitle "})
    listings = pd.concat([pd.DataFrame([[listing['title'], listing['href']]],
        columns=['name', 'url']) for listing in units], ignore_index=True)
    if soup.find('a', {'class':"next "}):
        url = soup.find('a', {'class':"next "})['href']
    else:
        url = None
    return url, listings

def next_page(url):
    units = pd.DataFrame(columns = ['name', 'url'])
    while url:
        url, listings = listing_scraper(url)
        units = units.append(listings, ignore_index=True)
    return units

def building_scraper(url, center_point):
    page = requests.get(url).content
    soup = BeautifulSoup(page, 'html.parser')

    description = description_info(soup)
    name = name_info(soup)
    address = get_property_address(soup)
    map_info = maps(center_point)
    distance, time = get_distance_duration(map_info, address)
    miles = float(distance.split(' ')[0])
    minutes = float(time.split(' ')[0])
    price = size_and_price(soup, 'rent')
    sq_ft = size_and_price(soup, 'sqft')
    if (price == []) | (name == ''):
        pass
    else:
        df = pd.concat([pd.DataFrame([[name, price[i], sq_ft[i], miles, minutes, url, description]],
            columns=['name', 'price', 'sq_ft', 'miles', 'minutes', 'url', 'description']) for i in range(len(price))], ignore_index=True)
        return df

def description_info(soup):
    STOPLIST = set(list(ENGLISH_STOP_WORDS) + ["n't", "'s", "'m", "ca", "'", "'re"])
    PUNCT_DICT = {ord(punc): None for punc in punctuation if punc not in ['_', '@']}#'*']}
    article = soup.find('p', {'itemprop':'description'})
    if article is None:
        return ''
    else:
        article = article.text
        doc = nlp(article)

        # Let's merge all of the proper entities
        for ent in doc.ents:
            if ent.root.tag_ != 'DT':
                ent.merge(ent.root.tag_, ent.text, ent.label_)
            else:
                # Keep entities like 'the New York Times' from getting dropped
                ent.merge(ent[-1].tag_, ent.text, ent.label_)

        # Part's of speech to keep in the result
        pos_lst = ['ADJ', 'ADV', 'NOUN', 'PROPN', 'VERB', 'NUM'] # NUM?

        tokens = [token.lemma_.lower().replace(' ', '_') for token in doc if token.pos_ in pos_lst]

        description= ' '.join(token for token in tokens if token not in STOPLIST).replace("'s", '').translate(PUNCT_DICT)
        return description

def parking_info(soup):
    parking = soup.find('div', {'class':"parkingDetails"})

    letters = 'abcdefghijklmnopqrstuvwxyz :$'
    price = int(''.join(token for token in parking.lower() if token not in set(letters)))

    return parking

def pet_info(soup):
    pass

def name_info(soup):
    name = prettify_text(soup.find('h1', {'class':'propertyName'}).text)
    if ('Senior' in name) | ('Student' in name):
        return ''
    else:
        return name

def size_and_price(soup, val):
    lst = []
    active_units = soup.find('div', {'class':'tabContent active'})
    if active_units is not None:
        pass
    else:
        active_units=soup
    for i in range(len(active_units.findAll('td', {'class':"available"}))):
        if 'Now' in active_units.findAll('td', {'class':"available"})[i].text:
            letters = 'abcdefghijklmnopqrstuvwxyz :$,'
            obj = prettify_text(active_units.findAll('td', {'class':val})[i].text)
            if obj is not '':
                obj = int(''.join(token for token in obj.lower() if token not in set(letters)).split('-')[0])
            else:
                obj = 0
            lst.append(obj)
    return lst

def prettify_text(data):
    """Given a string, replace unicode chars and make it prettier"""

    # format it nicely: replace multiple spaces with just one
    data = re.sub(' +', ' ', data)
    # format it nicely: replace multiple new lines with just one
    data = re.sub('(\r?\n *)+', '\n', data)
    # format it nicely: replace bullet with *
    data = re.sub(u'\u2022', '* ', data)
    # format it nicely: replace registered symbol with (R)
    data = re.sub(u'\xae', ' (R) ', data)
    # format it nicely: remove trailing spaces
    data = data.strip()
    # format it nicely: encode it, removing special symbols
    data = data.encode('utf8', 'ignore')

    return str(data,'utf-8')

def get_property_address(soup):
    """Given a beautifulSoup parsed page, extract the full address of the property"""

    # create the address from parts connected by comma (except zip code)
    address = []

    # this can be either inside the tags or as a value for "content"
    obj = soup.find(itemprop='streetAddress')
    text = obj.get('content')
    if text is None:
        text = obj.getText()
    text = prettify_text(text)
    address.append(text)

    obj = soup.find(itemprop='addressLocality')
    text = obj.get('content')
    if text is None:
        text = obj.getText()
    text = prettify_text(text)
    address.append(text)

    obj = soup.find(itemprop='addressRegion')
    text = obj.get('content')
    if text is None:
        text = obj.getText()
    text = prettify_text(text)
    address.append(text)

    # join the addresses on comma before getting the zip
    address = ', '.join(address)

    obj = soup.find(itemprop='postalCode')
    text = obj.get('content')
    if text is None:
        text = obj.getText()
    text = prettify_text(text)
    # put the zip with a space before it
    address += ' ' + text

    return address

def get_distance_duration(map_info, address):
    """Use google API to return the distance and time to the target address"""

    # get the distance and the time from google
    # getting to work in the morning
    origin = map_info['target_address'].replace(' ', '+')
    destination = address.replace(' ', '+')
    map_url = map_info['maps_url'] + '&origins=' + origin + '&destinations=' + \
        destination + '&arrival_time=' + map_info['morning']

    # populate the distance / duration fields for morning
    travel_morning = get_travel_time(map_url)

    # coming back from work in the evening
    origin = address.replace(' ', '+')
    destination = map_info['target_address'].replace(' ', '+')
    map_url = map_info['maps_url'] + '&origins=' + origin + '&destinations=' + \
        destination + '&departure_time=' + map_info['evening']

    # populate the distance / duration fields for evening
    travel_evening = get_travel_time(map_url)

    # take the average
    distance = average_field(travel_morning, travel_evening, 'distance')
    duration = average_field(travel_morning, travel_evening, 'duration')
    return distance, duration

def get_travel_time(map_url):
    """Get the travel distance & time from Google Maps distance matrix app given a URL"""

    # the travel info dict
    travel = {}

    # read and parse the google maps distance / duration from the api
    response = requests.get(map_url).json()

    # the status might not be OK, ignore this in that case
    if response['status'] == 'OK':
        response = response['rows'][0]['elements'][0]
        # extract the distance and duration
        if response['status'] == 'OK':
            # get the info
            travel['distance'] = response['distance']['text']
            travel['duration'] = response['duration']['text']

    # return the travel info
    return travel

def average_field(obj1, obj2, field):
    """Take the average given two objects that have field values followed by (same) unit"""
    val1 = float(prettify_text(obj1[field]).split()[0])
    val2 = float(prettify_text(obj2[field]).split()[0])
    unit = ' ' + prettify_text(obj1[field]).split()[1]

    avg = 0.5 * (val1 + val2)
    if field == 'duration':
        avg = int(avg)

    return str(avg) + unit

def maps(center_point):
    # create a dict to pass in all of the Google Maps info to have fewer params
    map_info = {}

    # get the Google Maps information
    map_info['maps_url'] = 'https://maps.googleapis.com/maps/api/distancematrix/json?'
    units = 'imperial'
    mode = 'walking'
    routing = ''
    api_key = os.environ['GOOGLE_MAPS_API']
    map_info['target_address'] = center_point
    map_info['morning'] = parse_config_times('8:00 AM')
    map_info['evening'] = parse_config_times('5:00 PM')
    # create the maps URL so we don't pass all the parameters
    map_info['maps_url'] += 'units=' + units + '&mode=' + mode + \
        '&transit_routing_preference=' + routing + '&key=' + api_key
    return map_info

def parse_config_times(given_time):
    """Convert the tomorrow at given_time New York time to seconds since epoch"""

    # tomorrow's date
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    # tomorrow's date/time string based on time given
    date_string = str(tomorrow) + ' ' + given_time
    # tomorrow's datetime object
    format_ = '%Y-%m-%d %I:%M %p'
    date_time = datetime.datetime.strptime(date_string, format_)

    # the epoch
    epoch = datetime.datetime.utcfromtimestamp(0)

    # return time since epoch in seconds, string without decimals
    time_since_epoch = (date_time - epoch).total_seconds()
    return str(int(time_since_epoch))

if __name__ == '__main__':
    center_point = '200 E Colfax Ave, Denver, CO 80203'
    max_price = '1100'
    url = 'https://www.apartments.com/denver-co/under-{}/?so=2'.format(max_price)
    # if os.path.exists('../data/df_units.pkl'):
    #     units = pd.read_pickle('../data/df_units.pkl')
    # else:
    units = next_page(url)
    units.to_pickle('../data/df_units_1_22_2018.pkl')
    # if os.path.exists('../data/df_apartments.pkl'):
    #     df_apartments = pd.read_pickle('../data/df_apartments.pkl')
    # else:
    #     df_new = pd.DataFrame()
    #     for url in units.url:
    #         df = building_scraper(url)
    #         df_new = df_new.append(df,ignore_index=True)
    #     df_new.to_pickle('../data/df_apartments.pkl')
    if os.path.exists('../data/df_apartment_1_22_2018.pkl'):
        df_apartments = pd.read_pickle('../data/df_apartment_1_22_2018.pkl')
    else:
        df_apts = pd.DataFrame()
        for url in units.url:
            df = building_scraper(url, center_point)
            df_apts = df_apts.append(df,ignore_index=True)
        df_apts.to_pickle('../data/df_apartment_1_22_2018.pkl')
