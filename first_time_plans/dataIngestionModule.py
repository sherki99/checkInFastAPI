
from datetime import datetime
from pydantic import BaseModel
from typing import Dict, Any

class ClientProfile(BaseModel):
    personal: Dict[str, Any]
    goals: Dict[str, Any]
    fitness: Dict[str, Any]
    nutrition: Dict[str, Any]
    lifestyle: Dict[str, Any]
    measurements: Dict[str, Any]



class DataIngestionModule:
    def process(self, raw_data: dict) -> ClientProfile:
        # Extract data from the nested JSON structure.
        profile = raw_data.get("profile", {})
        measurements = raw_data.get("measurements", {})
        
        # Build a structured client profile.
        client_profile = ClientProfile(
            personal=profile.get("personal", {}).get("data", {}),
            goals=profile.get("goals", {}).get("data", {}),
            fitness=profile.get("fitness", {}).get("data", {}),
            nutrition=profile.get("nutrition", {}).get("data", {}),
            lifestyle=profile.get("lifestyle", {}).get("data", {}),
            measurements=measurements.get("measurements", {}).get({}),
            measurement_date=measurements.get("date")  # Should be parseable as a datetime
        )
        return client_profile
