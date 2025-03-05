import pandas as pd
import os
from datetime import datetime

class DataManager:
    def __init__(self):
        self.file_path = "personal_data.csv"
        self.create_file_if_not_exists()

    def create_file_if_not_exists(self):
        if not os.path.exists(self.file_path):
            # Create an empty DataFrame with the required columns
            df = pd.DataFrame(columns=['Name', 'Location', 'Event', 'Hours', 'Timestamp'])
            df.to_csv(self.file_path, index=False)

    def get_all_people(self):
        df = pd.read_csv(self.file_path)
        # Convert all names to lowercase for comparison, then use unique with case preservation
        unique_names = []
        seen_lower = set()
        
        for name in df['Name']:
            if name.lower() not in seen_lower:
                seen_lower.add(name.lower())
                unique_names.append(name)
                
        # Sort alphabetically (case-insensitive)
        return sorted(unique_names, key=lambda x: x.lower())

    def add_person_info(self, name, location, event, hours, date=None):
        try:
            df = pd.read_csv(self.file_path)
            
            # Check if name exists (case-insensitive), use the original case if found
            matching_names = df[df['Name'].str.lower() == name.lower()]['Name'].unique()
            if len(matching_names) > 0:
                # Use the first instance we found to maintain case consistency
                name_to_use = matching_names[0]
            else:
                name_to_use = name
            
            # Generate timestamp - if date is provided, use it as the date part
            if date and date.strip():
                try:
                    # Parse the provided date and combine with current time
                    date_obj = datetime.strptime(date, "%Y-%m-%d")
                    current_time = datetime.now().time()
                    combined_datetime = datetime.combine(date_obj.date(), current_time)
                    timestamp = combined_datetime.strftime("%Y-%m-%d %H:%M:%S")
                except ValueError:
                    # If date parsing fails, use current datetime
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            else:
                # Use current datetime if no date provided
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
            new_data = {
                'Name': [name_to_use],
                'Location': [location],
                'Event': [event],
                'Hours': [hours],
                'Timestamp': [timestamp]
            }
            df = pd.concat([df, pd.DataFrame(new_data)], ignore_index=True)
            df.to_csv(self.file_path, index=False)
            return True, "Information added successfully!"
        except Exception as e:
            return False, f"Error saving data: {str(e)}"

    def get_person_info(self, name):
        df = pd.read_csv(self.file_path)
        # Case-insensitive match
        person_data = df[df['Name'].str.lower() == name.lower()]
        return person_data.to_dict('records')

    def add_new_person(self, name):
        if not name.strip():
            return False, "Name cannot be empty!"

        df = pd.read_csv(self.file_path)
        # Case-insensitive check for duplicates
        if any(existing_name.lower() == name.lower() for existing_name in df['Name'].unique()):
            return False, "Person already exists (name is case-insensitive)!"

        # Add the person with initial empty information
        new_data = {
            'Name': [name],
            'Location': [''],
            'Event': [''],
            'Hours': [''],
            'Timestamp': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        }
        df = pd.concat([df, pd.DataFrame(new_data)], ignore_index=True)
        df.to_csv(self.file_path, index=False)
        return True, "Person added successfully!"
        
    def get_all_entries(self):
        """Get all entries in the database"""
        df = pd.read_csv(self.file_path)
        return df.to_dict('records')
        
    def import_and_merge_entries(self, import_file_path):
        """Import and merge entries from another CSV file"""
        try:
            # Check if the import file exists
            if not os.path.exists(import_file_path):
                return False, "Import file not found!"
                
            # Read the current data and the import data
            current_df = pd.read_csv(self.file_path)
            import_df = pd.read_csv(import_file_path)
            
            # Ensure the import file has the required columns
            required_columns = ['Name', 'Location', 'Event', 'Hours', 'Timestamp']
            missing_columns = [col for col in required_columns if col not in import_df.columns]
            if missing_columns:
                return False, f"Import file is missing required columns: {', '.join(missing_columns)}"
            
            # Merge the dataframes
            merged_df = pd.concat([current_df, import_df], ignore_index=True)
            
            # Remove exact duplicates
            merged_df = merged_df.drop_duplicates()
            
            # Save the merged data
            merged_df.to_csv(self.file_path, index=False)
            
            return True, f"Successfully imported {len(import_df)} entries. After removing duplicates, database now has {len(merged_df)} entries."
        except Exception as e:
            return False, f"Error importing data: {str(e)}"
            
    def delete_entry(self, name, timestamp, location, event, hours):
        """Delete a specific entry from the database"""
        try:
            df = pd.read_csv(self.file_path)
            
            # Create a mask for the exact entry to delete
            mask = (
                (df['Name'] == name) & 
                (df['Timestamp'] == timestamp) & 
                (df['Location'] == location) & 
                (df['Event'] == event) & 
                (df['Hours'] == hours)
            )
            
            # Delete the matching row(s)
            df = df[~mask]
            
            # Save the updated dataframe
            df.to_csv(self.file_path, index=False)
            
            return True
        except Exception as e:
            print(f"Error deleting entry: {str(e)}")
            return False
            
    def add_entry(self, name, timestamp, location, event, hours):
        """Add an entry with an existing timestamp (for undo functionality)"""
        try:
            df = pd.read_csv(self.file_path)
            
            new_data = {
                'Name': [name],
                'Location': [location],
                'Event': [event],
                'Hours': [hours],
                'Timestamp': [timestamp]
            }
            
            df = pd.concat([df, pd.DataFrame(new_data)], ignore_index=True)
            df.to_csv(self.file_path, index=False)
            
            return True
        except Exception as e:
            print(f"Error adding entry: {str(e)}")
            return False
            
    def get_password(self):
        """Get the saved admin password or return default if not set"""
        password_file = "admin_password.txt"
        default_password = "admin123"
        
        if not os.path.exists(password_file):
            # Create password file with default password
            with open(password_file, 'w') as f:
                f.write(default_password)
            return default_password
        
        # Read password from file
        try:
            with open(password_file, 'r') as f:
                password = f.read().strip()
                return password if password else default_password
        except:
            return default_password
            
    def change_password(self, current_password, new_password):
        """Change the admin password"""
        saved_password = self.get_password()
        
        if current_password != saved_password:
            return False, "Current password is incorrect"
            
        try:
            with open("admin_password.txt", 'w') as f:
                f.write(new_password)
            return True, "Password changed successfully"
        except Exception as e:
            return False, f"Error changing password: {str(e)}"