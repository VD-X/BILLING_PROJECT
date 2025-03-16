from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# Connection string with URL-encoded password (@ becomes %40)
uri = "mongodb+srv://VDX:VDX%40018238@cluster0.tqqoa.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
    
    # Create the grocery_billing database if it doesn't exist
    db = client["grocery_billing"]
    
    # List available databases
    print("\nAvailable databases:")
    for db_name in client.list_database_names():
        print(f"- {db_name}")
    
    print("\nConnection test completed successfully!")
    
except Exception as e:
    print(f"Connection error: {e}")