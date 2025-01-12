from pydantic import BaseModel
from datetime import date
from typing import Optional

class TravelSearchRequest(BaseModel):
    start_date: date
    end_date: date
    budget: float
    travelers: Optional[int] = 1

class FlightSearchRequest(TravelSearchRequest):
    departure_city: str
    arrival_city: str

class HotelSearchRequest(TravelSearchRequest):
    city: str
    room_count: Optional[int] = 1

class ActivitySearchRequest(TravelSearchRequest):
    city: str
    activity_type: Optional[str] = None

class RestaurantSearchRequest(TravelSearchRequest):
    city: str
    cuisine_type: Optional[str] = None
    price_level: Optional[str] = None 