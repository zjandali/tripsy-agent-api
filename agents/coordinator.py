from datetime import datetime
from typing import Optional
from .travel_agents import FlightAgent, HotelAgent, ActivityAgent, RestaurantAgent

class TravelCoordinator:
    def __init__(self):
        self.flight_agent = FlightAgent()
        self.hotel_agent = HotelAgent()
        self.activity_agent = ActivityAgent()
        self.restaurant_agent = RestaurantAgent()

    async def plan_trip(
        self,
        departure: str,
        destination: str,
        start_date: str,
        end_date: str,
        budget: float,
        travelers: int = 1,
        include_activities: bool = True,
        include_restaurants: bool = True
    ):
        # Split budget (example allocation)
        flight_budget = budget * 0.4
        hotel_budget = budget * 0.4
        activities_budget = budget * 0.2

        # Get flights
        flights = await self.flight_agent.search(
            departure=departure,
            arrival=destination,
            date=start_date,
            budget=flight_budget,
            travelers=travelers
        )

        # Get hotels
        hotels = await self.hotel_agent.search(
            location=destination,
            check_in=start_date,
            check_out=end_date,
            budget=hotel_budget,
            guests=travelers
        )

        # Get activities if requested
        activities = None
        if include_activities:
            activities = await self.activity_agent.search(
                location=destination,
                date=start_date,
                budget="medium" if budget > 1000 else "low"
            )

        # Get restaurants if requested
        restaurants = None
        if include_restaurants:
            restaurants = await self.restaurant_agent.search(
                location=destination,
                budget="medium" if budget > 1000 else "low"
            )

        return {
            "flights": flights,
            "hotels": hotels,
            "activities": activities,
            "restaurants": restaurants
        } 