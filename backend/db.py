
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

def get_database(uri, database):
  # Create a new client and connect to the server
  client = MongoClient(uri, server_api=ServerApi('1'))
  # Send a ping to confirm a successful connection
  try:
      client.admin.command('ping')
      print("Pinged your deployment. You successfully connected to MongoDB!")
  except Exception as e:
      print(e)

  return client[database]


def get_collection(uri, database, collection):
  print('getting collection')
  return get_database(uri, database)[collection]


