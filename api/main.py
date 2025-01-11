from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import date
import uuid
import os
from langchain_core.messages import HumanMessage

from agents.agent import Agent

app = FastAPI(title="Travel Planning API")

class TravelQuery(BaseModel):
    query: str
    thread_id: Optional[str] = None

class TripPlanRequest(BaseModel):
    trip_name: str
    start_date: date
    end_date: date
    companions: List[str]
    budget: float
    destination: str

class EmailRequest(BaseModel):
    sender_email: str
    receiver_email: str
    subject: str = "Travel Information"
    thread_id: str

# Initialize agent
agent = Agent()

@app.post("/travel/query")
async def process_travel_query(request: TravelQuery):
    try:
        thread_id = request.thread_id or str(uuid.uuid4())
        messages = [HumanMessage(content=request.query)]
        config = {'configurable': {'thread_id': thread_id}}
        
        result = agent.graph.invoke({'messages': messages}, config=config)
        
        return {
            "thread_id": thread_id,
            "result": result['messages'][-1].content
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/travel/plan")
async def create_trip_plan(request: TripPlanRequest):
    try:
        query = f"""
        Plan a trip to {request.destination}
        Dates: {request.start_date} to {request.end_date}
        Budget: ${request.budget}
        Travelers: {len(request.companions) + 1} people
        """
        
        thread_id = str(uuid.uuid4())
        messages = [HumanMessage(content=query)]
        config = {'configurable': {'thread_id': thread_id}}
        
        result = agent.graph.invoke({'messages': messages}, config=config)
        
        return {
            "thread_id": thread_id,
            "trip_plan": result['messages'][-1].content
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/travel/email")
async def send_travel_email(request: EmailRequest):
    try:
        os.environ['FROM_EMAIL'] = request.sender_email
        os.environ['TO_EMAIL'] = request.receiver_email
        os.environ['EMAIL_SUBJECT'] = request.subject
        
        config = {'configurable': {'thread_id': request.thread_id}}
        agent.graph.invoke(None, config=config)
        
        return {"message": "Email sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
    
    from fastapi import FastAPI, HTTPException
from agents.coordinator import TravelCoordinator

@app.post("/travel/plan")
async def create_trip_plan(request: TripPlanRequest):
    try:
        coordinator = TravelCoordinator()
        result = await coordinator.plan_trip(
            departure="",  # You'll need to add this to TripPlanRequest
            destination=request.destination,
            start_date=str(request.start_date),
            end_date=str(request.end_date),
            budget=request.budget,
            travelers=len(request.companions) + 1
        )
        
        return {
            "trip_plan": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 