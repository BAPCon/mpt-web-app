import boto3
import json, os
from decimal import Decimal

#Does quasi the same things as json.loads from here: https://pypi.org/project/dynamodb-json/
class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return json.JSONEncoder.default(self, obj)

table = None

def dumb_cache(cache_name: str, file_ext: str = ".json"):
    cache_path = os.path.join('dumb_cache', cache_name + file_ext)
    if not os.path.exists(cache_path):
        return False, None, cache_path
    with open(cache_path, 'r') as r:
        return True, json.loads(r.read()), cache_path
        

def get_markers():
    cache = dumb_cache("markers")
    if not cache[0]:
        items = get_items()
        items = sort_articles(items)
        coords = []
        people_names = []
        for x in items:
            if str(x['geo']).lower() != 'false' and x['geo'] != None:
                if x['gpt']['person'] not in people_names:
                    coords.append([x['geo']['lat_lng'], x['gpt']['person'], x['category']['category'], x['gpt'], x['thumbnail']]  )
                    people_names.append(x['gpt']['person'])
                    
                
        with open(cache[2], 'w') as w:
            w.write(json.dumps(coords, indent=4, cls=JSONEncoder))
        return coords
    else:
        return cache[1]

def get_people():
    items_with_gpt = get_items()

    
    people = [x['gpt']['person'] for x in items_with_gpt if str(x['gpt']['person']).lower() != 'false']

    return [*set(people)]
    
    
def get_items():
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

    return items_with_gpt

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
    