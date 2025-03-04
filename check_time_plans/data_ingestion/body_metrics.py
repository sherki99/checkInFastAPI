from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field
from first_time_plans.call_llm_class import BaseLLM
import json
import logging

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class MeasurementRatio(BaseModel):
    """Represents a measurement ratio with name and value."""
    name: str
    value: float

class BodyCompositionMetrics(BaseModel):
    """Metrics for body composition changes."""
    weight_change: float = Field(..., description="Change in body weight (in kg/lbs)")
    weight_change_percentage: float = Field(..., description="Percentage change in body weight")
    body_fat_change: Optional[float] = Field(None, description="Change in body fat percentage")
    lean_mass_change: Optional[float] = Field(None, description="Change in lean body mass (in kg/lbs)")
    lean_mass_change_percentage: Optional[float] = Field(None, description="Percentage change in lean mass")
    bmi_change: Optional[float] = Field(None, description="Change in BMI")
    waist_measurement_change: Optional[float] = Field(None, description="Change in waist measurement (in cm/inches)")

class BodyProportionAssessment(BaseModel):
    """Assessment of body proportions and symmetry."""
    upper_lower_balance: str = Field(..., description="Assessment of upper vs. lower body development")
    left_right_symmetry: str = Field(..., description="Assessment of left-right symmetry")
    anterior_posterior_balance: str = Field(..., description="Assessment of front vs. back muscle development")
    measurement_ratios: List[MeasurementRatio] = Field(..., description="Key measurement ratios (e.g., waist-to-hip, shoulder-to-waist)")
    proportion_observations: str = Field(..., description="Notable observations about body proportions")

class MeasurementChange(BaseModel):
    """Represents a specific body measurement change."""
    name: str
    change: float
    description: Optional[str] = None
    unit: Optional[str] = None

class BodyMetricsAnalysis(BaseModel):
    """Comprehensive analysis of body measurement and composition data."""
    composition_metrics: BodyCompositionMetrics
    proportion_assessment: Optional[BodyProportionAssessment] = None
    specific_measurement_changes: List[MeasurementChange] = []
    trending_measurements: List[str] = []
    primary_change_areas: List[str] = []
    stable_measurements: List[str] = []
    change_rate_assessment: str = ""
    visual_impact_assessment: str = ""
    body_recomposition_indicators: str = ""
    health_marker_implications: str = ""

    class Config:
        extra = 'ignore'
        allow_population_by_field_name = True

