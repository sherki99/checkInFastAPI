
from datetime import datetime
from pydantic import BaseModel
from typing import Dict, Any, List, Optional



class Measurement: 
    part:  str
    current: str
    previous: Optional[float] = None
    change: Optional[float] = None




class ClientProfile(BaseModel):
    personal: Dict[str, Any]
    goals: Dict[str, Any]
    fitness: Dict[str, Any]
    nutrition: Dict[str, Any]
    lifestyle: Dict[str, Any]
    measurements: List[Measurement]
    measurement_date: datetime | None


class DataIngestionModule:

    def process(self, raw_data: dict) -> ClientProfile:

        profile = raw_data.get("profile", {})
        measurements_data = raw_data.get("measurements", {}).get("measurements", {})

        # Convert measurement dictionary into a list of Measurement objects
        measurements = [
            Measurement(
                part=part,
                current=values.get("current"),
             #   previous=values.get("previous"),
             #   change=values.get("change")
            )
            for part, values in measurements_data.items()
        ]

        client_profile = ClientProfile(
            personal=profile.get("personal", {}).get("data", {}),
            goals=profile.get("goals", {}).get("data", {}),
            fitness=profile.get("fitness", {}).get("data", {}),
            nutrition=profile.get("nutrition", {}).get("data", {}),
            lifestyle=profile.get("lifestyle", {}).get("data", {}),
            measurements=measurements.get("measurements", {}),  
            measurement_date=measurements.get("date") 
        )
        return client_profile

    # I might I want to add more module to return in case I need them 

