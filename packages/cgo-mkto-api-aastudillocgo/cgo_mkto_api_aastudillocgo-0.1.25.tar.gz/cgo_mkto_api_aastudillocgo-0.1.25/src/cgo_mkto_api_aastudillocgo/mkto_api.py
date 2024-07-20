from cgo_email_aastudillocgo import oauth2 as email
from datetime import datetime, timedelta

import requests
import time

import sys
#sys.path.insert(1, '../../utils/email')
#import oauth2



#from io import StringIO
#from io import BytesIO

#import configparser
#import pandas as pd
#import csv

# libraries to send files to GBQ
#from google.oauth2 import service_account
#from google.cloud import bigquery

def send_email(config, content):
  config['MAIL']['refresh_token'], config['MAIL']['access_token'], config['MAIL']['expires_in'] = email.send_email(config['MAIL'], 
  'Synchronization error', content)

  with open('config.ini','w') as configfile:
    config.write(configfile)

def get_global_access_token(config):

  if datetime.now() > datetime.strptime(config['MARKETOCREDENTIALS']['ATExpiration'],'%Y-%m-%d %H:%M:%S.%f'):

    IdentityURL = config['MARKETOCREDENTIALS']['IdentityURL']
    ClientID = config['MARKETOCREDENTIALS']['ClientID']
    ClientSecret = config['MARKETOCREDENTIALS']['ClientSecret']

    access_token_url = f"{IdentityURL}/oauth/token?grant_type=client_credentials&client_id={ClientID}&client_secret={ClientSecret}"

    print(access_token_url)

    result = requests.get(access_token_url)

    try:
      result_dict = result.json()
      config['MARKETOCREDENTIALS']['AccessToken'] = result_dict['access_token']
      config['MARKETOCREDENTIALS']['ATExpiration'] = str(datetime.now() + timedelta(seconds=result_dict['expires_in']))

      with open('config.ini','w') as configfile:
        config.write(configfile)

    except:
      error = 'Exception raised'
      print(error)
      send_email(config, f"{config['GLOBAL']['context']}: get_global_access_token function {error}")

  return config['MARKETOCREDENTIALS']['AccessToken']

def create_request_by_fields(config, fields, smart_list_id):
        
  bulkurl = config['MARKETOCREDENTIALS']['bulkurl']
  access_token = get_global_access_token(config)

  create_export_leads_url = f"{bulkurl}/v1/leads/export/create.json?access_token={access_token}"

  print(create_export_leads_url)

  headers = {'content-type': 'application/json'}

  #for a in kwargs:
  #  print(a, kwargs[a])  
  #  if len(kwargs[a]) == 1:
  #    #if a == "smart_list_id":
  #    config['MARKETOVARIABLES']['filename'] = kwargs[a][0]
  #    filters = {"smartListId": kwargs[a][0]}
  #  else:
  #    #elif a == "starting_creation_date":
  #    #filters = {"createdAt": {"startAt": kwargs[a],"endAt": kwargs["end_creation_date"]} }
  #    filters = {"createdAt": {"startAt": kwargs[a][0],"endAt": kwargs[a][1]} }

  filters = {"smartListId":smart_list_id}

  body = {"fields": eval(fields),"filter": filters}

  result = requests.post(create_export_leads_url, headers = headers, json = body)

  print(result.text)
  print("JSON")

  try:
    json_result = result.json()
    if json_result["success"]:
      config['MARKETOVARIABLES']['export_id'] = json_result["result"][0]["exportId"]
      config['MARKETOVARIABLES']['status'] = json_result["result"][0]["status"]
      with open('config.ini','w') as configfile:
        config.write(configfile)
  except:
    error = 'Exception raised'
    print(error)
    send_email(config, f"{config['GLOBAL']['context']}: create_request_by_fields function {error}")

def enqueue_request(config):

  print('enqueuing')

  bulkurl = config['MARKETOCREDENTIALS']['bulkurl']
  exportId = config['MARKETOVARIABLES']['export_id']
  access_token = get_global_access_token(config)

  enqueue_export_leads_url = f"{bulkurl}/v1/leads/export/{exportId}/enqueue.json?access_token={access_token}"

  print(enqueue_export_leads_url)

  headers = {'content-type': 'application/json'}
  result = requests.post(enqueue_export_leads_url, headers = headers)

  print(result.text)

  try:
    json_result = result.json()

    if json_result["success"]:
      config['MARKETOVARIABLES']['status'] = json_result["result"][0]["status"]

      with open('config.ini','w') as configfile:
        config.write(configfile)
    else:
      error = "The request failed"
      print(error)
      send_email(config, f"{config['GLOBAL']['context']}: enqueue_leads_export function {error}")
      sys.exit()
      
  except:
    error = 'Exception raised'
    print(error)
    send_email(config, f"{config['GLOBAL']['context']}: enqueue_leads_export function {error}")

  time.sleep(10)

