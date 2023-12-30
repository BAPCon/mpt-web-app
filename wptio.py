import boto3
import json
from decimal import Decimal

#Does quasi the same things as json.loads from here: https://pypi.org/project/dynamodb-json/
class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return json.JSONEncoder.default(self, obj)

table = None

def get_people():
    global table

    if not table:
        _resource = boto3.resource('dynamodb')
        table = _resource.Table('ArticleTable')

    response = table.scan(
        FilterExpression='attribute_exists(gpt)'
    )

    # Retrieve items with 'gpt' attribute
    items_with_gpt = response['Items']

    # If there are more items, handle pagination
    while 'LastEvaluatedKey' in response:
        response = table.scan(
            FilterExpression='attribute_exists(gpt)',
            ExclusiveStartKey=response['LastEvaluatedKey']
        )
        items_with_gpt.extend(response['Items'])

    people = [x['gpt']['person'] for x in items_with_gpt if str(x['gpt']['person']).lower() != 'false']

    return [*set(people)]

def scan_items_by_person(requested_person):
    global table

    if not table:
        _resource = boto3.resource('dynamodb')
        table = _resource.Table('ArticleTable')

    response = table.scan(
        FilterExpression='attribute_exists(gpt) AND #g.#p = :person_val',
        ExpressionAttributeNames={
            '#g': 'gpt',
            '#p': 'person'
        },
        ExpressionAttributeValues={
            ':person_val': requested_person
        }
    )

    return response['Items']
    
def sort_articles(articles: list):
    return sorted(articles, key=lambda x: x.get('date_formatted'), reverse=True)
    