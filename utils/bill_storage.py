import pandas as pd
import os

def save_bill_to_master(bill_data, master_file_path=None):
    """
    Save bill data to a master Excel file.
    
    Args:
        bill_data (pd.DataFrame): DataFrame containing the bill data
        master_file_path (str, optional): Path to the master file. If None, a default path is used.
    
    Returns:
        str: Path to the master file
    """
    # Set default master file path if not provided
    if master_file_path is None:
        master_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                        'data', 'master_bills.xlsx')
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(master_file_path), exist_ok=True)
    
    # Check if the master file already exists
    if os.path.exists(master_file_path):
        try:
            # Read existing data
            existing_data = pd.read_excel(master_file_path)
            
            # Append new data
            combined_data = pd.concat([existing_data, bill_data], ignore_index=True)
            
            # Save the combined data
            combined_data.to_excel(master_file_path, index=False)
        except Exception as e:
            print(f"Error appending to master file: {e}")
            # If there's an error, create a new file
            bill_data.to_excel(master_file_path, index=False)
    else:
        # Create a new master file
        bill_data.to_excel(master_file_path, index=False)
    
    return master_file_path