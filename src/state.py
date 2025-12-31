import operator
from typing import Annotated, List, Dict, Union, TypedDict

# 1. FlightInfo now supports the 'legs' from your nomadic tool
class FlightInfo(TypedDict):
    price: float
    details: str
    itinerary: List[Dict]

# 2. HotelInfo now supports the formatted string output from your RAG tool
class HotelInfo(TypedDict):
    location: str
    price: float
    description: str

class ActivityInfo(TypedDict):
    location: str
    total_cost: float
    details: List[Dict]

# 3. The Final TravelState
class TravelState(TypedDict):
    request: str
    destinations: List[str]
    durations: List[int]  
    origin: str
    start_window: str
    budget: float
    
    messages: Annotated[List[Dict], operator.add] 
    
    flight_info: FlightInfo
    hotel_info: List[HotelInfo]
    activity_info: List[ActivityInfo]
    
    total_cost: float
    status: str