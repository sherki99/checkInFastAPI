from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from first_time_plans.call_llm_class import BaseLLM
import logging

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class CompositionInsight(BaseModel):
    """Insight about body composition changes."""
    insight_type: str = Field(..., description="Type of composition insight (e.g., 'fat_loss', 'muscle_gain', 'water_retention')")
    description: str = Field(..., description="Detailed description of the composition change")
    evidence: str = Field(..., description="Evidence from measurements supporting this insight")
    physiological_explanation: str = Field(..., description="Physiological explanation of the observation")
    significance: str = Field(..., description="Significance relative to goals")

class PhysiqueAssessment(BaseModel):
    """Assessment of physique development and changes."""
    overall_development: str = Field(..., description="Assessment of overall physique development")
    structural_balance: str = Field(..., description="Evaluation of structural balance and proportions")
    symmetry_assessment: str = Field(..., description="Assessment of left-right symmetry")
    aesthetic_development: str = Field(..., description="Evaluation of aesthetic development")
    physiological_health_indicators: List[str] = Field(..., description="Indicators of physiological health from measurements")

class BodyMetricsDeepAnalysis(BaseModel):
    """Comprehensive analysis of body metrics with physiological insights."""
    metrics_quality_score: float = Field(..., description="Quality score for the metrics data (0-100)")
    measurement_accuracy_assessment: str = Field(..., description="Assessment of measurement accuracy and consistency")
    change_rate_evaluation: str = Field(..., description="Evaluation of change rate relative to biological norms")
    composition_insights: List[CompositionInsight] = Field(..., description="Insights about body composition changes")
    physique_assessment: PhysiqueAssessment = Field(..., description="Assessment of physique development")
    body_fat_distribution_changes: Optional[str] = Field(None, description="Analysis of changes in body fat distribution")
    water_retention_assessment: str = Field(..., description="Assessment of water retention/balance")
    metabolic_health_indicators: List[str] = Field(..., description="Indicators of metabolic health from body metrics")
    primary_adaptation_patterns: List[str] = Field(..., description="Primary physiological adaptation patterns observed")
    measurement_recommendations: List[str] = Field(..., description="Recommendations for future measurements")
    body_composition_targets: Dict[str, Any] = Field(..., description="Suggested targets for body composition")

