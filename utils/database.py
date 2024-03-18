
from pymongo.mongo_client import MongoClient
import dns.resolver

dns.resolver.default_resolver=dns.resolver.Resolver(configure=False)
dns.resolver.default_resolver.nameservers=['8.8.8.8']

def connect_to_db():
    username = 'Project-AI'
    pword = 'm5vr23zThUdemscI'

    uri = f"mongodb+srv://{username}:{pword}@atlascluster.doihstd.mongodb.net/?retryWrites=true&w=majority&appName=AtlasCluster"
    # Create a new client and connect to the server
    client = MongoClient(uri)
    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
        db = client['PurpleGirls']
        return db
    except Exception as e:
        print(e)
