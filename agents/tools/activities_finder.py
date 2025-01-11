import os
from typing import Optional
from langchain.pydantic_v1 import BaseModel, Field
from langchain_core.tools import tool
import serpapi

class ActivitiesInput(BaseModel):
    location: str = Field(description='Location to find activities')
    date: Optional[str] = Field(description='Date for activities. Format: YYYY-MM-DD')
    activity_type: Optional[str] = Field(description='Type of activity (e.g., outdoor, cultural, entertainment)')
    budget: Optional[str] = Field(description='Budget range (e.g., low, medium, high)')
    
class ActivitiesInputSchema(BaseModel):
    params: ActivitiesInput

@tool(args_schema=ActivitiesInputSchema)
def activities_finder(params: ActivitiesInput):
    '''
    Find activities and attractions using Google Places API.
    '''
    params = {
        'api_key': os.environ.get('SERPAPI_API_KEY'),
        'engine': 'google_maps',
        'type': 'things to do',
        'q': f'attractions in {params.location}',
        'hl': 'en'
    }
    
    try:
        search = serpapi.search(params)
        results = search.data.get('local_results', [])[:5]
        return results
    except Exception as e:
        return str(e) 