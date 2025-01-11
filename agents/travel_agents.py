from typing import Optional
from datetime import date
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from agents.tools.flights_finder import flights_finder
from agents.tools.hotels_finder import hotels_finder
from agents.tools.activities_finder import activities_finder

class BaseTravelAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model='gpt-4')

class FlightAgent(BaseTravelAgent):
    def __init__(self):
        super().__init__()
        self.tool = flights_finder

    async def search(self, departure: str, arrival: str, date: str, budget: float, travelers: int = 1):
        query = {
            "departure_airport": departure,
            "arrival_airport": arrival,
            "outbound_date": date,
            "adults": travelers
        }
        results = self.tool(query)
        # Filter by budget
        return [flight for flight in results if flight.get('price', float('inf')) <= budget]

class HotelAgent(BaseTravelAgent):
    def __init__(self):
        super().__init__()
        self.tool = hotels_finder

    async def search(self, location: str, check_in: str, check_out: str, budget: float, guests: int = 1):
        query = {
            "q": location,
            "check_in_date": check_in,
            "check_out_date": check_out,
            "adults": guests,
            "sort_by": "price"
        }
        results = self.tool(query)
        # Filter by budget
        return [hotel for hotel in results if hotel.get('price', float('inf')) <= budget]

class ActivityAgent(BaseTravelAgent):
    def __init__(self):
        super().__init__()
        self.tool = activities_finder

    async def search(self, location: str, date: str, budget: Optional[str] = None):
        query = {
            "location": location,
            "date": date,
            "budget": budget
        }
        return self.tool(query)

class RestaurantAgent(BaseTravelAgent):
    def __init__(self):
        super().__init__()

    async def search(self, location: str, cuisine: Optional[str] = None, budget: Optional[str] = None):
        # Similar to activities_finder but for restaurants
        # You'll need to implement a restaurant_finder tool similar to the others
        pass 