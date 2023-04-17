from pymongo import MongoClient
import os
from dotenv import load_dotenv, dotenv_values
config = dotenv_values(".env")
load_dotenv()

def getDB():
    cluster=MongoClient(os.getenv('Mongo_URI'))
    db=cluster['Bo__training']
    return db  