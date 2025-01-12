import os
from typing import Optional
from pydantic import BaseModel
from langchain.pydantic_v1 import Field
from langchain_core.tools import tool
from serpapi import GoogleSearch
from dotenv import load_dotenv

load_dotenv()


class FlightsInput(BaseModel):
    departure_airport: Optional[str] = Field(description='Departure airport code (IATA)')
    arrival_airport: Optional[str] = Field(description='Arrival airport code (IATA)')
    outbound_date: Optional[str] = Field(description='Parameter defines the outbound date. The format is YYYY-MM-DD.')
    return_date: Optional[str] = Field(description='Parameter defines the return date. The format is YYYY-MM-DD.')
    adults: Optional[int] = Field(default=1, description='Parameter defines the number of adults.')
    children: Optional[int] = Field(default=0, description='Parameter defines the number of children.')
    infants_in_seat: Optional[int] = Field(default=0, description='Parameter defines the number of infants in seat.')
    infants_on_lap: Optional[int] = Field(default=0, description='Parameter defines the number of infants on lap.')


class FlightsInputSchema(BaseModel):
    params: FlightsInput


@tool(args_schema=FlightsInputSchema)
def flights_finder(params: FlightsInput):
    '''
    Find flights using the Google Flights engine.

    Returns:
        dict: Flight search results.
    '''

    search_params = {
        'api_key': os.getenv('SERP_API_KEY'),
        'engine': 'google_flights',
        'departure_id': params.departure_airport,
        'arrival_id': params.arrival_airport,
        'outbound_date': params.outbound_date,
        'return_date': params.return_date,
        'currency': 'USD',
        'hl': 'en',
        'adults': params.adults,
        'children': params.children
    }

    try:
        search = GoogleSearch(search_params)
        results = search.get_dict()
        if 'error' in results:
            print(f"SerpAPI Error: {results['error']}")
            return []
        return results.get('best_flights', [])
    except Exception as e:
        print(f"Exception in flights_finder: {str(e)}")
        return str(e)
