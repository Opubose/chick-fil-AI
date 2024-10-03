import json
import boto3
import os

dynamodb = boto3.resource('dynamodb', 
                        aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
                        aws_secret_access_key=os.getenv('AWS_SECRET_KEY'),
                        region_name='us-east-1')
menu = dynamodb.Table('CFA-Data')

