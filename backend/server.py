
# server.py

from flask import Flask, request, Response
from db import *
from dateutil import parser
from bson import json_util, ObjectId
import json

def create_app():
  vars = {}
  with open('env.txt', 'r', encoding='utf-8') as file:
    for line in file:
      varpair = line.split()
      vars[varpair[0]] = varpair[1]


  uri = vars['CONNECTION_URI']
  cluster = get_collection(uri, 'bithacks2025', 'bithacks2025')
  print(dict(cluster.find()))
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
      return json.loads(json_util.dumps(list(cluster.find()))), 201, {'Content-Type': 'application/json'}
    except:
      return {'err': 'an error posting single data point'}, 500, {'Content-Type': 'application/json'}


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
      return json.loads(json_util.dumps(list(cluster.find()))), 201, {'Content-Type': 'application/json'}
    except:
      return {'err': 'an error posting batch data points'}, 500, {'Content-Type': 'application/json'}

  return app