class BodyMetricsModule:
    """
    Module for analyzing body measurement data to assess physiological changes and adaptations.
    
    This class takes the body metrics data extracted by BodyMetricsExtractor and performs
    deeper analysis to guide physique development and body composition strategies.
    """

    def __init__(self, llm_client: Optional[Any] = None):
        """
        Initialize the BodyMetricsModule with an optional custom LLM client.
        
        Args:
            llm_client: Custom LLM client implementation. If None, uses the default BaseLLM.
        """
        self.llm_client = llm_client or BaseLLM()
    
    def analyze_body_changes(self, body_metrics_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze body measurement data to assess physiological changes.
        
        This method evaluates the body metrics data to identify patterns, changes,
        and opportunities for improvement in body composition and physique development.
        
        Args:
            body_metrics_data: The body metrics data extracted by BodyMetricsExtractor
            
        Returns:
            A dictionary containing structured body metrics analysis
        """
        try:
            # Process using the schema-based approach
            schema_result = self._analyze_metrics_schema(body_metrics_data)
            
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
        body measurements according to physiological principles.
        
        Returns:
            Formatted system message string
        """
        return (
            "You are a body composition specialist with expertise in physiological assessment and adaptation. "
            "Your task is to analyze body measurement data to assess composition changes, physiological adaptations, "
            "and provide insights for optimizing body composition strategies.\n\n"
            
            "Apply these principles when analyzing body metrics:\n"
            "1. **Composition Change Analysis**: Differentiate between fat loss, muscle gain, and water balance changes.\n"
            "2. **Physiological Context**: Interpret changes within physiological norms and adaptation principles.\n"
            "3. **Structural Assessment**: Evaluate balance, symmetry, and proportional development.\n"
            "4. **Health Indicator Analysis**: Identify health implications from body composition changes.\n"
            "5. **Adaptational Patterns**: Recognize patterns indicative of specific adaptational responses.\n"
            "6. **Measurement Quality Assessment**: Evaluate consistency and reliability of measurements.\n"
            "7. **Goal-Specific Context**: Interpret changes relative to specific physique or performance goals.\n\n"
            
            "Your analysis should provide physiologically-grounded insights about body composition changes, "
            "identify patterns of adaptation, and offer targeted recommendations for optimization."
        )
    
    def _analyze_metrics_schema(self, body_metrics_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze body metrics using Pydantic schema validation.
        
        Args:
            body_metrics_data: The body metrics data from extractor
            
        Returns:
            Structured body metrics analysis as a Pydantic model



        """
        try:
            # Ensure body_metrics_data is a dictionary
            if not isinstance(body_metrics_data, dict):
                raise ValueError("Input must be a dictionary")

            # Extract body metrics analysis, defaulting to an empty dictionary
            body_metrics_analysis = body_metrics_data.get("body_metrics_analysis", {})
            
            # Ensure body_metrics_analysis is a dictionary
            if not isinstance(body_metrics_analysis, dict):
                logger.warning("body_metrics_analysis is not a dictionary. Defaulting to empty dict.")
                body_metrics_analysis = {}

            # Extract metrics components with safe defaults
            composition_metrics = body_metrics_analysis.get("composition_metrics", {})
            proportion_assessment = body_metrics_analysis.get("proportion_assessment", {})
            specific_measurement_changes = body_metrics_analysis.get("specific_measurement_changes", {})
            trending_measurements = body_metrics_analysis.get("trending_measurements", [])
            primary_change_areas = body_metrics_analysis.get("primary_change_areas", [])
            stable_measurements = body_metrics_analysis.get("stable_measurements", [])
            change_rate_assessment = body_metrics_analysis.get("change_rate_assessment", "No assessment available")
            visual_impact = body_metrics_analysis.get("visual_impact_assessment", "No visual impact analysis")
            recomposition_indicators = body_metrics_analysis.get("body_recomposition_indicators", "No recomposition indicators")
            health_implications = body_metrics_analysis.get("health_marker_implications", "No health implications noted")

            # Construct detailed prompt with comprehensive body metrics data
            prompt = (
                "Analyze this client's body measurement data to assess physiological changes, adaptations, "
                "and body composition shifts. Apply physiological principles to provide insights that can "
                "guide body composition optimization strategies.\n\n"
                
                f"COMPOSITION METRICS:\n{self._format_dict(composition_metrics)}\n\n"
                f"PROPORTION ASSESSMENT:\n{self._format_dict(proportion_assessment)}\n\n"
                f"SPECIFIC MEASUREMENT CHANGES:\n{self._format_dict(specific_measurement_changes)}\n\n"
                f"TRENDING MEASUREMENTS:\n{self._format_list(trending_measurements)}\n\n"
                f"PRIMARY CHANGE AREAS:\n{self._format_list(primary_change_areas)}\n\n"
                f"STABLE MEASUREMENTS:\n{self._format_list(stable_measurements)}\n\n"
                f"CHANGE RATE ASSESSMENT:\n{change_rate_assessment}\n\n"
                f"VISUAL IMPACT ASSESSMENT:\n{visual_impact}\n\n"
                f"RECOMPOSITION INDICATORS:\n{recomposition_indicators}\n\n"
                f"HEALTH IMPLICATIONS:\n{health_implications}\n\n"
                
                "Your body metrics analysis should include:\n"
                "1. Assessment of measurement quality and consistency\n"
                "2. Evaluation of change rate relative to physiological norms\n"
                "3. Detailed insights about body composition changes with physiological explanations\n"
                "4. Assessment of physique development and structural balance\n"
                "5. Analysis of fat distribution changes and water retention\n"
                "6. Identification of primary adaptation patterns\n"
                "7. Recommendations for measurement protocols and body composition targets\n\n"
                
                "Create a comprehensive body metrics analysis with physiologically-grounded insights."
            )
            
            system_message = self.get_system_message()
            result = self.llm_client.call_llm(prompt, system_message, schema=BodyMetricsDeepAnalysis)
            return result
    
        except Exception as e:
            logger.error(f"Comprehensive error in analyzing body metrics: {str(e)}")
            raise
    

    
    def _format_dict(self, data: Dict[str, Any]) -> str:
        """Format dictionary into readable string."""
        if not data:
            return "No data available"
        
        formatted = ""
        for key, value in data.items():
            formatted += f"- {key}: {value}\n"
        return formatted
    
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