def update_request_status(config):
  print('waiting')

  bulkurl = config['MARKETOCREDENTIALS']['bulkurl']
  exportId = config['MARKETOVARIABLES']['export_id']
  access_token = get_global_access_token(config)

  status_leads_url = f"{bulkurl}/v1/leads/export/{exportId}/status.json?access_token={access_token}"

  print(status_leads_url)

  result = requests.get(status_leads_url)

  try:
    json_result = result.json()
    print(json_result)

    if json_result["success"]:
      config['MARKETOVARIABLES']['status'] = json_result["result"][0]["status"]

      with open('config.ini','w') as configfile:
        config.write(configfile)
  except:
    error = 'Exception raised'
    print(error)
    send_email(config, f"{config['GLOBAL']['context']}: update_request_status function {error}")

def retrieve_data(config):
  print("downloading")

  bulkurl = config['MARKETOCREDENTIALS']['bulkurl']
  exportId = config['MARKETOVARIABLES']['export_id']
  access_token = get_global_access_token(config)

  retrieve_export_leads_url = f"{bulkurl}/v1/leads/export/{exportId}/file.json?access_token={access_token}"

  print(retrieve_export_leads_url)

  result = requests.get(retrieve_export_leads_url, allow_redirects=True, stream=True)

  #filename = f"./{config['MARKETOVARIABLES']['filename']}.csv"
  #print(result.content)

  #open(filename, 'wb').write(result.content)

  #send_data_to_gbq(config, result)

  config['MARKETOVARIABLES']['status'] = ""
  with open('config.ini','w') as configfile:
          config.write(configfile)

  return result.content
  #print("file rows number" + sum(1 for i in csv.reader(open(filename))))


def download_smart_list(config, smart_list_id):
  start_time = time.time()
  job_status = config['MARKETOVARIABLES']['status']

  print('Starting requests')

  while job_status == "" or job_status == "Created" or job_status == "Queued" or job_status == "Processing":
    if job_status == "Created":
      enqueue_request(config)
    elif job_status == "Queued" or job_status == "Processing":
      time.sleep(60)
      update_request_status(config)
    else:
      #with open(config['MARKETOVARIABLES']['lead_fields'], 'r') as file:
      #  create_request_by_fields(config, file.read().rstrip(), smart_list_id)
       create_request_by_fields(config, config['MARKETOVARIABLES']['lead_fields'], smart_list_id)
    
    job_status = config['MARKETOVARIABLES']['status']

  print("--- %s seconds ---" % (time.time() - start_time))

  if job_status == "Completed":
    return retrieve_data(config)
  elif job_status == "Cancelled" or job_status == "Failed":
    error = 'Job cancelled or failed'
    print(error)
    config['MARKETOVARIABLES']['status'] = ""
    with open('config.ini','w') as configfile:
            config.write(configfile)
    send_email(config, f"{config['GLOBAL']['context']}: download_smart_list function {error}")
  else:
    error = 'unexpected behaviour'
    print(error)
    send_email(config, f"{config['GLOBAL']['context']}: download_smart_list function {error}")

def merge_leads(config, winning_lead, losing_array):
  print('merging leads')

  endpointurl = config['MARKETOCREDENTIALS']['endpointurl']
  access_token = get_global_access_token(config)

  merge_leads_url = f"{endpointurl}/v1/leads/{winning_lead}/merge.json?access_token={access_token}&leadIds={','.join(map(str, losing_array))}"

  print(merge_leads_url)

  headers = {'content-type': 'application/json'}
  try:
    result = requests.post(merge_leads_url, '', headers = headers) 

    print(result.text)
    #print(result.json())

    json_result = result.json()
    return json_result
    
  except:
    error = 'Exception raised'
    print(error)
    send_email(config, f"{config['GLOBAL']['context']}: enqueue_leads_export function {error}")

def get_paging_token(config, since_datetime):
  print('get paging token since: %s' % (since_datetime))

  endpointurl = config['MARKETOCREDENTIALS']['endpointurl']
  access_token = get_global_access_token(config)

  paging_token_url = f"{endpointurl}/v1/activities/pagingtoken.json?sinceDatetime={since_datetime}&access_token={access_token}"

  print(paging_token_url)
  try:
    result = requests.get(paging_token_url)

    print(result.text)
    #print(result.json())
  
    json_result = result.json()
    return json_result["nextPageToken"]
    
  except:
    error = 'Exception raised'
    print(error)
    send_email(config, f"{config['GLOBAL']['context']}: enqueue_leads_export function {error}")

def get_deleted_leads(config, since_datetime):
  print('get deleted leads: %s' % (since_datetime))

  next_page_token = get_paging_token(config, since_datetime)
  more_result = True

  endpointurl = config['MARKETOCREDENTIALS']['endpointurl']

  while more_result:
    #more_result = False
    access_token = get_global_access_token(config)

    paging_token_url = f"{endpointurl}/v1/activities/deletedleads.json?nextPageToken={next_page_token}&access_token={access_token}"

    print(paging_token_url)
    try:
      result = requests.get(paging_token_url)

      print(result.text)
      print(result.content)
      #print(result.json())
    
      json_result = result.json()
      next_page_token = json_result['nextPageToken']
      more_result = json_result['moreResult']
      #more_result = False
      
    except:
      error = 'Exception raised'
      print(error)
      send_email(config, f"{config['GLOBAL']['context']}: enqueue_leads_export function {error}")
  return json_result

