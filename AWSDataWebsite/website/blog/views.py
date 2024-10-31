from django.shortcuts import render
from subprocess import run, PIPE
import boto3
from boto3.dynamodb.conditions import Key, Attr
import json
from datetime import datetime, timedelta

import csv

csv_file_path = '../../../Ana_accessKeys.csv'

with open(csv_file_path, 'r') as csvfile:
    csv_reader = csv.reader(csvfile)

    # Skip the first line (header)
    header = next(csv_reader, None)

    # Read the second line
    second_line = next(csv_reader, None)

    if second_line:
        aws_access_key_id = second_line[0]
        aws_secret_access_key = second_line[1]

boto3.setup_default_session(
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name='eu-north-1'  # Replace with your actual AWS region
)

last_hour_r = datetime.now() - timedelta(hours = 1)

batch_size = 500

# Change the region name and the table name
client = boto3.client('dynamodb');
dynamoDB = boto3.resource('dynamodb', region_name='eu-north-1')     # connection to DynamoDB and access
dynamoTable = dynamoDB.Table('EnvironmentalStationData')               # to the table EnvironmentalStation that will store the data provided

def home(request):

    # Last data from station1
    response = dynamoTable.query(
        KeyConditionExpression = Key('ID').eq('station1')
    )
    items = response['Items']

    context = {}
    context['ID'] = (items[len(items) - 1]["ID"])
    context['Temperature'] = (items[len(items) - 1]["Temperature"])
    context['datetime'] = (items[len(items) - 1]["timestamp"])
    context['WindIntensity'] = (items[len(items) - 1]["WindIntensity"])
    context['WindDirection'] = (items[len(items) - 1]["WindDirection"])
    context['Humidity'] = (items[len(items) - 1]["Humidity"])
    context['RainHeight'] = (items[len(items) - 1]["RainHeight"])

    # Last data from station2
    response = dynamoTable.query(
        KeyConditionExpression = Key('ID').eq('station2')
    )
    items = response['Items']

    context['ID2'] = (items[len(items) - 1]["ID"])
    context['Temperature2'] = (items[len(items) - 1]["Temperature"])
    context['datetime2'] = (items[len(items) - 1]["timestamp"])
    context['WindIntensity2'] = (items[len(items) - 1]["WindIntensity"])
    context['WindDirection2'] = (items[len(items) - 1]["WindDirection"])
    context['Humidity2'] = (items[len(items) - 1]["Humidity"])
    context['RainHeight2'] = (items[len(items) - 1]["RainHeight"])


    return render(request, 'blog/home.html', context)


def format_data(filtered_data, parameter_name:str, parameter_symbol:str):
    
    formatted_data = [f"{data[i]['timestamp']} | {data[i]['ID']} | {data[i][parameter_name]}{parameter_symbol}" for data in filtered_data for i in reversed(range(len(data)))]

    return reversed(formatted_data)

def filter_data(station_str: str, context: dict, key_name: str, data: list):

    response = dynamoTable.query(
        KeyConditionExpression=Key('ID').eq(station_str)
    )
    items = response['Items']

    filtered_data = [elem for elem in reversed(items) if datetime.strptime(elem["timestamp"], '%Y-%m-%d %H:%M:%S') >= last_hour_r]

    data_s = get_data_points(filtered_data)

    context[key_name] = data_s

    data.append(data_s)

def storage(request):

    context = {}
    data = []

    # Last hour data from station1

    filter_data('station1', context, 'items1', data)

    filter_data('station2', context, 'items2', data)

    # The rest of the code is for the last hour data of each sensor

    parameters = {"Temperature":('temp', ' C°'), "RainHeight": ('rain', ' mm/h'), "WindIntensity": ('windintensity', ' m/s'), "Humidity": ('humidity', ' %'), "WindDirection": ('windirection', ' °')}

    for key, value in parameters.items():
        context[value[0]] = format_data(data, key, value[1])

    return render(request, 'blog/storage.html', context)

def get_station_data(station_str: str):
    response_station = dynamoTable.query(
        KeyConditionExpression=Key('ID').eq(station_str)
    )
    items_station = response_station['Items']
    filtered_station_data = [elem for elem in reversed(items_station) if datetime.strptime(elem["timestamp"], '%Y-%m-%d %H:%M:%S') >= last_hour_r]
    return filtered_station_data

# new function that uses between instead of manually filtering the dates

def all_stations_data_hour():
    start_datetime = (datetime.now() - timedelta(hours = 1)).strftime('%Y-%m-%d %H:%M:%S')
    end_datetime = (datetime.now()).strftime('%Y-%m-%d %H:%M:%S')

    response_station = dynamoTable.query(
        KeyConditionExpression=Key('ID').eq('station1') & Key('timestamp').between(start_datetime, end_datetime)
    )

    items_station = response_station['Items']
    
    return items_station

# function to get the data for each station in the desired period (1 hour)

def station_data(station_str: str):

    response = dynamoTable.query(
        KeyConditionExpression=Key('ID').eq(station_str)
    )
    items = response['Items']

    filtered_data = [elem for elem in reversed(items) if datetime.strptime(elem["timestamp"], '%Y-%m-%d %H:%M:%S') >= last_hour_r]

    return filtered_data

# Function to parse datetime strings

def parse_datetime(datetime_str):
    return datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')

# function to select the data points in each minute of the time (1 hour) that we are observing

def get_data_points(data):

    # Dictionary to keep track of unique minutes
    unique_minutes = {}

    # Select the first entry for each unique minute
    filtered_entries = []
    for entry in data:
        minute_key = parse_datetime(entry['timestamp']).strftime('%Y-%m-%d %H:%M')
        if minute_key not in unique_minutes:
            filtered_entries.insert(0, entry)
            unique_minutes[minute_key] = True
        if len(filtered_entries) >= 60:
            break

    return filtered_entries

# function to take only the time

def take_time(datetime_str):
    # Parse the datetime string into a datetime object
    datetime_obj = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')

    # Extract the minutes and format as a string
    minutes_str = datetime_obj.strftime('%H:%M')

    return minutes_str

def data_points(station_str):
    stat_data = station_data(station_str)
    data = get_data_points(stat_data)
    return data

def charts(request):
    y_variables = ['Temperature', 'RainHeight', 'WindIntensity', 'Humidity', 'WindDirection']
    context = {}

    for station_str in ['station1', 'station2']:
        items_station = data_points(station_str)
        context['time'] = [take_time(item['timestamp']) for item in items_station]
        for y_variable in y_variables:
            str_data = f'{station_str}_{y_variable.lower()}'
            context[str_data] = [item[y_variable] for item in items_station]

    return render(request, 'blog/chart.html', {'context':context})
