from typing import Dict, Any, Optional
from pydantic import BaseModel
from first_time_plans.call_llm_class import BaseLLM
import logging

class BodyMetricsExtractor:
    """
    Extracts and analyzes client body measurement data using LLM.
    """
    def __init__(self, llm_client: Optional[Any] = None):
        """
        Initialize the BodyMetricsExtractor with an optional custom LLM client.
        """
        self.llm_client = llm_client or BaseLLM()
        self.logger = logging.getLogger(__name__)
    
    def extract_body_measurements(self, body_measurements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process body measurement data using LLM analysis.
        """
        try:
            # Validate basic input
            if not body_measurements or 'measurements' not in body_measurements:
                raise ValueError("Invalid or empty body measurements data")
            
            # Prepare prompt for LLM
            prompt = self._create_body_metrics_prompt(body_measurements)
            
            # System message to guide LLM analysis
            system_message = (
                "You are a body composition expert. Analyze the client's body measurements, "
                "focusing on key changes, trends, and potential insights. "
                "Provide a concise, actionable summary of the body composition data."
            )
            
            # Call LLM for analysis
            analysis_result = self.llm_client.call_llm(
                prompt, 
                system_message
            )
            
            return {
                "original_measurements": body_measurements,
                "llm_analysis": analysis_result
            }
        
        except Exception as e:
            self.logger.error(f"Error in body metrics extraction: {str(e)}")
            return {
                "error": str(e),
                "original_measurements": body_measurements
            }
    
    def _create_body_metrics_prompt(self, body_measurements: Dict[str, Any]) -> str:
        """
        Create a detailed prompt for LLM analysis of body measurements.
        """
        # Format measurements for clear LLM input
        dates = body_measurements.get('dates', {})
        measurements = body_measurements.get('measurements', {})
        
        prompt = "Body Measurement Analysis:\n"
        
        # Add date context
        prompt += f"Measurement Period:\n"
        prompt += f"- Current Date: {dates.get('current', 'N/A')}\n"
        prompt += f"- Previous Date: {dates.get('previous', 'N/A')}\n\n"
        
        # Add detailed measurements
        prompt += "Detailed Measurements:\n"
        for name, data in measurements.items():
            prompt += f"{name.title()}:\n"
            prompt += f"  - Current: {data.get('current', 'N/A')} {data.get('unit', '')}\n"
            prompt += f"  - Previous: {data.get('previous', 'N/A')} {data.get('unit', '')}\n"
            prompt += f"  - Change: {data.get('change', 'N/A')} {data.get('unit', '')}\n\n"
        
        # Add analysis request
        prompt += "Analysis Request:\n"
        prompt += "1. Summarize key body composition changes\n"
        prompt += "2. Highlight any significant trends\n"
        prompt += "3. Provide insights for potential program adjustments\n"
        
        return prompt