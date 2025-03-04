from typing import Dict, Any, List
from pydantic import BaseModel, Field
from first_time_plans.call_llm_class import BaseLLM
import logging

class NutritionAdjustment(BaseModel):
    """Structured nutrition modification recommendation."""
    adjustment_type: str = Field(..., description="Type of nutrition adjustment")
    macro_modifications: Dict[str, float] = Field(..., description="Recommended changes in macronutrient intake")
    calorie_adjustment: float = Field(..., description="Recommended calorie intake change")
    meal_timing_recommendations: List[str] = Field(..., description="Suggestions for meal timing and frequency")
    rationale: str = Field(..., description="Explanation for the nutrition adjustments")
    priority_level: int = Field(default=3, ge=1, le=5, description="Priority of nutrition adjustment")

class NutritionAdjustmentNode:
    """
    Decision node for determining targeted nutrition changes based on analysis and goal alignment.
    """
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client or BaseLLM()
        self.logger = logging.getLogger(__name__)
    
    def determine_nutrition_changes(
        self, 
        nutrition_analysis: Dict[str, Any], 
        goal_alignment: Dict[str, Any]
    ) -> NutritionAdjustment:
        """
        Generate nutrition adjustments based on nutrition analysis and goal progress.
        
        Args:
            nutrition_analysis: Comprehensive nutrition adherence analysis
            goal_alignment: Goal progress assessment
        
        Returns:
            Structured nutrition adjustment recommendations
        """
        try:
            prompt = self._construct_nutrition_adjustment_prompt(
                nutrition_analysis, 
                goal_alignment
            )
            system_message = self._get_nutrition_adjustment_system_message()
            
            nutrition_adjustment = self.llm_client.call_llm(
                prompt, 
                system_message, 
                schema=NutritionAdjustment
            )
            
            return nutrition_adjustment
        
        except Exception as e:
            self.logger.error(f"Error determining nutrition changes: {e}")
            raise
    
    def _construct_nutrition_adjustment_prompt(
        self, 
        nutrition_analysis: Dict[str, Any], 
        goal_alignment: Dict[str, Any]
    ) -> str:
        """
        Construct a comprehensive prompt for nutrition adjustment recommendations.
        """
        nutrition_adherence = nutrition_analysis.get('nutrition_adherence_analysis', {})
        
        return (
            "Generate precise nutrition adjustments based on the following analysis:\n\n"
            
            "NUTRITION ADHERENCE:\n"
            f"Overall Adherence Score: {nutrition_adherence.get('overall_adherence_score', 'N/A')}%\n"
            f"Macro Adherence: {', '.join(nutrition_adherence.get('macro_adherence', ['N/A']))}\n"
            f"Calorie Adherence: {nutrition_adherence.get('calorie_adherence', 'N/A')}%\n\n"
            
            "PRIMARY NUTRITION ISSUES:\n" +
            "\n".join([
                f"- {issue}" for issue in nutrition_adherence.get('primary_nutrition_issues', [])
            ]) + "\n\n"
            
            "GOAL CONTEXT:\n"
            "- Weekly Goal: Increase bench press by 5kg while maintaining current body weight\n"
            "- Monthly Goal: Add 2cm to arm circumference while improving overall conditioning\n"
            "- Quarterly Goal: Reach 45kg body weight with 15% body fat and improve all major lifts by 10%\n\n"
            
            "GOAL ALIGNMENT:\n"
            f"Goal Progress: {goal_alignment.get('overall_goal_progress', 'N/A')}%\n"
            f"Goal Alignment Status: {goal_alignment.get('goal_alignment_status', 'N/A')}\n\n"
            
            "Provide nutrition adjustment recommendations that:\n"
            "1. Address current nutritional deficiencies\n"
            "2. Support stated fitness goals\n"
            "3. Improve macro and calorie intake\n"
            "4. Enhance meal timing and consistency\n"
            "5. Offer practical, implementable strategies"
        )
    
    def _get_nutrition_adjustment_system_message(self) -> str:
        """Define system instructions for nutrition adjustment."""
        return (
            "You are a sports nutritionist specializing in performance-driven nutrition strategies. "
            "Your recommendations must be scientifically grounded, personalized, and aligned with "
            "specific fitness goals. Focus on creating actionable, practical nutrition plans."
        )
