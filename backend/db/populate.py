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
                    'Carbohydrates': Decimal(row[8]),
                    'Fiber': Decimal(row[9]),
                    'Sugar': Decimal(row[10]),
                    'Protein': Decimal(row[11]),
                    'Dairy': int(row[12]),
                    'Egg': int(row[13]),
                    'Soy': int(row[14]),
                    'Wheat': int(row[15]),
                    'Tree_Nuts': int(row[16]),
                    'Fish': int(row[17]),
                    'Price': Decimal(row[18]),
                    'Description': row[19],
                    'Ingredients': row[20],
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


# import boto3
# import csv
# from decimal import Decimal
# from botocore.exceptions import NoCredentialsError, PartialCredentialsError

# # Initialize a session using Amazon DynamoDB
# dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

# # Choose your table
# table = dynamodb.Table('CFA-Data')

# # Define a function to delete an item
# def delete_item(primary_key_value):
#     try:
#         table.delete_item(Key={'Item': primary_key_value})
#         print(f"Successfully deleted item with key: {primary_key_value}")
#     except Exception as e:
#         print(f"Error deleting item with key {primary_key_value}: {e}")

# # Function to delete all items in the table
# def delete_all_items():
#     try:
#         # Scan the table to get all items
#         response = table.scan()
#         items = response.get('Items', [])
        
#         # Loop through each item and delete it
#         for item in items:
#             delete_item(item['Item'])  # Assuming 'Item' is the primary key
            
#         # Handle pagination if there are more items
#         while 'LastEvaluatedKey' in response:
#             response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
#             items = response.get('Items', [])
#             for item in items:
#                 delete_item(item['Item'])

#     except Exception as e:
#         print(f"Error deleting items: {e}")

# # Define a function to insert an item
# def insert_item(item):
#     try:
#         table.put_item(Item=item)
#         print(f"Successfully inserted: {item}")
#     except NoCredentialsError:
#         print("No AWS credentials found.")
#     except PartialCredentialsError:
#         print("Incomplete AWS credentials.")
#     except Exception as e:
#         print(f"Error inserting item: {e}")

# # Function to read CSV file line by line and map data to DynamoDB items
# def populate_table_from_csv(csv_file):
#     try:
#         with open(csv_file, mode='r', newline='', encoding='utf-8') as file:
#             csv_reader = csv.reader(file)
#             _ = next(csv_reader)  # Read the header row
#             for row in csv_reader:
#                 # Map each row to DynamoDB attributes
#                 item = {
#                     'Item': row[0],
#                     'Serving_size': int(row[1][:-1]), # remove 'g' at the end
#                     'Calories': Decimal(row[2]),
#                     'Fat': Decimal(row[3]),
#                     'Sat_Fat': Decimal(row[4]),
#                     'Trans_Fat': Decimal(row[5]),
#                     'Cholesterol': Decimal(row[6]),
#                     'Sodium': Decimal(row[7]),
#                     'Carbohydrates': Decimal(row[8]),
#                     'Fiber': Decimal(row[9]),
#                     'Sugar': Decimal(row[10]),
#                     'Protein': Decimal(row[11]),
#                     'Dairy': int(row[12]),
#                     'Egg': int(row[13]),
#                     'Soy': int(row[14]),
#                     'Wheat': int(row[15]),
#                     'Tree_Nuts': int(row[16]),
#                     'Fish': int(row[17]),
#                     'Price': Decimal(row[18]),
#                     'Description': row[19],
#                     'Ingredients': row[20],
#                 }
#                 insert_item(item)
#     except FileNotFoundError:
#         print(f"File {csv_file} not found.")
#     except Exception as e:
#         print(f"Error reading CSV file: {e}")

# # Provide the path to your CSV file
# url = './backend/resources/database-resources/CFA_Data.csv'

# # Delete all items in the DynamoDB table before populating
# delete_all_items()

# # Populate the DynamoDB table with data from the CSV file
# populate_table_from_csv(url)
