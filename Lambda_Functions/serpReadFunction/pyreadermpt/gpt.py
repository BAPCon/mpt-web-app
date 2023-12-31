import requests, json

class GPT:
    """
    Functions for communicating with ChatGPT.

    Attributes
    ----------
    base_url : str
        URL for requests to chat/completions
    api_key : str
        OpenAI api key.
    config : dict
        Configuration settings for this class
    exception_output : str
        Contains most recent exception raised.

    Methods
    -------
    header() -> dict
        Returns the header dict used for requests.
    userMessage() -> dict
        Returns a message dict for GPT requests.
    gptFunction(schema, query, value) -> dict
        Returns GPT completion fitting passed natural language schema.
    """

    base_url = "https://api.openai.com/v1/chat/completions"

    def __init__(self, api_key: str, config: dict = {}) -> None:
        self.api_key = api_key
        self.config = config
        self.exception_output = None

    def header(self):
        """
        Returns header dict.
        """
        return {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.api_key
        }
    
    def userMessage(self, content: str) -> dict:
        """
        Returns a dict containg user role and passed content.

        Parameters
        ----------
        content : str
            The message content..
        """
        return {
            "role": "user",
            "content": content
        }

    def gptFunction(self, schema: dict, query: str, value: dict or str) -> list:
        """
        Returns an chat output following the referenced schema.

        Parameters
        ----------
        schema : dict
            The schema of the desired JSON output.
        query : str
            The text directing GPT to act.
        value : dict or str
            The data to be acted on.
        """
        if isinstance(value, dict): value = json.dumps(value)
        content  = '(Respond with JSON in schema `'+json.dumps(schema)+'`) '
        content += query + ': '+ value 

        body = {
            "model"           : "gpt-3.5-turbo-1106",
            "temperature"     :  0.4,
            "messages"        : [self.userMessage(content)],
            "response_format" : { "type": "json_object" }
        }

        response = requests.post(GPT.base_url, headers=self.header(),json=body)
        return json.loads(response.json()['choices'][0]['message']['content'])