import datetime
import json
import logging
import time
import pandas as pd
import os
import requests
import http.client


CALENDAR_BY_DIST_URL  = 'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?state_id=' #571&date=04-05-2021
TARGET_DATE = datetime.date(2021, 5, 2)

START_DATE = datetime.date(2021, 4, 29)
END_DATE  = datetime.date(2021, 5, 22)

def saveResponse(name, json_data):
    with open('./data/' + name + '.json', 'w') as json_file:
        json.dump(json_data, json_file)


def main():
    logging.info('====Start CoWIN Availability====')
    with open('./data/districts.json') as json_file:
        districts = json.load(json_file)

    summaries = []

    for day in pd.date_range(start=START_DATE.strftime('%Y-%m-%d'), end=END_DATE.strftime('%Y-%m-%d'), freq='7D'):        
        for district in districts:
            summary = {}
            summary['date'] = day.strftime('%d-%m-%Y')
            summary['state_id'] = district['state_id']
            summary['district_id'] = district['district_id']
            summary['district_name'] = district['district_name']
            url = CALENDAR_BY_DIST_URL + str(district['state_id']) + '&district_id=' + str(district['district_id']) + '&date=' + day.strftime('%d-%m-%Y')
            logging.debug(url)
            response = requests.get(url)
            if (response.status_code == http.HTTPStatus.UNAUTHORIZED.value):
                logging.debug('Error saving state ' + str(district['state_id']) + ' and ' + str(district['district_id']) + 'for date' + TARGET_DATE.strftime('%d-%m-%Y'))
                continue
            else:
                centers = json.loads(response.text)['centers']
                summary['centers'] = len(centers)

                logging.debug(str(len(centers)) + ' in ' + str(district['state_id']) + ' and ' + str(district['district_id']))
                if(len(centers) > 0 ):
                    saveResponse('Centers_' + str(district['district_id']) + '_' + TARGET_DATE.strftime('%d-%m-%Y'),centers)
                    available_centers = [c for c in centers if any(s for s in c['sessions'] if s['min_age_limit'] != 45)]
                    paid_centers = [c for c in centers if c["fee_type"] != "Free"]
                    summary['paid_centers'] = paid_centers
                    summary['centers_18'] = available_centers
                    if(len(paid_centers) > 0):
                        saveResponse('Paid_Centers_' + str(district['district_id']) + '_' + TARGET_DATE.strftime('%d-%m-%Y'),paid_centers)                    
                    if(len(available_centers) > 0):
                        saveResponse('Available_18_Centers_' + str(district['district_id']) + '_' + TARGET_DATE.strftime('%d-%m-%Y'),available_centers)
            summaries.append(summary)
    saveResponse('Summaries', summaries)

if __name__ == "__main__":
    logging.basicConfig(filename='CoWINAvailability_' + time.strftime("%Y%m%d-%H%M%S") +
                        '.log', format='%(asctime)s %(message)s', level=logging.DEBUG)
    main()
