from bs4 import BeautifulSoup
import pandas as pd
import requests
import datetime
import os
import numpy as np
from pymongo import MongoClient
import math
import time


class CraigslistScraper(object):

    def __init__(self, city, params):
        '''
        INPUT:
            city = 'denver'
            params = {'search_distance': 5,
                'postal': 80206,
                'max_price': 0,
                'max_price': 1100,
                'min_bedrooms': 0,
                'max_bedrooms': 1,
                'minSqft': 400,
                'availabilityMode': 1,
                'pets_dog': 1,
                'pets_cat': 1,
                'sale_date': 'all+dates'}
        '''
        self.url = 'https://{}.craigslist.org/search/apa'.format(city)
        self.params = params
        self.soup = []
        self.db = MongoClient('mongodb://localhost:27017/')['{}_cl_urls'.format(city)]['listings']

    def scrape(self):
        self._soupify()
        results = int((self.soup.find('span', {'class':'totalcount'}).text))/120
        # for page in range(math.ceil(results)):
        #     self.params['s'] = page*120
        #     self._soupify()
        #     self._url_build()
        self._url_build() # delete when for loop brought back

    def _soupify(self):
        page = requests.get(self.url, self.params)
        if page.status_code == 404:
            self.db.delete_one({'url' : self.url})
        elif page.status_code != 200:
            time.sleep(1)
            page = requests.get(self.url, self.params)
        self.soup = BeautifulSoup(page.content, 'html.parser')

    def _url_build(self):
        for data in self.soup.select('li.result-row'):
            features = {'_id': data['data-pid'],
                        'url': data.find('a')['href'],
                        'result-date': data.find('time')['datetime'],
                        'title': data.find('a', {'class':'result-title hdrlnk'}).text,
                        'price': int(data.find('span', {'class':'result-price'}).text[1:])}
                        # 'housing': ''.join(''.join(data.find('span', {'class':'housing'}).text.split(' ')).split('-\n')[1])}
            self.db.replace_one({'_id': features['_id']}, features, upsert=True)

    def _listing_build(self):
        for listing in self.db.find():
            self.url = listing['url']
            self.params = {}
            self._soupify()
            if self.soup.find("span", {"id":"has_been_removed"}) or self.soup.find("div", {"class":"post-not-found"}):
                self.db.delete_one({'_id' : listing['_id']})
            else:
                specs = ''.join(words for words in str(self.soup.select('p.attrgroup')[0]) if words not in '<>b/[],')
                features = {'address': ''.join(i.text for i in self.soup.select('div.mapaddress') if i != []),
                    'bed': int(specs[specs.find('BR')-1]) if specs.find('BR') != -1 else '',
                    'bath': int(specs[specs.find('Ba')-1]) if specs.find('Ba') != -1 else '',
                    'sqft': int(specs.split('ft')[0].split('"')[-1]) if specs.find('ft') != -1 else '',
                    'description': self.soup.find('section', {'id':"postingbody"}).text,
                    'img': ''.join(i.find('img')['src'] for i in self.soup.findAll('div',{'class':'slide first visible'}) if i != [])}
                if self.soup.select('div.viewposting'):
                    features['lat'] = float(''.join(i['data-latitude'] for i in self.soup.select('div.viewposting') if i != [])),
                    features['long'] = float(''.join(i['data-longitude'] for i in self.soup.select('div.viewposting') if i != [])),
                self.db.update_one({'_id': listing['_id']}, {'$set':features})


if __name__ == '__main__':
    city = 'denver'
    params = {'search_distance': 5,
        'postal': 80206,
        'max_price': 0,
        'max_price': 1500,
        'min_bedrooms': 0,
        'max_bedrooms': 1,
        'minSqft': 400,
        'availabilityMode': 1,
        'pets_dog': 1,
        'pets_cat': 1,
        'sale_date': 'all+dates'}
    scraper = CraigslistScraper(city, params)
    scraper.scrape()
    listings = scraper._listing_build()
