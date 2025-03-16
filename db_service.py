import pymongo
import pandas as pd
import os
from datetime import datetime
import streamlit as st

class DatabaseService:
    def __init__(self, config):
        self.config = config
        self.is_cloud = config["is_cloud"]
        
        try:
            # Try to connect to MongoDB
            self.client = pymongo.MongoClient(config["mongodb_uri"], serverSelectionTimeoutMS=5000)
            # Verify connection
            self.client.server_info()
            self.db = self.client[config["db_name"]]
            self.using_mongodb = True
        except Exception as e:
            # Fall back to file-based storage if MongoDB connection fails
            self.using_mongodb = False
            st.warning(f"MongoDB connection failed. Using file-based storage instead.")
            # Ensure data directory exists
            self.data_dir = os.path.join(os.path.dirname(__file__), 'data')
            os.makedirs(self.data_dir, exist_ok=True)
    
    def save_data(self, collection_name, data):
        """Save data to MongoDB collection or file"""
        if self.using_mongodb:
            collection = self.db[collection_name]
            
            # Convert DataFrame to records if needed
            if isinstance(data, pd.DataFrame):
                records = data.to_dict('records')
                if records:
                    collection.insert_many(records)
            else:
                collection.insert_one(data)
        else:
            # Save to file
            file_path = os.path.join(self.data_dir, f"{collection_name}.csv")
            
            if isinstance(data, pd.DataFrame):
                # If file exists, append to it
                if os.path.exists(file_path):
                    existing_data = pd.read_csv(file_path)
                    updated_data = pd.concat([existing_data, data], ignore_index=True)
                    updated_data.to_csv(file_path, index=False)
                else:
                    data.to_csv(file_path, index=False)
            else:
                # Convert dict to DataFrame
                df = pd.DataFrame([data])
                
                # If file exists, append to it
                if os.path.exists(file_path):
                    existing_data = pd.read_csv(file_path)
                    updated_data = pd.concat([existing_data, df], ignore_index=True)
                    updated_data.to_csv(file_path, index=False)
                else:
                    df.to_csv(file_path, index=False)
        
        return True
    
    def load_data(self, collection_name, query=None):
        """Load data from MongoDB collection or file"""
        if self.using_mongodb:
            collection = self.db[collection_name]
            
            if query is None:
                query = {}
                
            data = list(collection.find(query))
            
            # Remove MongoDB _id field for clean DataFrame
            for item in data:
                if '_id' in item:
                    item['_id'] = str(item['_id'])  # Convert ObjectId to string
            
            return pd.DataFrame(data) if data else pd.DataFrame()
        else:
            # Load from file
            file_path = os.path.join(self.data_dir, f"{collection_name}.csv")
            
            if os.path.exists(file_path):
                return pd.read_csv(file_path)
            
            return pd.DataFrame()
    
    def update_data(self, collection_name, query, update_data):
        """Update data in MongoDB collection or file"""
        if self.using_mongodb:
            collection = self.db[collection_name]
            result = collection.update_one(query, {"$set": update_data})
            return result.modified_count > 0
        else:
            # Update in file
            file_path = os.path.join(self.data_dir, f"{collection_name}.csv")
            
            if os.path.exists(file_path):
                df = pd.read_csv(file_path)
                
                # Find matching rows
                mask = True
                for key, value in query.items():
                    mask = mask & (df[key] == value)
                
                # Update matching rows
                for key, value in update_data.items():
                    df.loc[mask, key] = value
                
                df.to_csv(file_path, index=False)
                return True
            
            return False
    
    def delete_data(self, collection_name, query):
        """Delete data from MongoDB collection or file"""
        if self.using_mongodb:
            collection = self.db[collection_name]
            result = collection.delete_many(query)
            return result.deleted_count > 0
        else:
            # Delete from file
            file_path = os.path.join(self.data_dir, f"{collection_name}.csv")
            
            if os.path.exists(file_path):
                df = pd.read_csv(file_path)
                
                # Find matching rows
                mask = True
                for key, value in query.items():
                    mask = mask & (df[key] == value)
                
                # Remove matching rows
                df = df[~mask]
                df.to_csv(file_path, index=False)
                return True
            
            return False