
# server.py

from flask import Flask, request, Response, render_template
from db import *
from dateutil import parser
from bson import json_util, ObjectId
import json

import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import numpy as np
import tensorflow
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.preprocessing import StandardScaler

def fetch_x_most_recent(cluster, limit=206):
  return list(cluster.aggregate([
      {"$sort": {"timestamp": -1}},
      {"$limit": limit}
  ]))[::-1]

def make_prediction(cluster):
  x, y, z = [], [], []
  recent_data = fetch_x_most_recent(cluster)
  for data in recent_data:
    x.append(data['accel_x'])
    y.append(data['accel_y'])
    z.append(data['accel_z'])
    
  parent_dir =  os.path.dirname(os.getcwd())
  cnn_model = tensorflow.keras.models.load_model(parent_dir + "\ML\model_cnn.keras")

  accel_data = np.column_stack((x, y, z))

  scaler = StandardScaler()
  accel_data_reshaped = accel_data.reshape(-1, 3)
  accel_data_scaled = scaler.fit_transform(accel_data_reshaped)
  accel_data_scaled = accel_data_scaled.reshape(1, 206, 3)

  cnn_pred = cnn_model.predict(accel_data_scaled)
 
  return ("1" if cnn_pred[0][0] > 0.5 else "0")
  

def create_app():
  vars = {}
  with open('env.txt', 'r', encoding='utf-8') as file:
    for line in file:
      varpair = line.split()
      vars[varpair[0]] = varpair[1]


  uri = vars['CONNECTION_URI']
  cluster = get_collection(uri, 'bithacks2025', 'bithacks2025')
  if ('remove' in vars and vars['remove'] == 'true'):
    empty_db(cluster)

  print(list(cluster.find()))
  for v in cluster.find():
    print(v)

  app = Flask(__name__)

  @app.route('/', methods=['GET'])
  def base():
    if request.method == 'GET':
      return json.loads(json_util.dumps(list(cluster.find()))), 200, {'Content-Type': 'application/json'}

  @app.route('/insert-single/', methods=['GET', 'POST'])
  def insert_single():

    if request.method == 'GET':
        return json.loads(json_util.dumps(list(cluster.find()))), 200, {'Content-Type': 'application/json'}

    data = None
    try:
      data = request.get_json()
    except:
      data = request.data
    try:
      data['timestamp'] = parser.parse(data['timestamp'])
      cluster.insert_one(data)
      return make_prediction(cluster), 201, {'Content-Type': 'application/json'}
    except:
      pass
      # return {'err': 'an error posting single data point'}, 500, {'Content-Type': 'application/json'}


  @app.route('/insert-batch/', methods=['GET', 'POST'])
  def insert_batch():

    if request.method == 'GET':
        return json.loads(json_util.dumps(list(cluster.find()))), 200, {'Content-Type': 'application/json'}

    data = None
    try:
      data = request.get_json()
    except:
      data = request.data

    try:
      for points in data['data']:
        points['timestamp'] = parser.parse(points['timestamp'])
      cluster.insert_many(data['data'])
      return make_prediction(cluster), 201, {'Content-Type': 'application/json'}
    except:
      pass
      # return {'err': 'an error posting batch data points'}, 500, {'Content-Type': 'application/json'}
    
  @app.route('/client/', methods=['GET'])
  def client():
    if request.method == 'GET':
      return render_template('client.html', points=[{k: v for k, v in d.items() if k != '_id'} for d in list(cluster.find())])  # Ensure 'client.html' is in the 'templates' folder


  @app.route('/recent/', methods=['GET'])
  def recent():
    if request.method == 'GET':
      return render_template('client.html', points=[{k: v for k, v in d.items() if k != '_id'} for d in fetch_x_most_recent(cluster)])  # Ensure 'client.html' is in the 'templates' folder


  return app