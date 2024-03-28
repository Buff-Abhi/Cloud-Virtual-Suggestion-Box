# Import Dependencies
from flask import Flask, request, Response, session, render_template, redirect, url_for
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from google.logging.type import log_severity_pb2 as severity
from google.cloud import storage
from xlsxwriter import Workbook
from datetime import timedelta
import googleapiclient.discovery
import google.cloud.logging
import google.auth
import pandas as pd
import jsonpickle
import requests
import logging
import redis
import json
import os

# Google Authentication
credentials, project = google.auth.default()

# Logging
logging_client = google.cloud.logging.Client()
logger = logging_client.logger('Virtual-Box')
logger.log_text('Virtual Box - Logging Enabled', severity='DEBUG')

# VM Instance External IP Address
service = googleapiclient.discovery.build('compute', 'v1', credentials=credentials)
compute = googleapiclient.discovery.build('compute', 'v1')
inst = compute.instances().list(project='datacenter-project-370219', zone='us-east1-b').execute()
item = inst.get('items')
item_str = json.dumps(item)
split1 = item_str.split('"natIP": ')
split2 = split1[1].split(',')
ext_ip = split2[0].replace('"','')
logger.log_text('External IP of the VM is:'+ext_ip, severity='DEBUG')

# Vader Sentiment Analyzer
sentiment = SentimentIntensityAnalyzer()

# Initialize Flask Application
app = Flask(__name__)

# Google Storage
storage_client = storage.Client()
bucket_name = "abhi-datacenter-bucket"
bucket = storage_client.get_bucket(bucket_name)

# Global Variables
flask_url = 'http://'+ext_ip+':8080/'
excel_filepath = '/home/abhi_buff/GCP/'
data_dict = {'Message':[], 'Sentiment':[], 'Location':[]}
box_list = []

# REST API Endpoint - Landing Page
@app.route('/', methods=['GET', 'POST'])
def land():
    logger.log_text('Received a hit on Endpoint /', severity='DEBUG')
    return redirect(flask_url+'box')

# REST API Endpoint - Create Box
@app.route('/box', methods=['GET', 'POST'])
def create_box():
    logger.log_text('Received a hit on Endpoint /box', severity='DEBUG')
    global box_list
    error = None
    if request.method == 'POST':
        if request.form['boxname'] != '':
            box_name = request.form['boxname']
            box_url = flask_url+'box/'+box_name
            box_list.append(box_name)
            logger.log_text('Box '+box_name+' has been created.', severity='DEBUG')
            box_list_str = ''.join(box_list)
            logger.log_text('Global Box List: '+box_list_str, severity='DEBUG')
            return redirect(box_url+'/close')
        else:
            error = 'Box name cannot be empty!'
    return render_template('createbox.html', error=error)

# REST API Endpoint - Enter Feedback
@app.route('/box/<name>', methods=['GET', 'POST'])
def new(name):
    logger.log_text('Received a hit on Endpoint /box/'+name, severity='DEBUG')
    global box_list
    box_list_str = ''.join(box_list)
    logger.log_text('Global Box List: '+box_list_str, severity='DEBUG')
    if name not in box_list:
        return 'Invalid URL!'
    if request.method == 'POST':
        message = request.form['message']
        redis.lpush(name, message)
        return 'Thank you for providing the feedback!'
    return render_template('message.html')

# REST API Endpoint - Close Box
@app.route('/box/<name>/close', methods=['GET', 'POST'])
def close(name):
    logger.log_text('Received a hit on Endpoint /box/'+name+'/close', severity='DEBUG')
    global box_list
    error = None
    if request.method == 'POST':
        response = redis.lrange(name, 0, -1)
        data_dict = {'Message':[], 'Sentiment':[], 'Location':[]}
        for x in response:
            prepare_excel_data(x, data_dict)
        write_excel(data_dict, name)
        write_to_bucket(name)
        delete_from_redis(name)
        delete_excel(name)
        box_list.remove(name)
        box_list_str = ''.join(box_list)
        logger.log_text('Box '+name+' has been closed.', severity='DEBUG')
        logger.log_text('Global Box List: '+box_list_str, severity='DEBUG')
        return Response(response=json.dumps(data_dict, indent=4), status=200, mimetype="application/json")
    return render_template('close.html', variable=flask_url+'box/'+name, error=error)

# Local Method - Prepare Excel Data
def prepare_excel_data(response, data_dict):
    logger.log_text('Received a hit on Method prepare_excel_data', severity='DEBUG')
    message = response.decode('utf-8')
    data_dict['Message'].append(message)
    data_dict['Sentiment'].append(get_sentiment(message))
    data_dict['Location'].append(get_location(request.remote_addr))

# Local Method - Delete Redis Data
def delete_from_redis(key):
    logger.log_text('Received a hit on Method delete_from_redis with key '+key, severity='DEBUG')
    redis.delete(key)

# Local Method - Delete Excel
def delete_excel(name):
    logger.log_text('Received a hit on Method delete_excel with name '+name, severity='DEBUG')
    global excel_filepath
    if os.path.exists(excel_filepath+name+'_temp.xlsx'):
        os.remove(excel_filepath+name+'_temp.xlsx')

# Local Method - Create Excel
def write_excel(data, name):
    logger.log_text('Received a hit on Method create_excel with name '+name, severity='DEBUG')
    global excel_filepath
    df = pd.DataFrame(data)
    writer = pd.ExcelWriter(excel_filepath+name+'_temp.xlsx')
    df.to_excel(writer, index=False)
    writer.save()

# Local Method - Upload Excel to Bucket
def write_to_bucket(name):
    logger.log_text('Received a hit on Method write_to_bucket with name '+name, severity='DEBUG')
    global excel_filepath
    blob = bucket.blob(name+'.xlsx')
    blob.upload_from_filename(excel_filepath+name+'_temp.xlsx')

# Local Method - Sentiment Analysis
def get_sentiment(message):
    logger.log_text('Received a hit on Method get_sentiment for message '+message, severity='DEBUG')
    sentiment_value = sentiment.polarity_scores(message)['compound']
    if(sentiment_value > 0):
        zsentiment = 'Positive'
    elif(sentiment_value < 0):
        zsentiment = 'Negative'
    else:
        zsentiment = 'Neutral'
    return zsentiment + ' - {}'.format(sentiment_value)

# Local Method - IP Trace
def get_location(ip_address):
    logger.log_text('Received a hit on Method get_location for IP '+ip_address, severity='DEBUG')
    response = requests.get(f'https://ipapi.co/{ip_address}/json/').json()
    return response

# Redis Connection
pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
redis = redis.Redis(connection_pool=pool)

# Run Flask Application
app.run(debug=True, host="0.0.0.0", port=8080)
