from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from first_time_plans.call_llm_class import BaseLLM
import logging

from typing import List, Optional
from pydantic import BaseModel, Field

class MacroAdjustment(BaseModel):
    """Represents an adjustment for a specific macronutrient."""
    nutrient_type: str  # e.g., "protein", "carbs", "fat"
    adjustment_value: float  # percentage or absolute change
    adjustment_unit: str = "%"  # default to percentage, can be "%" or "g"

class MealComponent(BaseModel):
    """Represents a component of a meal."""
    food_item: str
    portion_size: Optional[float] = None
    portion_unit: Optional[str] = None

class MealPlanEntry(BaseModel):
    """Represents a single meal in a meal plan."""
    meal_name: str  # e.g., "Breakfast", "Lunch", "Dinner", "Snack"
    components: List[MealComponent]
    estimated_calories: Optional[float] = None
    estimated_macros: Optional[List[MacroAdjustment]] = None

class NutritionAdjustmentRecommendation(BaseModel):
    """Structured recommendation for nutrition adjustments."""
    macro_adjustments: List[MacroAdjustment] = Field(
        default_factory=list, 
        description="Recommended changes to macronutrient intake"
    )
    calorie_adjustments: float = Field(
        default=0, 
        description="Recommended change in total daily calorie intake"
    )
    meal_timing_changes: Optional[List[str]] = Field(
        None, 
        description="Suggested changes to meal timing or distribution"
    )
    specific_food_recommendations: Optional[List[str]] = Field(
        None, 
        description="Specific food or supplement recommendations"
    )
    rationale: str = Field(
        ..., 
        description="Explanation for the recommended nutrition changes"
    )
    new_meal_plan: Optional[List[MealPlanEntry]] = Field(
        None, 
        description="Updated meal plan if significant changes are needed. Always return the entire meal plan even if no changes are needed."
    )


    
class NutritionAdjustmentNode:
    """
    Module for determining nutrition changes based on analysis and goal alignment.
    """

    def __init__(self, llm_client: Optional[Any] = None):
        """
        Initialize the NutritionAdjustmentNode.
        
        Args:
            llm_client: Custom LLM client implementation. If None, uses the default BaseLLM.
        """
        self.llm_client = llm_client or BaseLLM()
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    def get_system_message(self) -> str:
        """
        Returns the system message to guide the LLM in nutrition adjustment decisions.
        
        Returns:
            Formatted system message string
        """
        return (
            "You are a nutrition and fitness optimization expert specializing in creating personalized "
            "nutrition adjustment recommendations. Your task is to provide precise, scientifically-backed "
            "nutrition modifications that align with the client's fitness goals and current performance.\n\n"
            
            "Key Considerations:\n"
            "1. Analyze current nutrition adherence and performance\n"
            "2. Align recommendations with specific fitness goals\n"
            "3. Provide actionable and precise macro/calorie adjustments\n"
            "4. Consider individual metabolic and performance metrics\n"
            "5. Ensure recommendations are practical and sustainable"
        )

    def determine_nutrition_changes(
        self, 
        nutrition_analysis: Dict[str, Any], 
        goal_alignment: Dict[str, Any],
        current_meal_plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Determine nutrition changes based on comprehensive analysis.
        
        Args:
            nutrition_analysis: Detailed nutrition performance analysis
            goal_alignment: Current goal progress and alignment status
            current_meal_plan: Existing meal plan details
            
        Returns:
            Nutrition adjustment recommendations
        """
        try:
            # Prepare comprehensive prompt for LLM analysis
            prompt = (
                "Perform a detailed nutrition adjustment analysis based on the following data:\n\n"
                f"NUTRITION ANALYSIS:\n{self._format_dict(nutrition_analysis)}\n\n"
                f"GOAL ALIGNMENT:\n{self._format_dict(goal_alignment)}\n\n"
                f"CURRENT MEAL PLAN:\n{self._format_dict(current_meal_plan)}\n\n"
                
                "Provide comprehensive nutrition adjustment recommendations covering:\n"
                "1. Macro and calorie adjustments\n"
                "2. Meal timing and distribution changes\n"
                "3. Specific food or supplement recommendations\n"
                "4. Rationale for proposed changes\n"
                "5. Potential updates to the meal plan"
            )
            
            system_message = self.get_system_message()
            result = self.llm_client.call_llm(
                prompt, 
                system_message, 
                schema=NutritionAdjustmentRecommendation
            )
            
            return result
        
        except Exception as e:
            self.logger.error(f"Error determining nutrition changes: {str(e)}")
            raise e

    def _format_dict(self, data: Dict[str, Any]) -> str:
        """Format dictionary into readable string."""
        if not data:
            return "No data available"
        
        formatted = ""
        for key, value in data.items():
            formatted += f"  {key}: {value}\n"
        return formatted


    """
    Module for determining training changes based on analysis and goal alignment.
    """

    def __init__(self, llm_client: Optional[Any] = None):
        """
        Initialize the TrainingAdjustmentNode.
        
        Args:
            llm_client: Custom LLM client implementation. If None, uses the default BaseLLM.
        """
        self.llm_client = llm_client or BaseLLM()
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    def get_system_message(self) -> str:
        """
        Returns the system message to guide the LLM in training adjustment decisions.
        
        Returns:
            Formatted system message string
        """
        return (
            "You are a high-performance training optimization expert specializing in creating "
            "personalized workout adjustments. Your task is to provide precise, scientifically-backed "
            "training modifications that align with the client's fitness goals and current performance.\n\n"
            
            "Key Considerations:\n"
            "1. Analyze current training performance and progression\n"
            "2. Align recommendations with specific fitness goals\n"
            "3. Provide actionable exercise, volume, and intensity modifications\n"
            "4. Consider individual strength, recovery, and technique metrics\n"
            "5. Ensure recommendations promote continuous improvement and injury prevention"
        )

    def determine_training_changes(
        self, 
        training_analysis: Dict[str, Any], 
        goal_alignment: Dict[str, Any],
        current_workout_plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Determine training changes based on comprehensive analysis.
        
        Args:
            training_analysis: Detailed training performance analysis
            goal_alignment: Current goal progress and alignment status
            current_workout_plan: Existing workout plan details
            
        Returns:
            Training adjustment recommendations
        """
        try:
            # Prepare comprehensive prompt for LLM analysis
            prompt = (
                "Perform a detailed training adjustment analysis based on the following data:\n\n"
                f"TRAINING ANALYSIS:\n{self._format_dict(training_analysis)}\n\n"
                f"GOAL ALIGNMENT:\n{self._format_dict(goal_alignment)}\n\n"
                f"CURRENT WORKOUT PLAN:\n{self._format_dict(current_workout_plan)}\n\n"
                
                "Provide comprehensive training adjustment recommendations covering:\n"
                "1. Exercise modifications and progressions\n"
                "2. Volume and intensity adjustments\n"
                "3. Recovery and technique improvement strategies\n"
                "4. Rationale for proposed changes\n"
                "5. Potential updates to the workout plan"
            )
            
            system_message = self.get_system_message()
            result = self.llm_client.call_llm(
                prompt, 
                system_message, 
                schema=TrainingAdjustmentRecommendation
            )
            
            return result
        
        except Exception as e:
            self.logger.error(f"Error determining training changes: {str(e)}")
            raise e

    def _format_dict(self, data: Dict[str, Any]) -> str:
        """Format dictionary into readable string."""
        if not data:
            return "No data available"
        
        formatted = ""
        for key, value in data.items():
            formatted += f"  {key}: {value}\n"
        return formatted