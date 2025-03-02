# check_time_plans/data_ingestion/body_metrics.py

from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime

class BodyCompositionChange(BaseModel):
    weight_change: float  # kg
    waist_change: float  # cm
    hip_change: float  # cm
    chest_change: float  # cm
    arm_change: float  # cm
    thigh_change: float  # cm
    significant_changes: List[str]
    weight_trend: str  # "increasing", "decreasing", "stable"
    body_fat_direction: str  # "improving", "worsening", "stable" (inferred from measurements)

class BodyMetricsExtractor:
    """Module for extracting and analyzing body measurement changes."""
    
    def extract_body_measurements(self, body_data: Any) -> BodyCompositionChange:
        """
        Extracts and analyzes changes in body measurements.
        
        Args:
            body_data: Standardized body measurement data
            
        Returns:
            BodyCompositionChange: Calculated body composition changes
        """
        # Default values
        weight_change = 0.0
        waist_change = 0.0
        hip_change = 0.0
        chest_change = 0.0
        arm_change = 0.0
        thigh_change = 0.0
        significant_changes = []
        weight_trend = "stable"
        body_fat_direction = "stable"
        
        # Extract measurements if available
        measurements = body_data.measurements if hasattr(body_data, "measurements") else {}
        
        # Process weight change from daily reports (not available in body measurements)
        # This would typically come from separate weight data
        
        # Process waist change
        if "waistGirth" in measurements:
            waist_change = measurements["waistGirth"].change
            if abs(waist_change) >= 1.0:
                trend = "decreased" if waist_change < 0 else "increased"
                significant_changes.append(f"Waist circumference {trend} by {abs(waist_change):.1f}cm")
        
        # Process hip change
        if "hipGirth" in measurements:
            hip_change = measurements["hipGirth"].change
            if abs(hip_change) >= 1.0:
                trend = "decreased" if hip_change < 0 else "increased"
                significant_changes.append(f"Hip circumference {trend} by {abs(hip_change):.1f}cm")
        
        # Process chest change
        if "bustGirth" in measurements:
            chest_change = measurements["bustGirth"].change
            if abs(chest_change) >= 1.0:
                trend = "decreased" if chest_change < 0 else "increased"
                significant_changes.append(f"Chest circumference {trend} by {abs(chest_change):.1f}cm")
        
        # Process arm change
        if "upperArmGirthR" in measurements:
            arm_change = measurements["upperArmGirthR"].change
            if abs(arm_change) >= 0.5:
                trend = "decreased" if arm_change < 0 else "increased"
                significant_changes.append(f"Arm circumference {trend} by {abs(arm_change):.1f}cm")
        
        # Process thigh change
        if "thighGirthR" in measurements:
            thigh_change = measurements["thighGirthR"].change
            if abs(thigh_change) >= 0.5:
                trend = "decreased" if thigh_change < 0 else "increased"
                significant_changes.append(f"Thigh circumference {trend} by by {abs(arm_change):.1f}cm")