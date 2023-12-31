import os
import sys
import json
from typing import Generator
from datetime import datetime
import googlemaps
import requests
import newspaper
from newspaper import Config
import boto3
from decimal import Decimal
from .gpt import GPT  # Assuming '.gpt' is a correct relative import

class DataBuilder:
    base_url = "https://serpapi.com/search"

    def __init__(self, initial_object: dict, config: dict = None) -> None:
        """
        Initialize the DataBuilder with initial data and configuration.

        :param initial_object: Initial data for the DataBuilder.
        :param config: Optional configuration settings, defaulting to None.
        """
        if config is None:
            config = {}

        self.initial_object = initial_object
        self.geocode_result = None
        self.config = self.get_config(config)
        self.lambda_client = None
        self.table_resource = None

    def exception_handler(self, e: Exception) -> None:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        e_info = exc_type, fname, exc_tb.tb_lineno
        # TODO: Implement logging or handling of the exception info in e_info

    def parse_gmap_result(self, gresult: dict) -> dict or False:
        """
        Parses geocoding results from Google Maps API to extract relevant data.

        :param gresult: A dict containing the Google Maps geocoding result.
        :return: A dict containing parsed location data, or False if failed.
        """
        try:
            lat_lng = gresult['geometry']['location']
            result = {
                "lat_lng": lat_lng,
                "lat_lng_str": f"{lat_lng['lat']}, {lat_lng['lng']}",
                "address_full": gresult.get('formatted_address', ''),
                "place": gresult['address_components'][0].get('long_name', '')
            }

            for component in gresult['address_components']:
                if "locality" in component['types']:
                    result['locality'] = component.get('long_name', '')
                if "administrative_area_level_1" in component['types']:
                    result['region_state'] = component.get('long_name', '')
                if "country" in component['types']:
                    result['country'] = component.get('long_name', '')

            self.geocode_result = result
            return result
        except (KeyError, IndexError):
            # Could not parse the result properly, return False or handle the exception.
            return False

    def geocode(self, location: str) -> dict or None:
        """
        Uses the Google Maps API client to geocode a location string.

        :param location: A string containing the location to geocode.
        :return: A dict containing geocoded location data, or None if failed.
        """
        client = googlemaps.Client(key=os.getenv("geocoding_key"))
        results = client.geocode(location)
        
        for result in results:
            parsed_result = self.parse_gmap_result(result)
            if parsed_result:
                return parsed_result
        return None

    def gpt_request(self, body: str) -> dict:
        """
        Makes a request to the GPT service with the provided body of text.

        :param body: A string containing the text body for the GPT request.
        :return: A dict containing the GPT response.
        """
        gpt_service = GPT(os.getenv("openai_key"))
        body = body[:min(len(body), 2500)]  # Ensure the body is not too long
        schema = {
            "person": "The first and last name of the missing person, set to False if not found.",
            "location": "String of the location where the person went missing, formatted appropriately.",
            "details": "Summarized article and most important details relevant to the status of the missing person."
        }
        return gpt_service.gptFunction(schema, "Given the following article, scrape and return the desired values from the schema in json.", body)
    
    @staticmethod
    def get_config(config: dict) -> Config:
        """
        Creates a newspaper.Config object based on the provided configuration dict.

        :param config: A dict containing configuration options.
        :return: A Config object with the specified settings.
        """
        newspaper_config = Config()
        newspaper_config.browser_user_agent = config.get(
            "user_agent",
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0'
        )
        newspaper_config.request_timeout = config.get("timeout", 30)
        return newspaper_config

    def read_from_serp(self, article: dict) -> dict:
        """
        Downloads and parses an article from a SERP using the newspaper library.

        :param article: A dict representing the article with the key 'link'.
        :return: The updated article dict containing the parsed text.
        """
        article_url = article.get('link')
        # Ensure article URL is provided, else return the original article unchanged.
        if not article_url:
            return article

        newspaper_article = newspaper.Article(article_url, config=self.config)
        newspaper_article.download()
        newspaper_article.parse()

        article['text'] = newspaper_article.text
        return article
    
    def params(self, **kwargs) -> dict:
        """
        Builds a parameter dict for the SERP API request and prints it.

        :param kwargs: Keyword arguments representing additional parameters.
        :return: The parameter dict with added API key.
        """
        kwargs['api_key'] = os.getenv("serp_key")
        print(json.dumps(kwargs, indent=4))  # Optionally, consider logging instead of printing
        return kwargs

    def news(self, query: str, gl: str = "us") -> list[dict]:
        """
        Retrieves news results from the SERP API based on the provided query and location.

        :param query: A string representing the search query.
        :param gl: A string representing the geographical location parameter, defaults to 'us'.
        :return: A list of dicts representing news results.
        """
        params = self.params(q=query, gl=gl, engine="google_news")
        response = requests.get(self.base_url, params=params).json()
        # Optionally, consider logging the response instead of printing
        return response.get('news_results', [])
    
    def articles(self, query: str, gl: str = "us") -> Generator[dict, None, None]:
        """
        Generates articles from news results.

        :param query: A string representing the search query.
        :param gl: A string representing the geographical location parameter, defaults to 'us'.
        :return: A generator yielding article dicts.
        """
        articles = self.news(query=query, gl=gl)
        for article in articles:
            yield article

    def send_batches(self, serp_results: list, batch_size: int = 5) -> None:
        """
        Sends batches of SERP results to the configured AWS Lambda function.

        :param serp_results: A list of SERP result dicts.
        :param batch_size: The size of each batch to be sent to Lambda, defaults to 5.
        """
        if self.lambda_client is None:
            self.lambda_client = boto3.client("lambda")

        for batch in [serp_results[i:i + batch_size] for i in range(0, len(serp_results), batch_size)]:
            self.lambda_client.invoke(
                FunctionName=os.getenv('gpt_function_name'),
                Payload=json.dumps({"articles": batch}),
                InvocationType='Event'   
            )

    def article_dt(self, article: dict) -> datetime:
        """
        Parses the article's date field into a datetime object.

        :param article: A dict containing the article with a date string.
        :return: A datetime object representing the parsed date.
        """
        date_format = "%m/%d/%Y, %I:%M %p, %z %Z"
        return datetime.strptime(article['date'], date_format)

    def put_item(self, item: dict) -> None:
        """
        Stores a given item in a DynamoDB table.

        :param item: A dict representing the item to be stored.
        """
        if self.table_resource is None:
            self.table_resource = boto3.resource('dynamodb').Table(os.getenv('table_name'))
        
        serialized_item = json.loads(json.dumps(item), parse_float=Decimal)
        self.table_resource.put_item(Item=serialized_item)