from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from first_time_plans.call_llm_class import BaseLLM
import json
import logging

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

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
    measurement_ratios: Dict[str, float] = Field(..., description="Key measurement ratios (e.g., waist-to-hip, shoulder-to-waist)")
    proportion_observations: str = Field(..., description="Notable observations about body proportions")

class BodyMetricsAnalysis(BaseModel):
    """Comprehensive analysis of body measurement and composition data."""
    composition_metrics: BodyCompositionMetrics = Field(..., description="Body composition change metrics")
    proportion_assessment: Optional[BodyProportionAssessment] = Field(None, description="Body proportion assessment")
    specific_measurement_changes: Dict[str, float] = Field(..., description="Changes in specific body measurements")
    trending_measurements: List[str] = Field(..., description="Measurements showing most significant changes")
    primary_change_areas: List[str] = Field(..., description="Body areas showing most significant changes")
    stable_measurements: List[str] = Field(..., description="Measurements showing minimal change")
    change_rate_assessment: str = Field(..., description="Assessment of change rate relative to goals")
    visual_impact_assessment: str = Field(..., description="Assessment of aesthetic impact of changes")
    body_recomposition_indicators: str = Field(..., description="Indicators of simultaneous fat loss and muscle gain")
    health_marker_implications: str = Field(..., description="Implications for health markers based on changes")

class BodyMetricsExtractor:
    """
    Extracts and analyzes client body measurement data.
    
    This class processes body measurement data to evaluate changes in body composition,
    proportions, and specific measurements over time, providing insights for
    program effectiveness and goal alignment.
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
        
        This method evaluates changes in body weight, composition, and specific
        measurements to assess progress toward physique-related goals.
        
        Args:
            body_measurements: The client's body measurement data over time
            
        Returns:
            A dictionary containing structured body metrics analysis
        """
        try:
            # Process using the schema-based approach
            schema_result = self._analyze_body_metrics_schema(body_measurements)
            
            return {
                "body_metrics_analysis": schema_result
            }
            
        except Exception as e:
            logger.error(f"Error analyzing body metrics: {str(e)}")
            raise e
    
    def get_system_message(self) -> str:
        """
        Returns the system message to guide the LLM in body metrics analysis.
        
        The system message establishes the context and criteria for analyzing
        body measurement data according to physiological principles.
        
        Returns:
            Formatted system message string
        """
        return (
            "You are a body composition specialist with expertise in physiological assessment. "
            "Your task is to analyze a client's body measurement data to evaluate changes in "
            "body composition, proportions, and specific measurements over time.\\n\\n"
            
            "Apply these principles when analyzing body metrics:\\n"
            "1. **Composition Analysis**: Evaluate changes in weight, body fat, and lean mass.\\n"
            "2. **Proportion Assessment**: Analyze balance and symmetry in development.\\n"
            "3. **Measurement Changes**: Track specific measurement changes and their significance.\\n"
            "4. **Rate Analysis**: Assess the rate of change relative to physiological norms.\\n"
            "5. **Visual Impact**: Consider the aesthetic implications of measured changes.\\n"
            "6. **Recomposition Indicators**: Identify signs of simultaneous fat loss and muscle gain.\\n"
            "7. **Health Implications**: Consider health marker implications of body composition changes.\\n\\n"
            
            "Your analysis should provide insights about the client's physiological changes, "
            "highlighting both positive developments and areas for attention, with practical "
            "implications for program adjustment to optimize results."
        )
    
    def _analyze_body_metrics_schema(self, body_measurements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze body metrics using Pydantic schema validation.
        
        Args:
            body_measurements: The client's body measurement data
            
        Returns:
            Structured body metrics analysis as a Pydantic model
        """
        # Extract measurement dates
        dates = body_measurements.get("dates", {})
        current_date = dates.get("current", "Current")
        previous_date = dates.get("previous", "Previous")
        
        # Extract measurements
        measurements = body_measurements.get("measurements", {})
        measurement_names = list(measurements.keys())
        
        # Construct detailed prompt with body measurement data
        prompt = (
            "Analyze this client's body measurement data to evaluate changes in body composition, "
            "proportions, and specific measurements. Identify patterns, notable changes, and implications "
            "for program adjustment.\\n\\n"
            
            f"MEASUREMENT DATES:\\n"
            f"- Current: {current_date}\\n"
            f"- Previous: {previous_date}\\n\\n"
            
            f"MEASUREMENTS SUMMARY:\\n"
            f"- Number of measurements: {len(measurement_names)}\\n"
            f"- Measurement types: {', '.join(measurement_names)}\\n\\n"
            
            f"DETAILED MEASUREMENTS:\\n{self._format_measurements(measurements)}\\n\\n"
            
            "Your body metrics analysis should include:\\n"
            "1. Body composition change metrics\\n"
            "2. Assessment of body proportions and symmetry\\n"
            "3. Analysis of specific measurement changes\\n"
            "4. Identification of trending and stable measurements\\n"
            "5. Assessment of change rate relative to goals\\n"
            "6. Implications for program adjustment\\n\\n"
            
            "Create a complete body metrics analysis with practical insights for optimization."
        )
        
        system_message = self.get_system_message()
        result = self.llm_client.call_llm(prompt, system_message, schema=BodyMetricsAnalysis)
        return result
    
    def _format_measurements(self, measurements: Dict[str, Any]) -> str:
        """
        Format measurement data as a readable string for inclusion in prompts.
        
        Args:
            measurements: Dictionary of body measurements
            
        Returns:
            Formatted string representation
        """
        if not measurements:
            return "No measurement data available."
        
        formatted = ""
        for name, data in measurements.items():
            current = data.get("current", "N/A")
            previous = data.get("previous", "N/A")
            unit = data.get("unit", "")
            change = data.get("change", "N/A")
            
            formatted += f"  {name.title()}:\\n"
            formatted += f"    - Current: {current} {unit}\\n"
            formatted += f"    - Previous: {previous} {unit}\\n"
            formatted += f"    - Change: {change} {unit}\\n"
            
            # Calculate percentage change if possible
            if isinstance(current, (int, float)) and isinstance(previous, (int, float)) and previous != 0:
                pct_change = (current - previous) / previous * 100
                formatted += f"    - Percentage change: {pct_change:.2f}%\\n"
            
            formatted += "\\n"
        
        return formatted
    
    def _format_dict(self, data: Dict[str, Any]) -> str:
        """
        Format a dictionary as a readable string for inclusion in prompts.
        
        Args:
            data: Dictionary to format
            
        Returns:
            Formatted string representation
        """
        try:
            return json.dumps(data, indent=2)
        except:
            # Fallback for non-serializable objects
            return str(data)