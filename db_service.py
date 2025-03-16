import os
import json
import pandas as pd
from datetime import datetime
from pymongo import MongoClient
from pymongo.server_api import ServerApi

class DatabaseService:
    def __init__(self, config):
        self.config = config
        self.using_mongodb = bool(config.get("mongodb_uri"))
        
        if self.using_mongodb:
            try:
                # Connect to MongoDB
                self.client = MongoClient(config["mongodb_uri"], server_api=ServerApi('1'))
                self.db = self.client[config["db_name"]]
                print("Connected to MongoDB")
            except Exception as e:
                print(f"MongoDB connection error: {str(e)}")
                self.using_mongodb = False
        
        # Set up file storage as fallback
        self.data_dir = os.path.join(os.path.dirname(__file__), "data")
        os.makedirs(self.data_dir, exist_ok=True)
    
    def save_data(self, collection_name, data):
        """Save data to database or file"""
        # Add timestamp if not present
        if "timestamp" not in data:
            data["timestamp"] = datetime.now().isoformat()
        
        if self.using_mongodb:
            try:
                # Save to MongoDB
                collection = self.db[collection_name]
                result = collection.insert_one(data)
                return str(result.inserted_id)
            except Exception as e:
                print(f"MongoDB save error: {str(e)}")
                # Fall back to file storage
        
        # Save to file
        file_path = os.path.join(self.data_dir, f"{collection_name}.json")
        
        # Load existing data
        existing_data = []
        if os.path.exists(file_path):
            try:
                with open(file_path, "r") as f:
                    existing_data = json.load(f)
            except:
                existing_data = []
        
        # Add new data
        existing_data.append(data)
        
        # Save updated data
        with open(file_path, "w") as f:
            json.dump(existing_data, f, indent=2)
        
        return "saved_to_file"
    
    def load_data(self, collection_name, query=None):
        """Load data from database or file"""
        if self.using_mongodb:
            try:
                # Load from MongoDB
                collection = self.db[collection_name]
                if query:
                    cursor = collection.find(query)
                else:
                    cursor = collection.find()
                
                # Convert to DataFrame
                data = list(cursor)
                if data:
                    return pd.DataFrame(data)
                else:
                    return pd.DataFrame()
            except Exception as e:
                print(f"MongoDB load error: {str(e)}")
                # Fall back to file storage
        
        # Load from file
        file_path = os.path.join(self.data_dir, f"{collection_name}.json")
        if os.path.exists(file_path):
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)
                
                if data:
                    return pd.DataFrame(data)
            except:
                pass
        
        return pd.DataFrame()
    
    def update_data(self, collection_name, query, update_data):
        """Update data in database or file"""
        if self.using_mongodb:
            try:
                # Update in MongoDB
                collection = self.db[collection_name]
                result = collection.update_one(query, {"$set": update_data})
                return result.modified_count
            except Exception as e:
                print(f"MongoDB update error: {str(e)}")
                # Fall back to file storage
        
        # Update in file
        file_path = os.path.join(self.data_dir, f"{collection_name}.json")
        if os.path.exists(file_path):
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)
                
                # Find and update matching item
                updated = False
                for item in data:
                    match = True
                    for key, value in query.items():
                        if key not in item or item[key] != value:
                            match = False
                            break
                    
                    if match:
                        for key, value in update_data.items():
                            item[key] = value
                        updated = True
                        break
                
                # Save updated data
                with open(file_path, "w") as f:
                    json.dump(data, f, indent=2)
                
                return 1 if updated else 0
            except:
                pass
        
        return 0