import boto3

# Initialize DynamoDB client
dynamodb = boto3.client('dynamodb', region_name='us-east-1')

# DynamoDB table name
table_name = 'CFA-Data'

# Function to scan and retrieve all items from the DynamoDB table
def scan_dynamodb_table(table_name):
    try:
        # Perform the scan operation
        response = dynamodb.scan(
            TableName=table_name
        )
        
        # Check if items were found and print them
        if 'Items' in response:
            print(f"Found {len(response['Items'])} items in table {table_name}:")
            for item in response['Items']:
                print(item)
        else:
            print(f"No items found in table {table_name}.")
    except Exception as e:
        print(f"Error querying DynamoDB: {e}")

# Call the function to print all data from the DynamoDB table
scan_dynamodb_table(table_name)