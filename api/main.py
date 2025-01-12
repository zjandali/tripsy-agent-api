from fastapi import FastAPI, HTTPException
from api.models import (
    FlightSearchRequest, HotelSearchRequest, 
    ActivitySearchRequest, RestaurantSearchRequest
)
from agents.search_agents import (
    FlightSearchAgent, HotelSearchAgent,
    ActivitySearchAgent, RestaurantSearchAgent
)

app = FastAPI()

@app.post("/api/flights/search")
async def search_flights(request: FlightSearchRequest):
    try:
        agent = FlightSearchAgent()
        results = await agent.search(
            departure=request.departure_city,
            arrival=request.arrival_city,
            start_date=request.start_date,
            end_date=request.end_date,
            budget=request.budget,
            travelers=request.travelers
        )
        
        if "error" in results:
            raise HTTPException(status_code=500, detail=results["error"])
            
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/hotels/search")
async def search_hotels(request: HotelSearchRequest):
    try:
        agent = HotelSearchAgent()
        results = await agent.search(
            city=request.city,
            start_date=request.start_date,
            end_date=request.end_date,
            budget=request.budget,
            travelers=request.travelers,
            rooms=request.room_count
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/activities/search")
async def search_activities(request: ActivitySearchRequest):
    try:
        agent = ActivitySearchAgent()
        results = await agent.search(
            city=request.city,
            start_date=request.start_date,
            end_date=request.end_date,
            budget=request.budget,
            activity_type=request.activity_type
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/restaurants/search")
async def search_restaurants(request: RestaurantSearchRequest):
    try:
        agent = RestaurantSearchAgent()
        results = await agent.search(
            city=request.city,
            start_date=request.start_date,
            end_date=request.end_date,
            budget=request.budget,
            cuisine_type=request.cuisine_type
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 