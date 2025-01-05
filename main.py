import vertexai
from vertexai.preview.generative_models import GenerativeModel, FunctionDeclaration, Tool, HarmCategory, HarmBlockThreshold, Content, Part

import requests
import os
from datetime import date
from dotenv import load_dotenv
PROJECT_ID = "travel-agent-446900" 
LOCATION = "us-central1" 

# !gcloud auth login 
# !gcloud config set project $PROJECT_ID
# !gcloud auth application-default login

vertexai.init(project=PROJECT_ID, location=LOCATION)

load_dotenv()

SERP_API_KEY = os.getenv("SERP_API_KEY")
print(SERP_API_KEY)


def event_api(query: str, htichips: str = "date:today"):
  URL = f"https://serpapi.com/search.json?api_key={SERP_API_KEY}&engine=google_events&q={query}&htichips={htichips}&hl=en&gl=us"
  response = requests.get(URL).json()
  return response["events_results"]


def hotel_api(query:str, check_in_date:str, check_out_date:int, hotel_class:int = 3, adults:int = 2):
    URL = f"https://serpapi.com/search.json?api_key={SERP_API_KEY}&engine=google_hotels&q={query}&check_in_date={check_in_date}&check_out_date={check_out_date}&adults={int(adults)}&hotel_class={int(hotel_class)}&currency=USD&gl=us&hl=en"
    response = requests.get(URL).json()
    
    # Debug the response
    print("API Response:", response)
    
    # Check if there are any error messages
    if "error" in response:
        return f"Error: {response['error']}"
    
    # The actual key might be different, check the response structure
    # Common keys in SERP API hotel responses are 'hotels_results' or 'hotel_results'
    for possible_key in ['properties', 'hotels_results', 'hotel_results']:
        if possible_key in response:
            return response[possible_key]
    
    # If no valid data is found, return an informative message
    return "No hotel data found in the response"

def weather_api(query:str):
    URL = f"https://serpapi.com/search.json?api_key={SERP_API_KEY}&engine=google_events&q={query}&htichips=date:today&hl=en&gl=us"
    response = requests.get(URL).json()
    return response["events_results"]



def get_events(query: str, htichips: str = "date:today"):
  events = event_api(query, htichips)
  return events


def get_hotels(query:str, check_in_date:str, check_out_date:int, hotel_class:int = 3, adults:int = 2):
    try:
        hotels = hotel_api(query, check_in_date, check_out_date, hotel_class, adults)
        return hotels
    except Exception as e:
        return f"Error fetching hotel data: {str(e)}"


def flight_api(query:str, departure_date:str, return_date:str, adults:int = 2):
    URL = f"https://serpapi.com/search.json?api_key={SERP_API_KEY}&engine=google_flights&q={query}&departure_date={departure_date}&return_date={return_date}&adults={int(adults)}&currency=USD&gl=us&hl=en"
    response = requests.get(URL).json()
    return response["properties"]


def get_flights(query:str, departure_date:str, return_date:str, adults:int = 2):
    flights = flight_api(query, departure_date, return_date, adults)
    return flights


event_function = FunctionDeclaration(
    name = "event_api",
    description = "Retrieves event information based on a query and optional filters.",
    parameters = {
        "type":"object",
        "properties": {
            "query":{
                "type":"string",
                "description":"The query you want to search for (e.g., 'Events in Austin, TX')."
            },
            "htichips":{
                "type":"string",
                "description":"""Optional filters used for search. Default: 'date:today'.
                
                Options:
                - 'date:today' - Today's events
                - 'date:tomorrow' - Tomorrow's events
                - 'date:week' - This week's events
                - 'date:weekend' - This weekend's events
                - 'date:next_week' - Next week's events
                - 'date:month' - This month's events
                - 'date:next_month' - Next month's events
                - 'event_type:Virtual-Event' - Online events
                """,
            }
    },
    "required": [
            "query"
        ]
    },
)


hotel_function = FunctionDeclaration(
    name="hotel_api",
    description="Retrieves hotel information based on location, dates, and optional preferences.",
    parameters= {
        "type":"object",
        "properties": {
            "query":{
                "type":"string",
                "description":"Parameter defines the search query. You can use anything that you would use in a regular Google Hotels search."
            },
            "check_in_date":{
                "type":"string",
                "description":"Check-in date in YYYY-MM-DD format (e.g., '2024-04-30')."
            },
           "check_out_date":{
               "type":"string",
               "description":"Check-out date in YYYY-MM-DD format (e.g., '2024-05-01')."
           },
           "hotel_class":{
               "type":"integer",
                "description":"""hotel class.


                  Options:
                  - 2: 2-star
                  - 3: 3-star
                  - 4: 4-star
                  - 5: 5-star
                
                  For multiple classes, separate with commas (e.g., '2,3,4')."""
           },
           "adults":{
               "type": "integer",
               "description": "Number of adults. Only integers, no decimals or floats (e.g., 1 or 2)"
           }
    },
    "required": [
            "query",
            "check_in_date",
            "check_out_date"
        ]
    },
)

weather_function = FunctionDeclaration(
    name="weather_api",
    description="Retrieves weather information based on a query.",
    parameters= {
        "type":"object",
        "properties": {
            "query":{
                "type":"string",
                "description":"The query you want to search for (e.g., 'Weather in Austin, TX')."
            }
        }
    }
)

generation_config = {
    "max_output_tokens": 128,
    "temperature": .5,
    "top_p": .3,
}

safety_settings = {
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
}



tools = Tool(function_declarations=[event_function, hotel_function])

model = GenerativeModel(
    model_name = 'gemini-1.5-pro-001', 
    generation_config = generation_config, 
    safety_settings = safety_settings, 
    tools = [tools])
chat = model.start_chat()
response = chat.send_message("Hello")
print(response.text)


CallableFunctions = {
    "event_api": event_api,
    "hotel_api": hotel_api,
    "weather_api": weather_api
}

today = date.today()

def mission_prompt(prompt:str):
    return f"""
    Thought: I need to understand the user's request and determine if I need to use any tools to assist them.
    Action: 
    
    - If the user's request needs following APIs from available ones: weather, event, hotel, and I have all the required parameters, call the corresponding API.
    - Otherwise, if I need more information to call an API, I will ask the user for it.
    - If the user's request doesn't need an API call or I don't have enough information to call one, respond to the user directly using the chat history.
    - Respond with the final answer only

    [QUESTION] 
    {prompt}

    [DATETIME]
    {today}

    """.strip()



def Agent(user_prompt):
    prompt = mission_prompt(user_prompt)
    response = chat.send_message(prompt)
    tools = response.candidates[0].function_calls
    while tools:
        for tool in tools:
            function_res = CallableFunctions[tool.name](**tool.args)
            response = chat.send_message(Content(role="function_response",parts=[Part.from_function_response(name=tool.name, response={"result": function_res})]))
        tools = response.candidates[0].function_calls
    return response.text



response1 = Agent("Hello")
print(response1)

response2 = Agent("What events are there to do in Atlanta, Georgia?")
print(response2)

response3 = Agent("Are there any hotel avaiable in Midtown Atlanta for this Sunday?")
print(response3)