class BodyMetricsExtractor:
    """
    Extracts and analyzes client body measurement data with advanced processing capabilities.
    """

    def __init__(self, llm_client: Optional[Any] = None):
        """
        Initialize the BodyMetricsExtractor with an optional custom LLM client.
        
        Args:
            llm_client: Custom LLM client implementation. If None, uses the default BaseLLM.
        """
        self.llm_client = llm_client or BaseLLM()
    
    def extract_body_measurements(self, body_measurements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process body measurement data to analyze changes and patterns.
        
        Args:
            body_measurements: The client's body measurement data over time
            
        Returns:
            A dictionary containing structured body metrics analysis
        """
        try:
            # Validate input data structure
            self._validate_input_data(body_measurements)
            
            # Process using the schema-based approach
            schema_result = self._analyze_body_metrics_schema(body_measurements)
            
            return {
                "body_metrics_analysis": schema_result
            }
            
        except Exception as e:
            logger.error(f"Error analyzing body metrics: {str(e)}")
            raise
    
    def _validate_input_data(self, body_measurements: Dict[str, Any]) -> None:
        """
        Validate the input body measurement data structure.
        
        Args:
            body_measurements: Input data to validate
        
        Raises:
            ValueError: If the input data is invalid
        """
        if not body_measurements:
            raise ValueError("Body measurements data is empty")
        
        if "dates" not in body_measurements:
            raise ValueError("Missing 'dates' in body measurements")
        
        if "measurements" not in body_measurements:
            raise ValueError("Missing 'measurements' in body measurements")
    
    def get_system_message(self) -> str:
        """
        Returns the system message to guide the LLM in body metrics analysis.
        
        Returns:
            Formatted system message string
        """
        return (
            "You are a body composition specialist with expertise in physiological assessment. "
            "Your task is to analyze a client's body measurement data to evaluate changes in "
            "body composition, proportions, and specific measurements over time.\n\n"
            
            "Analysis Principles:\n"
            "1. Composition Analysis: Evaluate changes in weight, body fat, and lean mass.\n"
            "2. Proportion Assessment: Analyze balance and symmetry in development.\n"
            "3. Measurement Changes: Track specific measurement changes and their significance.\n"
            "4. Rate Analysis: Assess the rate of change relative to physiological norms.\n"
            "5. Visual Impact: Consider the aesthetic implications of measured changes.\n"
            "6. Recomposition Indicators: Identify signs of simultaneous fat loss and muscle gain.\n"
            "7. Health Implications: Consider health marker implications of body composition changes.\n\n"
            
            "Provide comprehensive insights about the client's physiological changes, "
            "highlighting positive developments and areas for attention, with practical "
            "implications for program adjustment."
        )
    
    def _analyze_body_metrics_schema(self, body_measurements: Dict[str, Any]) -> BodyMetricsAnalysis:
        """
        Analyze body metrics using Pydantic schema validation and LLM analysis.
        
        Args:
            body_measurements: The client's body measurement data
            
        Returns:
            Structured body metrics analysis
        """
        # Extract measurement context
        dates = body_measurements.get("dates", {})
        current_date = dates.get("current", "Current")
        previous_date = dates.get("previous", "Previous")
        
        # Extract measurements
        measurements = body_measurements.get("measurements", {})
        
        # Prepare detailed prompt
        prompt = self._construct_detailed_prompt(current_date, previous_date, measurements)
        
        # Prepare system message
        system_message = self.get_system_message()
        
        # Call LLM with structured request
        result = self.llm_client.call_llm(
            prompt, 
            system_message, 
            schema=BodyMetricsAnalysis
        )
        
        return result
    
    def _construct_detailed_prompt(self, current_date: str, previous_date: str, measurements: Dict) -> str:
        """
        Construct a detailed prompt for LLM analysis.
        
        Args:
            current_date: Current measurement date
            previous_date: Previous measurement date
            measurements: Detailed measurements dictionary
        
        Returns:
            Formatted prompt string
        """
        # Format measurement details
        measurement_summary = self._format_measurements(measurements)
        
        return (
            "Perform a comprehensive analysis of body measurement data:\n\n"
            f"MEASUREMENT CONTEXT:\n"
            f"- Current Date: {current_date}\n"
            f"- Previous Date: {previous_date}\n\n"
            
            f"MEASUREMENT DETAILS:\n{measurement_summary}\n\n"
            
            "Analysis Requirements:\n"
            "1. Calculate key body composition metrics\n"
            "2. Assess body proportions and symmetry\n"
            "3. Identify significant measurement changes\n"
            "4. Evaluate change rate and potential implications\n"
            "5. Provide insights for program optimization\n\n"
            
            "Deliver a detailed, actionable body metrics analysis."
        )
    
    def _format_measurements(self, measurements: Dict[str, Any]) -> str:
        """
        Format measurement data as a readable string for LLM analysis.
        
        Args:
            measurements: Dictionary of body measurements
        
        Returns:
            Formatted string representation of measurements
        """
        if not measurements:
            return "No measurement data available."
        
        formatted_measurements = []
        for name, data in measurements.items():
            current = data.get("current", "N/A")
            previous = data.get("previous", "N/A")
            unit = data.get("unit", "")
            change = data.get("change", "N/A")
            
            measurement_str = (
                f"{name.title()}:\n"
                f"  - Current: {current} {unit}\n"
                f"  - Previous: {previous} {unit}\n"
                f"  - Change: {change} {unit}"
            )
            
            # Calculate percentage change if possible
            try:
                current_val = float(current)
                previous_val = float(previous)
                if previous_val != 0:
                    pct_change = (current_val - previous_val) / previous_val * 100
                    measurement_str += f"\n  - Percentage Change: {pct_change:.2f}%"
            except (ValueError, TypeError):
                pass
            
            formatted_measurements.append(measurement_str)
        
        return "\n\n".join(formatted_measurements)