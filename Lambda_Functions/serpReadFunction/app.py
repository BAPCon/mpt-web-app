
import boto3
import json
import pyreadermpt
import os

def lambda_handler(event, context):

    reader     = pyreadermpt.DataBuilder({})
    articles   = readArticles(reader)
    
    reader.send_batches(articles)
        

    return {
        "statusCode": 200,
        'body': ""
    }


def readArticles(reader: 'pyreadermpt.DataBuilder', q: str = "missing hiker"):
    '''
    
    '''
    articles = []
    for serpArticle in reader.news(q):
        try:
            articles.append(serpArticle)
        except Exception as e: print(e)
    return articles