#
from __future__ import print_function
import os.path
# import settings for Line notify
import notify
# import all needed keys
import creds

#import pdb

from datetime import datetime
import time
import requests

####### Read Google Sheet data ######

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from google.oauth2 import service_account

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'google_keys.json'


google_creds = None
google_creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)


# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = '18yRZu4DHzasAKjoBWcVpD4GQ0pPsKZO8aEJgnRdtBJU'
# SPREADSHEET_READ_RANGE = 'prices!A1:C10'
SPREADSHEET_WRITE_RANGE = 'results!A2'

# Search keys row
SPREADSHEET_PRICE = 'search!A2'
SPREADSHEET_KEYS_READ_RANGE = 'search!B1:L1'
SPREADSHEET_VALUES_READ_RANGE = 'search!B2:L2'
SPREADSHEET_RESULTS_WRITE_RANGE = 'results!B2'


service = build('sheets', 'v4', credentials=google_creds)

# Call the Sheets API
sheet = service.spreadsheets()
########

url = "https://skyscanner44.p.rapidapi.com/search-extended"


# TO DO: set the query based on google sheet

# Get the keys from the sheet
print('reading sheet')
result_price = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                            range=SPREADSHEET_PRICE).execute()

sheet_price = result_price.get('values', [])

result_keys = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                            range=SPREADSHEET_KEYS_READ_RANGE).execute()

search_keys = result_keys.get('values', [])
# print(search_keys)

# Get the values from the sheet
result_values = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                            range=SPREADSHEET_VALUES_READ_RANGE).execute()

search_values = result_values.get('values', [])
# print(search_values)

# search_keys = ['adults', 'origin', 'destination', 'departureDate', 'returnDate', 'currency', 'stops', 'duration', 'startFrom', 'arriveTo', 'returnStartFrom', 'returnArriveTo']
# search_values = ['1', 'KIX', 'MXP', '2023-07-28', '2023-08-05', 'EUR', '0,1', '24', '0:00', '22:00', '0:00', '22:00']

querystring = dict(map(lambda i,j:(i,j) , search_keys[0],search_values[0]))
MAX_PRICE = int(sheet_price[0][0])
print('setting research data:')
print(querystring)
print(MAX_PRICE)
# querystring = {"adults":"1",
#                "origin":"KIX",
#                "destination":"MXP",
#                "departureDate":"2023-07-28",
#                "returnDate":"2023-08-05",
#                "currency":"EUR",
#                "stops":"0,1",
#                "duration":"24",
#                "startFrom":"00:00",
#                "arriveTo":"22:00",
#                "returnStartFrom":"00:00",
#                "returnArriveTo":"22:00"}

# querystring = {'adults': '1', 'origin': 'KIX', 'destination': 'MXP', 'departureDate': '2023-07-28', 'returnDate': '2023-08-05', 'currency': 'EUR', 'stops': '0,1', 'duration': '24', 'startFrom': '0:00', 'arriveTo': '22:00', 'returnStartFrom': '0:00', 'returnArriveTo': '22:00'}

headers = {
	"X-RapidAPI-Key": creds.skyscanner_api_key ,
	"X-RapidAPI-Host": "skyscanner44.p.rapidapi.com"
}


# MAX_PRICE = 1550

complete = False
matching_data = []
# loop until context status is complete
while not complete:
    # check status
    response = requests.get(url, headers=headers, params=querystring)
    result = response.json()
    status = result['context']['status']
    print(status)
    # pdb.set_trace()
    if status == 'complete':
        # save matching data
        for r in result['itineraries']['results']:
            for o in r['pricing_options']:
              if ('amount' in o['price']) and o['price']['amount'] <= MAX_PRICE:
                dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                # print(dt_string)
                # print(o['price']['amount'])
                price = o['price']['amount']
                # print(o['url'])
                url = o['url']
                # print(r['deeplink'])
                deeplink = r['deeplink']
                matching_data.append([dt_string, price, url, deeplink])
        if matching_data:
            print('found matching data')
            # update sheet
            request = sheet.values().append(spreadsheetId=SPREADSHEET_ID,
                                range=SPREADSHEET_WRITE_RANGE, valueInputOption='USER_ENTERED', body={"values":matching_data})
            response = request.execute()
            # print(response)
            # notify
            requests.post(notify.api_url, headers=notify.TOKEN_dic, data=notify.send_dic)
        complete = True
        # print(result)
    else:
        # if not complete wait for next call
        print("incomplete status:wait 3mins for next call")
        time.sleep(180)
