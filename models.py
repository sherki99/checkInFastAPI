from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime

class Measurement(BaseModel):
    value: float
    unit: str

class MeasurementsData(BaseModel):
    acrossBackShoulderWidth: Optional[Measurement]
    backNeckHeight: Optional[Measurement]
    backNeckPointToGroundContoured: Optional[Measurement]
    backNeckPointToWaist: Optional[Measurement]
    backNeckPointToWristLengthR: Optional[Measurement]
    bellyWaistDepth: Optional[Measurement]
    bellyWaistGirth: Optional[Measurement]
    bellyWaistHeight: Optional[Measurement]
    bellyWaistWidth: Optional[Measurement]
    bustGirth: Optional[Measurement]
    bustHeight: Optional[Measurement]
    calfGirthR: Optional[Measurement]
    forearmGirthR: Optional[Measurement]
    hipGirth: Optional[Measurement]
    hipHeight: Optional[Measurement]
    # ... add other measurements as needed

class MeasurementsEntry(BaseModel):
    date: datetime
    measurements: MeasurementsData

class ProfileSection(BaseModel):
    title: str
    data: Dict[str, Any]

class ClientProfile(BaseModel):
    personal: ProfileSection
    fitness: ProfileSection
    goals: ProfileSection
    lifestyle: ProfileSection
    nutrition: ProfileSection

class FirstPlanRequest(BaseModel):
    userId: str
    measurements: MeasurementsEntry
    profile: ClientProfile