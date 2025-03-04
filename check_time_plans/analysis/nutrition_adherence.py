from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from first_time_plans.call_llm_class import BaseLLM
import logging

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class NutritionInsight(BaseModel):
    """Insight about a specific nutrition pattern or issue."""
    insight_type: str = Field(..., description="Type of insight (e.g., 'macro_imbalance', 'meal_timing', 'food_quality')")
    description: str = Field(..., description="Detailed description of the insight")
    evidence: str = Field(..., description="Evidence from the data supporting this insight")
    impact_level: str = Field(..., description="Impact on client's progress (low, medium, high)")
    recommendation: str = Field(..., description="Recommendation related to this insight")

class CompliancePattern(BaseModel):
    """Pattern of adherence detected in nutrition data."""
    pattern_name: str = Field(..., description="Name of the detected pattern")
    description: str = Field(..., description="Description of the pattern")
    timeframe: str = Field(..., description="When this pattern occurs (e.g., weekends, mornings)")
    impact: str = Field(..., description="Impact on overall nutrition goals")

class NutritionAdherenceAnalysis(BaseModel):
    """Comprehensive nutrition adherence analysis with insights and patterns."""
    overall_adherence_score: float = Field(..., description="Overall adherence score (0-100)")
    macro_adherence: List[str] = Field(..., description="Adherence score for each macronutrient")
    calorie_adherence: float = Field(..., description="Adherence to calorie targets (%)")
    primary_nutrition_issues: List[str] = Field(..., description="Primary issues affecting nutrition adherence")
    compliance_patterns: List[CompliancePattern] = Field(..., description="Detected patterns in meal compliance")
    nutrition_insights: List[NutritionInsight] = Field(..., description="Detailed insights about nutrition patterns")
    strengths: List[str] = Field(..., description="Areas of strong adherence")
    improvement_areas: List[str] = Field(..., description="Areas needing improvement")
    nutrition_recommendations: List[str] = Field(..., description="General recommendations for improving nutrition adherence")
    metabolic_adaptation_indicators: Optional[str] = Field(None, description="Indicators of potential metabolic adaptation")

class NutritionAdherenceModule:
    """
    Module for analyzing nutrition adherence data to identify patterns, issues, and opportunities.
    
    This class takes the meal adherence data extracted by MealAdherenceExtractor and performs
    deeper analysis to guide nutrition-related decisions and recommendations.
    """

    def __init__(self, llm_client: Optional[Any] = None):
        """
        Initialize the NutritionAdherenceModule with an optional custom LLM client.
        
        Args:
            llm_client: Custom LLM client implementation. If None, uses the default BaseLLM.
        """
        self.llm_client = llm_client or BaseLLM()
    
    def analyze_meal_compliance(self, meal_adherence_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze meal compliance data to generate deeper nutrition insights.
        
        This method evaluates the meal adherence data to identify patterns, issues,
        and opportunities for improvement in the client's nutrition approach.
        
        Args:
            meal_adherence_data: The meal adherence data extracted by MealAdherenceExtractor
            
        Returns:
            A dictionary containing structured nutrition adherence analysis
        """
        try:
            # Process using the schema-based approach
            schema_result = self._analyze_adherence_schema(meal_adherence_data)
            
            return {
                "nutrition_adherence_analysis": schema_result
            }
            
        except Exception as e:
            logger.error(f"Error analyzing nutrition adherence: {str(e)}")
            raise e
    
    def get_system_message(self) -> str:
        """
        Returns the system message to guide the LLM in nutrition adherence analysis.
        
        The system message establishes the context and criteria for analyzing
        meal compliance according to nutritional science principles.
        
        Returns:
            Formatted system message string
        """
        return (
            "You are a nutrition analyst specializing in pattern recognition and behavior analysis. "
            "Your task is to analyze meal adherence data to identify deeper patterns, "
            "nutritional issues, and opportunities for client improvement.\n\n"
            
            "Apply these principles when analyzing nutrition data:\n"
            "1. **Pattern Recognition**: Identify temporal patterns in adherence (weekdays vs weekends, time of day).\n"
            "2. **Macro Balance Analysis**: Evaluate balance and consistency of macronutrient intake.\n"
            "3. **Behavioral Triggers**: Identify potential triggers for non-adherence.\n"
            "4. **Metabolic Indicators**: Look for signs of metabolic adaptation or plateau.\n"
            "5. **Quality Assessment**: Evaluate food quality beyond simple macro compliance.\n"
            "6. **Sustainability Analysis**: Assess how sustainable the meal plan is for the client.\n"
            "7. **Nutritional Impact**: Evaluate the impact of adherence issues on overall progress.\n\n"
            
            "Your analysis should go beyond basic compliance metrics to provide deeper insights "
            "into nutrition patterns, challenges, and opportunities that can guide personalized recommendations."
        )
    
    def _analyze_adherence_schema(self, meal_adherence_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze nutrition adherence using Pydantic schema validation.
        
        Args:
            meal_adherence_data: The meal adherence data from extractor
            
        Returns:
            Structured nutrition adherence analysis as a Pydantic model
        """
        # Extract relevant data from meal adherence data
        meal_adherence_analysis = meal_adherence_data.get("meal_adherence_analysis", {})
        
        # Extract compliance metrics
        compliance_metrics = meal_adherence_analysis.get("compliance_metrics", {})
        meal_specific_adherence = meal_adherence_analysis.get("meal_specific_adherence", [])
        challenging_meals = meal_adherence_analysis.get("most_challenging_meals", [])
        consistent_meals = meal_adherence_analysis.get("most_consistent_meals", [])
        adherence_trends = meal_adherence_analysis.get("adherence_trends", "")
        practical_challenges = meal_adherence_analysis.get("practical_challenges", [])
        
        # Construct detailed prompt with comprehensive adherence data
        prompt = (
            "Analyze this client's nutrition adherence data to identify deeper patterns, issues, "
            "and opportunities for improvement. Go beyond basic compliance metrics to provide "
            "insights that can guide personalized nutrition recommendations.\n\n"
            
            f"COMPLIANCE METRICS:\n{self._format_dict(compliance_metrics)}\n\n"
            f"MEAL-SPECIFIC ADHERENCE:\n{self._format_list(meal_specific_adherence)}\n\n"
            f"CHALLENGING MEALS:\n{self._format_list(challenging_meals)}\n\n"
            f"CONSISTENT MEALS:\n{self._format_list(consistent_meals)}\n\n"
            f"ADHERENCE TRENDS:\n{adherence_trends}\n\n"
            f"PRACTICAL CHALLENGES:\n{self._format_list(practical_challenges)}\n\n"
            
            "Your nutrition adherence analysis should include:\n"
            "1. Overall adherence score and macro-specific scores\n"
            "2. Identified compliance patterns (temporal, situational)\n"
            "3. Primary nutrition issues affecting progress\n"
            "4. Detailed insights with supporting evidence\n"
            "5. Areas of strength and areas needing improvement\n"
            "6. Potential indicators of metabolic adaptation\n"
            "7. Targeted recommendations based on the analysis\n\n"
            
            "Create a comprehensive nutrition adherence analysis with actionable insights."
        )
        
        system_message = self.get_system_message()
        result = self.llm_client.call_llm(prompt, system_message, schema=NutritionAdherenceAnalysis)
        return result
    
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