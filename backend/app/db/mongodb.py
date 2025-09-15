from pymongo import MongoClient
import urllib.parse

username = "vorlve_log_db"
password = urllib.parse.quote_plus("Niffier1811")
client = MongoClient("mongodb+srv://vorlve_log_db:Niffier1811@cluster0.9l7c0l2.mongodb.net/?retryWrites=true&w=majority&tls=true&appName=Cluster0")
mongo_db = client["activity_logs"]

def get_activity_collection():
    return mongo_db["logs"]