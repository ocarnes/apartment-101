from flask import Flask, render_template, request, jsonify
import pickle
import json
import requests
import socket
import time
from datetime import datetime
import re
import pandas as pd
import ast
import os


app = Flask(__name__)

with open('model.pkl', 'rb') as f:
    model = pickle.load(f)

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
    return render_template('form/submit.html')

@app.route('/budget', methods=['GET','POST'])
def budget():
    """Render a page containing a textarea input where the user can either paste an
    article or a url to be classified.  """
    return render_template('form/budget.html')

@app.route('/predict', methods=['GET','POST'])
def predict():
    """Recieve the article to be classified from an input form and use the
    model to calculate popularity and make recomendations
    """
    data = str(request.form['article_body'])
    pred = str(model.predict([data])[0])
    return render_template('form/predict.html', article=data, predicted=pred)

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
