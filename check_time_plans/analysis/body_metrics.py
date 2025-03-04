from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from first_time_plans.call_llm_class import BaseLLM
import logging

class BodyCompositionMetrics(BaseModel):
    """Detailed metrics of body composition changes."""
    weight_change: float = Field(..., description="Total weight change")
    weight_change_percentage: float = Field(..., description="Percentage of weight change")
    body_fat_change: Optional[float] = Field(None, description="Change in body fat percentage")
    lean_mass_change: Optional[float] = Field(None, description="Change in lean muscle mass")
    lean_mass_change_percentage: Optional[float] = Field(None, description="Percentage change in lean mass")
    bmi_change: Optional[float] = Field(None, description="Change in Body Mass Index")
    waist_measurement_change: float = Field(..., description="Change in waist circumference")

class BodyProportionAssessment(BaseModel):
    """Assessment of body proportions and symmetry."""
    upper_lower_balance: str = Field(..., description="Balance between upper and lower body development")
    left_right_symmetry: str = Field(..., description="Symmetry between left and right body sides")
    anterior_posterior_balance: str = Field(..., description="Balance between front and back body measurements")
    measurement_ratios: List[List[str]] = Field(..., description="Key body measurement ratios")
    proportion_observations: str = Field(..., description="Qualitative observations about body proportions")

class BodyMetricsAnalysis(BaseModel):
    """Comprehensive analysis of body metrics and changes."""
    composition_metrics: BodyCompositionMetrics
    proportion_assessment: BodyProportionAssessment
    specific_measurement_changes: List[List[str]]
    trending_measurements: List[str]
    primary_change_areas: List[str]
    stable_measurements: List[str]
    change_rate_assessment: str
    visual_impact_assessment: str
    body_recomposition_indicators: str
    health_marker_implications: str

class BodyMetricsModule:
    """
    Module for analyzing body metrics and composition changes.
    
    This class processes body measurement data to provide comprehensive 
    insights into physiological changes, body composition, and health markers.
    """

    def __init__(self, llm_client: Optional[Any] = None):
        """
        Initialize the BodyMetricsModule with an optional custom LLM client.
        
        Args:
            llm_client: Custom LLM client implementation. If None, uses the default BaseLLM.
        """
        self.llm_client = llm_client or BaseLLM()
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    def analyze_body_changes(self, body_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze body measurement data to assess composition changes and health markers.
        
        Args:
            body_data: The body measurements data extracted by BodyMetricsExtractor
            
        Returns:
            A dictionary containing structured body metrics analysis
        """
        try:
            # Process using the schema-based approach
            schema_result = self._analyze_body_metrics_schema(body_data)
            
            return {
                "body_metrics_analysis": schema_result
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing body metrics: {str(e)}")
            raise e

    def get_system_message(self) -> str:
        """
        Returns the system message to guide the LLM in body metrics analysis.
        
        Returns:
            Formatted system message string
        """
        return (
            "You are a body composition and fitness analysis expert specializing in "
            "interpreting physical measurements and body changes. Your task is to provide "
            "a comprehensive, scientific analysis of body metrics data.\n\n"
            
            "Key Analysis Principles:\n"
            "1. Holistic body composition assessment\n"
            "2. Identification of physiological changes and trends\n"
            "3. Health and fitness implications of measurements\n"
            "4. Body proportion and symmetry evaluation\n"
            "5. Potential indicators of training effectiveness\n\n"
            
            "Provide insights that go beyond raw numbers, offering contextual "
            "and actionable interpretations of body measurements."
        )

    def _analyze_body_metrics_schema(self, body_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze body metrics using Pydantic schema validation.
        
        Args:
            body_data: The body metrics data from extractor
            
        Returns:
            Structured body metrics analysis as a Pydantic model
        """
        # Extract relevant data from body metrics data
        body_metrics_analysis = body_data.get("body_metrics_analysis", {})
        
        # Prepare comprehensive prompt for LLM analysis
        prompt = (
            "Perform a detailed analysis of the following body metrics data:\n\n"
            f"COMPOSITION METRICS:\n{self._format_dict(body_metrics_analysis.get('composition_metrics', {}))}\n\n"
            f"PROPORTION ASSESSMENT:\n{self._format_dict(body_metrics_analysis.get('proportion_assessment', {}))}\n\n"
            f"SPECIFIC MEASUREMENT CHANGES:\n{self._format_list(body_metrics_analysis.get('specific_measurement_changes', []))}\n\n"
            f"TRENDING MEASUREMENTS:\n{', '.join(body_metrics_analysis.get('trending_measurements', []))}\n\n"
            f"PRIMARY CHANGE AREAS:\n{', '.join(body_metrics_analysis.get('primary_change_areas', []))}\n\n"
            
            "Provide a comprehensive analysis covering:\n"
            "1. Detailed interpretation of body composition changes\n"
            "2. Assessment of body proportion and symmetry\n"
            "3. Potential health and fitness implications\n"
            "4. Recommendations for training and nutrition\n"
            "5. Insights into body recomposition progress"
        )
        
        system_message = self.get_system_message()
        result = self.llm_client.call_llm(prompt, system_message, schema=BodyMetricsAnalysis)
        return result

    def _format_list(self, data: List[Any]) -> str:
        """Format list into readable string."""
        if not data:
            return "None available"
        
        formatted = ""
        for item in data:
            if isinstance(item, dict):
                formatted += f"- {self._format_dict(item)}\n"
            else:
                formatted += f"- {item}\n"
        return formatted
    
    def _format_dict(self, data: Dict[str, Any]) -> str:
        """Format dictionary into readable string."""
        if not data:
            return "No data available"
        
        formatted = ""
        for key, value in data.items():
            formatted += f"  {key}: {value}\n"
        return formatted