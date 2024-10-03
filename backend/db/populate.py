import boto3
import csv
from decimal import Decimal
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

# Initialize a session using Amazon DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

# Choose your table
table = dynamodb.Table('CFA-Data')

# Define a function to insert an item
def insert_item(item):
    try:
        table.put_item(Item=item)
        print(f"Successfully inserted: {item}")
    except NoCredentialsError:
        print("No AWS credentials found.")
    except PartialCredentialsError:
        print("Incomplete AWS credentials.")
    except Exception as e:
        print(f"Error inserting item: {e}")

# Function to read CSV file line by line and map data to DynamoDB items
def populate_table_from_csv(csv_file):
    try:
        with open(csv_file, mode='r', newline='', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            _ = next(csv_reader)  # Read the header row
            for row in csv_reader:
                # Map each row to DynamoDB attributes
                item = {
                    'Item': row[0],
                    'Serving_size': int(row[1][:-1]), # remove 'g' at the end
                    'Calories': Decimal(row[2]),
                    'Fat': Decimal(row[3]),
                    'Sat_Fat': Decimal(row[4]),
                    'Trans_Fat': Decimal(row[5]),
                    'Cholesterol': Decimal(row[6]),
                    'Sodium': Decimal(row[7]),
                    'Fiber': Decimal(row[8]),
                    'Sugar': Decimal(row[9]),
                    'Protein': Decimal(row[10]),
                    'Dairy': int(row[11]),
                    'Egg': int(row[12]),
                    'Soy': int(row[13]),
                    'Wheat': int(row[14]),
                    'Tree_Nuts': int(row[15]),
                    'Fish': int(row[16]),
                    'Price': Decimal(row[17]),
                    'Description': row[18],
                    'Ingredients': row[19],
                }
                insert_item(item)
    except FileNotFoundError:
        print(f"File {csv_file} not found.")
    except Exception as e:
        print(f"Error reading CSV file: {e}")

# Provide the path to your CSV file
url = './backend/resources/database-resources/CFA_Data.csv'

# Populate the DynamoDB table with data from the CSV file
populate_table_from_csv(url)
