from boto3.dynamodb.conditions import Key
import boto3, random
from flask import Flask, jsonify, request, render_template

dynamodb = boto3.resource('dynamodb', region_name='us-east-2')

table = dynamodb.Table('missingPersonTableAssets')

def scan():
    return table.scan().get('Items')

def get_person(person_key):
    """
    Retrieve a person's data from DynamoDB by person_key
    """
    try:
        # Query DynamoDB to get the person's record by ID
        response = table.get_item(Key={'person_key': person_key.replace('_',' ').title().replace(' ', '_')})
        
        # Check if we got a match
        if 'Item' in response:
            person_data = response['Item']
            person_data['thumbnail'] = "https://missingpersonpublicbucket.s3.amazonaws.com/" + person_data['thumbnail']
            return person_data
        else:
            return jsonify({"error": "Person not found"}), 404
    except Exception as e:
        # Handle exception or any errors that occur during the query
        return jsonify({"error": str(e)}), 500
    
    
def _get_hikers(amount: int) -> list:
    response = []
    items = scan()
    if len(items) < amount: return items
    while len(response) < amount:
            response.append(items.pop(random.randint(0, len(items)-1)))
            response[-1]['thumbnail'] = "https://missingpersonpublicbucket.s3.amazonaws.com/" + response[-1]['thumbnail'];
    return response