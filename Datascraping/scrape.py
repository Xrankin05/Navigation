import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

# Define the scope
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Load credentials from environment variable
creds_path = os.getenv("GOOGLE_CREDENTIALS")
if not creds_path or not os.path.exists(creds_path):
    raise FileNotFoundError("Please set the GOOGLE_CREDENTIALS environment variable to the path of your credentials.json file.")

creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
client = gspread.authorize(creds)

# Open the Google Sheet
sheet = client.open_by_key("1idOzW4T52Sr69Eazpn_BMcNQFvLTeBYo4Nj258uFZMU").sheet1
# Get and print all data
data = sheet.get_all_records()
print(data)