from flask import Flask, render_template, request, jsonify
import json
import requests
import socket
import time
from datetime import datetime
import re
import pandas as pd
import ast
import os
from craigslist_scraper import CraigslistScraper
from pymongo import MongoClient

# CONNECT TO THE DATABASE
# client = MongoClient('mongodb://localhost:27017/')

app = Flask(__name__)

def cos_sim_recs(index, n=5, resort=None, color=None):
    trail = X[index].reshape(1,-1)
    cs = cosine_similarity(trail, X)
    rec_index = np.argsort(cs)[0][::-1][1:]
    ordered_df = df.loc[rec_index]
    if resort:
        ordered_df = ordered_df[ordered_df['resort'] == resort]
    if color:
        ordered_df = ordered_df[ordered_df['colors'].isin(color)]
    rec_df = ordered_df.head(n)
    rec_df = rec_df.reset_index(drop=True)
    rec_df.index = rec_df.index+1
    orig_row = df.loc[[index]].rename(lambda x: 'original')
    total = pd.concat((orig_row,rec_df))
    return total

@app.route('/', methods=['GET'])
def index():
    """Render a simple splash page."""
    return render_template('form/index.html')

@app.route('/submit', methods=['GET','POST'])
def submit():
    """Render a page containing a textarea input where the user can either paste an
    article or a url to be classified.  """
    API = os.environ['GOOGLE_MAPS_API']
    url = "https://maps.googleapis.com/maps/api/js?key="+API+"&callback=initMap"
    # data = str(request.form['article_body'])
    # city, income, beds, baths, cats, dogs,laundry, parking
    inputs = ['city', 'income', 'income_type', 'debt', 'debt_type']#, 'beds', 'baths', 'cats', 'dogs', 'laundry', 'parking']
    input_dict = {i: request.form[i] for i in inputs}
    letters = 'qwertyuiopasdfghjklzxcvbnm'
    digits = '1234567890'
    chars = '~!@#$%^&*()_+`-={}|[]\:";<>?,./`\''
    input_dict['city'] = ''.join(i.lower() for i in input_dict['city'] if i not in digits+chars)
    input_dict['income'] =  float(''.join(i for i in input_dict['income'] if i not in letters+chars))
    input_dict['debt'] =  float(''.join(i for i in input_dict['debt'] if i not in letters+chars))
    # db = client['transactions']['{}_cl_urls'.format(str(input_dict['city']))]

    # calculating rent based on income
    if str(input_dict['income_type']) == 'Annual':
        rent = 0.35*input_dict['income']/12
    elif str(input_dict['income_type']) == 'Monthly':
        rent = 0.35*input_dict['income']
    elif str(input_dict['income_type']) == 'Bi-Weekly':
        rent = 0.35*input_dict['income']*26/12
    else:
        rent = 0.35*input_dict['debt']*40*52/12

    #calculating rent less debt
    if str(input_dict['debt_type']) == 'Annual':
        rent -= input_dict['debt']/12
    elif str(input_dict['debt_type']) == 'Monthly':
        rent -= input_dict['debt']
    elif str(input_dict['debt_type']) == 'Bi-Weekly':
        rent -= input_dict['debt']*26/12

    params = {'search_distance': 5,
        # 'postal': 80206,
        # 'max_price': 0,
        'max_price': rent,
        # 'min_bedrooms': int(request.form['beds']),
        # 'max_bedrooms': 1,
        # 'minSqft': 400,
        'availabilityMode': 1,
        # 'pets_dog': request.form['dogs'],
        # 'pets_cat': request.form['cats'],
        'sale_date': 'all+dates'}
    listings = CraigslistScraper(str(input_dict['city']), params)
    listings.scrape()
    listings._listing_build()
    listings = [listing for listing in listings.db.find({'lat': {'$exists':True}})]
    return render_template('form/submit.html', url=url, listings=listings)

# @app.route('/budget', methods=['GET','POST'])
# def budget():
#     """Render a page containing a textarea input where the user can either paste an
#     article or a url to be classified.  """
#     return render_template('form/budget.html')
#
# @app.route('/predict', methods=['GET','POST'])
# def predict():
#     """Recieve the article to be classified from an input form and use the
#     model to calculate popularity and make recomendations
#     """
#     data = str(request.form['article_body'])
#     pred = str(model.predict([data])[0])
#     return render_template('form/predict.html', article=data, predicted=pred)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, threaded=True)
    # ip_address = socket.gethostbyname("")
    # print("attempting to register %s:%d" % (ip_address, PORT))
    # register_for_ping(ip_address, str(PORT))
    #
    # # Start Flask app
    # app.run(host='0.0.0.0', port=PORT, debug=True)
    #
    # my_ip = socket.gethostbyname("")
    # my_port = 5000
    # register_for_ping(my_ip, my_port)
    # app.run(host='0.0.0.0', debug=False, threaded=True)

# from flask import Flask, render_template, request, jsonify
# import pickle
# import json
# import requests
# import socket
# import time
# from datetime import datetime
# import re
# import pandas as pd
# import ast
#
#
# app = Flask(__name__)
# PORT = 5000
# # REGISTER_URL = "http://10.3.0.79:5000/register"
# REGISTER_URL = "http://galvanize-case-study-on-fraud.herokuapp.com/data_point"
# DATA = []
# TIMESTAMP = []
#
# with open('../src/model.pkl', 'rb') as f:
#     model = pickle.load(f)
#
# @app.route('/', methods=['GET'])
# def index():
#     """Render a simple splash page."""
#     return render_template('form/index.html')
#
# @app.route('/score', methods=['POST'])
# def score():
#     """Recieve live stream data to be classified from an input form and use the
#     model to classify.
#     """
#     url = 'http://galvanize-case-study-on-fraud.herokuapp.com/data_point'
#     r = requests.get(REGISTER_URL)
#     def cleanhtml(raw_html):
#         cleanr = re.compile('<.*?>')
#         almost = re.sub(cleanr, '', raw_html)
#         cleantext = re.sub(r'\s+', ' ', almost, flags=re.UNICODE)
#         return cleantext
#     new = cleanhtml(r.text)
#     # df = pd.read_json(new)
#     # r = json.dumps(request.json, sort_keys=True, indent=4, separators=(',', ': '))
#     # new = model(r)
#     event_dict = ast.literal_eval(new)
#     org = "Is '"+str(event_dict['org_name'])+"' up to no good?"
#     prediction = 'Probably'
#
#     return render_template('form/score.html', org_name=org, pred=prediction)#, article=data, predicted=pred)
#
#
# def register_for_ping(ip, port):
#     registration_data = {'ip': ip, 'port': port}
#     requests.post(REGISTER_URL, data=registration_data)
#
#
# if __name__ == '__main__':
#     my_ip = socket.gethostbyname("")
#     my_port = 5000
#     register_for_ping(my_ip, my_port)
#     app.run(host='0.0.0.0', debug=False, threaded=True)
