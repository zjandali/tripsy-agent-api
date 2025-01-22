from datetime import date
from typing import Optional, List
from langchain_openai import ChatOpenAI
from agents.tools.flights_finder import flights_finder, FlightsInput, FlightsInputSchema

class BaseSearchAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model='gpt-4')

class FlightSearchAgent(BaseSearchAgent):
    def __init__(self):
        super().__init__()
        self.tool = flights_finder

    async def search(self, departure: str, arrival: str, start_date: date, 
                    end_date: date, budget: float, travelers: int = 1) -> List[dict]:
        input_data = {
            "params": {
                "departure_airport": departure,
                "arrival_airport": arrival,
                "outbound_date": str(start_date),
                "return_date": str(end_date),
                "adults": travelers,
                "children": 0,
                "infants_in_seat": 0,
                "infants_on_lap": 0
            }
        }

        try:
            results = self.tool(input_data)
            
            if isinstance(results, str):  # Error case
                print(f"Search error: {results}")
                return {"error": results, "flights": []}
                
            # Filter by budget and add booking URL
            filtered_flights = []
            for flight in results:
                if flight.get('price', float('inf')) <= budget:
                    # Construct Google Flights URL
                    base_url = "https://www.google.com/travel/flights"
                    params = f"?q=Flights%20from%20{departure}%20to%20{arrival}"
                    flight['booking_url'] = base_url + params
                    filtered_flights.append(flight)
                    
            print(f"Found {len(filtered_flights)} flights within budget")
            return {
                "flights": filtered_flights
            }
        except Exception as e:
            print(f"Exception in flight search: {str(e)}")
            return {"error": str(e), "flights": []}

class HotelSearchAgent(BaseSearchAgent):
    def __init__(self):
        super().__init__()
        self.tool = hotels_finder

    async def search(self, city: str, start_date: date, end_date: date, 
                    budget: float, travelers: int = 1, rooms: int = 1) -> List[dict]:
        # Calculate daily budget
        days = (end_date - start_date).days
        daily_budget = budget / days

        results = self.tool({
            "q": city,
            "check_in_date": str(start_date),
            "check_out_date": str(end_date),
            "adults": travelers,
            "rooms": rooms
        })

        return [hotel for hotel in results if hotel.get('price_per_night', float('inf')) <= daily_budget]

class ActivitySearchAgent(BaseSearchAgent):
    def __init__(self):
        super().__init__()
        self.tool = activities_finder

    async def search(self, city: str, start_date: date, end_date: date, 
                    budget: float, activity_type: Optional[str] = None) -> List[dict]:
        # Calculate daily activities budget
        days = (end_date - start_date).days
        daily_budget = budget / days

        results = self.tool({
            "location": city,
            "date": str(start_date),
            "budget": "high" if daily_budget > 200 else "medium" if daily_budget > 100 else "low",
            "type": activity_type
        })

        return results

class RestaurantSearchAgent(BaseSearchAgent):
    async def search(self, city: str, start_date: date, end_date: date,
                    budget: float, cuisine_type: Optional[str] = None) -> List[dict]:
        # Calculate per-meal budget
        days = (end_date - start_date).days
        daily_budget = budget / days
        
        # Use Google Places API through SerpAPI
        query = f"restaurants in {city}"
        if cuisine_type:
            query += f" {cuisine_type} cuisine"

        price_level = "$$$$" if daily_budget > 100 else "$$$" if daily_budget > 50 else "$$"
        
        # This would need to be implemented similar to other search tools
        # For now returning placeholder
        return [{
            "name": "Example Restaurant",
            "price_level": price_level,
            "rating": 4.5,
            "cuisine": cuisine_type
        }] 