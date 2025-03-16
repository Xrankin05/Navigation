import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import pandas as pd

# Define the scope
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Load credentials from environment variable 
# Set GOOGLE_CREDENTIALS enviromnental variable to the your cloud credential key
# Via the linux command " $env:GOOGLE_CREDENTIALS="C:\Path\To\Program\Folder\yourkey.json "
creds_path = os.getenv("GOOGLE_CREDENTIALS")
if not creds_path or not os.path.exists(creds_path):
    raise FileNotFoundError("Please set the GOOGLE_CREDENTIALS environment variable to the path of your credentials.json file.")

creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
client = gspread.authorize(creds)

# Open the Google Sheets
spreadsheet = client.open_by_key("1idOzW4T52Sr69Eazpn_BMcNQFvLTeBYo4Nj258uFZMU") # Sheet with accessibility information.
companiesSheet = client.open_by_key("1-t_5-twXtjssF3e1OVUAEs8LscrXC3KiedAuUgqjFPA") # Sheet with business location information.
# Access the street accessibility data
streetInfo = spreadsheet.worksheet("Street_Accessibility_Info")
# Access the Business location data
businessInfo = companiesSheet.worksheet("Business_Info")
# Store all data
streetData = streetInfo.get_all_records()
businessData = businessInfo.get_all_records()
# Put the data into a dataFrame for easier manipulation.
streetDataFrame = pd.DataFrame(streetData)
businessDataFrame = pd.DataFrame(businessData)
print(streetDataFrame)
print("\n ----------------------------")
print(businessDataFrame)