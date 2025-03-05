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
    Nutrition adjustment decision node using LLM to generate personalized recommendations.
    Integrates nutrition analysis, goal alignment, and existing meal plan.
    """
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client or BaseLLM()
        self.logger = logging.getLogger(__name__)
    
    def determine_nutrition_changes(
        self, 
        nutrition_analysis: Dict[str, Any], 
        goal_alignment: Dict[str, Any],
        current_meal_plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate nutrition adjustments using LLM with comprehensive context.
        
        Args:
            nutrition_analysis: Detailed nutrition performance analysis
            goal_alignment: Current goal progress assessment
            current_meal_plan: Existing meal plan details
        
        Returns:
            Nutrition adjustment recommendations
        """
        try:
            # Construct comprehensive prompt
            prompt = self._construct_nutrition_adjustment_prompt(
                nutrition_analysis, 
                goal_alignment, 
                current_meal_plan
            )
            
            # Define system message for context
            system_message = (
                "You are an expert sports nutritionist tasked with creating "
                "precise, personalized nutrition recommendations. Analyze the "
                "provided data holistically and generate actionable adjustments "
                "that support the client's fitness goals."
            )
            
            # Define a flexible output schema
            class NutritionAdjustmentSchema(BaseModel):
                """Schema for capturing nutrition adjustment recommendations"""
                recommended_changes: Dict[str, Any] = Field(
                    description="Comprehensive nutrition adjustment recommendations"
                )
                meal_plan_modifications: Dict[str, Any] = Field(
                    description="Specific modifications to current meal plan"
                )
                rationale: str = Field(
                    description="Explanation of recommended nutrition changes"
                )
            
            # Call LLM with structured prompt and schema
            nutrition_adjustments = self.llm_client.call_llm(
                prompt, 
                system_message, 
                schema=NutritionAdjustmentSchema
            )
            
            # Log the generated adjustments
            self._log_nutrition_adjustments(nutrition_adjustments)
            
            return nutrition_adjustments.dict()
        
        except Exception as e:
            self.logger.error(f"Error in nutrition adjustment generation: {e}")
            raise
    
    def _construct_nutrition_adjustment_prompt(
        self, 
        nutrition_analysis: Dict[str, Any], 
        goal_alignment: Dict[str, Any],
        current_meal_plan: Dict[str, Any]
    ) -> str:
        """
        Create a comprehensive, context-rich prompt for nutrition adjustment.
        
        Args:
            nutrition_analysis: Detailed nutrition performance data
            goal_alignment: Goal progress assessment
            current_meal_plan: Existing meal plan details
        
        Returns:
            Detailed prompt for LLM to generate nutrition recommendations
        """
        # Extract key nutrition analysis details
        adherence_analysis = nutrition_analysis.get('nutrition_adherence_analysis', {})
        
        # Construct prompt with multiple contextual layers
        prompt = (
            "COMPREHENSIVE NUTRITION ADJUSTMENT ANALYSIS\n\n"
            
            "CURRENT NUTRITION PERFORMANCE:\n"
            f"Overall Adherence Score: {adherence_analysis.get('overall_adherence_score', 'N/A')}%\n"
            f"Macro Adherence: {', '.join(adherence_analysis.get('macro_adherence', ['N/A']))}\n"
            f"Calorie Adherence: {adherence_analysis.get('calorie_adherence', 'N/A')}%\n\n"
            
            "PRIMARY NUTRITION CHALLENGES:\n" +
            "\n".join([
                f"- {issue}" for issue in adherence_analysis.get('primary_nutrition_issues', [])
            ]) + "\n\n"
            
            "CURRENT MEAL PLAN STRUCTURE:\n"
            f"Total Daily Nutrition: {current_meal_plan.get('totalDailyNutrition', 'Not Available')}\n"
            "Training Day Meals:\n" +
            "\n".join([
                f"- {meal.get('name', 'Unnamed Meal')}: {meal.get('nutrition', 'No Details')}"
                for meal in current_meal_plan.get('trainingDayMeals', [])
            ]) + "\n\n"
            
            "FITNESS GOAL CONTEXT:\n"
            f"Goal Progress: {goal_alignment.get('overall_goal_progress', 'N/A')}%\n"
            f"Goal Alignment Status: {goal_alignment.get('goal_alignment_status', 'N/A')}\n"
            "Specific Goals:\n"
            "- Increase bench press by 5kg\n"
            "- Maintain current body weight\n"
            "- Improve overall muscle conditioning\n\n"
            
            "REQUIRED RECOMMENDATIONS:\n"
            "1. Modify current meal plan to address nutritional deficiencies\n"
            "2. Align nutrition with specific fitness goals\n"
            "3. Improve macro and calorie intake consistency\n"
            "4. Provide practical, implementable nutrition strategies\n\n"
            
            "Provide comprehensive nutrition adjustment recommendations "
            "that are specific, actionable, and directly tied to the client's "
            "performance and body composition goals."
        )
        
        return prompt
    
    def _log_nutrition_adjustments(self, adjustments: Dict[str, Any]):
        """
        Log nutrition adjustments for tracking and future reference.
        
        Args:
            adjustments: Generated nutrition adjustment recommendations
        """
        try:
            # Log key details about nutrition adjustments
            self.logger.info(
                "Nutrition Adjustments Generated: "
                f"Recommended Changes: {adjustments.get('recommended_changes')}"
            )
        except Exception as e:
            self.logger.error(f"Logging error: {e}")



"""# Example usage in the main processing pipeline
def process_nutrition_adjustments(analysis_data: Dict[str, Any]) -> Dict[str, Any]:
   
    nutrition_adjustment_node = NutritionAdjustmentNode()
    
    nutrition_adjustments = nutrition_adjustment_node.determine_nutrition_changes(
        nutrition_analysis=analysis_data.get('analysisData', {}).get('nutrition_analysis', {}),
        goal_alignment=analysis_data.get('analysisData', {}).get('goal_alignment', {}),
        current_meal_plan=analysis_data.get('extractedData', {}).get('meal_data', {})
    )
    
    return {
        "nutrition_adjustments": nutrition_adjustments
    }"""