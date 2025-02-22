from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from first_time_plans.call_llm_class import BaseLLM
import json
import logging

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class MealDetail(BaseModel):
    """Details for a specific meal in the plan."""
    meal_name: str = Field(..., description="Name of the meal (e.g., 'Breakfast', 'Pre-workout')")
    timing: str = Field(..., description="Time of day for this meal")
    caloric_allocation: int = Field(..., description="Calories allocated to this meal")
    protein_target: int = Field(..., description="Protein target in grams")
    carb_target: int = Field(..., description="Carbohydrate target in grams")
    fat_target: int = Field(..., description="Fat target in grams")
    meal_purpose: str = Field(..., description="Purpose of this meal (e.g., 'Recovery', 'Energy')")
    food_suggestions: List[str] = Field(..., description="Example foods appropriate for this meal")
    special_considerations: Optional[str] = Field(None, description="Any special notes for this meal")

class TrainingDayPlan(BaseModel):
    """Complete meal timing plan for training days."""
    total_meals: int = Field(..., description="Total number of meals for training days")
    total_calories: int = Field(..., description="Total calories for training days")
    meal_breakdown: List[MealDetail] = Field(..., description="Details for each meal on training days")
    scientific_rationale: str = Field(..., description="Scientific basis for training day meal timing")
    pre_workout_strategy: str = Field(..., description="Strategy for pre-workout nutrition")
    post_workout_strategy: str = Field(..., description="Strategy for post-workout nutrition")

class RestDayPlan(BaseModel):
    """Complete meal timing plan for rest days."""
    total_meals: int = Field(..., description="Total number of meals for rest days")
    total_calories: int = Field(..., description="Total calories for rest days")
    meal_breakdown: List[MealDetail] = Field(..., description="Details for each meal on rest days")
    scientific_rationale: str = Field(..., description="Scientific basis for rest day meal timing")
    key_differences: str = Field(..., description="Key differences from training day structure")

class MealTimingPlan(BaseModel):
    """Complete meal timing plan with scientific rationale."""
    client_name: str = Field(..., description="Client's name")
    primary_goal: str = Field(..., description="Client's primary goal influencing meal timing")
    training_day_plan: TrainingDayPlan = Field(..., description="Meal timing plan for training days")
    rest_day_plan: RestDayPlan = Field(..., description="Meal timing plan for rest days")
    nutrient_timing_principles: List[str] = Field(..., description="Scientific principles guiding the meal timing plan")
    protein_distribution_strategy: str = Field(..., description="Strategy for distributing protein throughout the day")
    carb_distribution_strategy: str = Field(..., description="Strategy for distributing carbs throughout the day")
    fat_distribution_strategy: str = Field(..., description="Strategy for distributing fats throughout the day")
    hydration_recommendations: str = Field(..., description="Guidelines for fluid intake throughout the day")
    individual_adaptations: List[str] = Field(..., description="Client-specific adaptations to the meal timing plan")
    implementation_guidelines: List[str] = Field(..., description="Practical tips for implementing the meal timing plan")

class MealTimingDecisionNode:
    """
    Determines optimal meal timing and nutrient distribution throughout the day.
    
    This class creates evidence-based meal timing plans that align with the client's
    training schedule, macronutrient targets, and lifestyle factors.
    """
    
    def __init__(self, llm_client: Optional[Any] = None):
        """
        Initialize the MealTimingDecisionNode with an optional custom LLM client.
        
        Args:
            llm_client: Custom LLM client implementation. If None, uses the default BaseLLM.
        """
        self.llm_client = llm_client or BaseLLM()
    
    def process(
        self,
        macro_plan: Dict[str, Any],
        split_recommendation: Dict[str, Any],
        client_data: Dict[str, Any],
        goal_analysis: Dict[str, Any],
        recovery_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process client data to determine optimal meal timing and distribution.
        
        This method integrates data from multiple sources to create a
        comprehensive meal timing plan based on:
        - Macronutrient targets for training and rest days
        - Training split and workout schedule
        - Daily schedule and lifestyle factors
        - Recovery needs and individual preferences
        
        Args:
            macro_plan: Macronutrient distribution plan
            split_recommendation: Training split recommendation
            client_data: Raw client profile data
            goal_analysis: Client goals and objectives analysis
            recovery_analysis: Recovery capacity and lifestyle analysis
            
        Returns:
            A dictionary containing structured meal timing recommendations
        """
        try:
            # Process using the schema-based approach
            schema_result = self._determine_meal_timing_schema(
                macro_plan, split_recommendation, client_data, goal_analysis, recovery_analysis
            )
            
            return {
                "meal_timing_plan": schema_result
            }
            
        except Exception as e:
            logger.error(f"Error determining meal timing plan: {str(e)}")
            raise e
    
    def get_system_message(self) -> str:
        """
        Returns the system message to guide the LLM in meal timing determination.
        
        The system message establishes the context and criteria for determining
        optimal meal timing according to scientific principles.
        
        Returns:
            Formatted system message string
        """
        return (
            "You are a sports nutrition specialist with expertise in nutrient timing "
            "and meal distribution strategies for athletes and fitness enthusiasts. "
            "Your task is to create an optimal meal timing plan based on the client's "
            "macronutrient targets, training schedule, lifestyle factors, and recovery needs.\n\n"
            
            "Apply these scientific principles when designing meal timing plans:\n"
            "1. **Protein Distribution**: Distribute protein evenly throughout the day in 4-6 meals "
            "with 20-40g per meal to maximize muscle protein synthesis.\n"
            "2. **Carbohydrate Timing**: Strategically place carbohydrates around training sessions "
            "for performance and recovery, with higher amounts pre/post workout.\n"
            "3. **Training Day Nutrition**: Prioritize carbohydrate intake before, during (if appropriate), "
            "and after training sessions to support performance and recovery.\n"
            "4. **Rest Day Adjustments**: Modify meal distribution on rest days to account for "
            "different activity levels and recovery needs.\n"
            "5. **Meal Frequency**: Consider lifestyle, hunger patterns, and practical constraints "
            "when determining optimal meal frequency (typically 3-6 meals per day).\n"
            "6. **Pre-Sleep Nutrition**: Consider slow-digesting protein sources before sleep "
            "to support overnight recovery and muscle protein synthesis.\n"
            "7. **Lifestyle Integration**: Account for work schedule, training time, and other "
            "lifestyle factors when creating practical meal timing recommendations.\n\n"
            
            "Your recommendation should include specific meal timing plans for both training "
            "and rest days, with detailed macronutrient distribution for each meal."
        )
    
    def _determine_meal_timing_schema(
        self,
        macro_plan: Dict[str, Any],
        split_recommendation: Dict[str, Any],
        client_data: Dict[str, Any],
        goal_analysis: Dict[str, Any],
        recovery_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Determine meal timing plan using Pydantic schema validation.
        
        Args:
            macro_plan: Macronutrient distribution plan
            split_recommendation: Training split recommendation
            client_data: Raw client profile data
            goal_analysis: Client goals and objectives analysis
            recovery_analysis: Recovery capacity and lifestyle analysis
            
        Returns:
            Structured meal timing plan as a Pydantic model
        """
        # Extract relevant data for prompt construction
        personal_info = client_data.get("personal_info", {}).get("data", {})
        nutrition_info = client_data.get("nutrition", {}).get("data", {})
        lifestyle_info = client_data.get("lifestyle", {}).get("data", {})
        
        macro_data = macro_plan.get("macro_plan", {})
        split_data = split_recommendation.get("split_recommendation", {})
        goals = goal_analysis.get("goal_analysis_schema", {})
        primary_goals = goals.get("primary_goals", [])
        recovery_data = recovery_analysis.get("recovery_analysis_schema", {})
        
        # Extract current meal timing if available
        current_meal_schedule = nutrition_info.get("mealTime", "")
        
        # Construct detailed prompt with comprehensive client data
        prompt = (
            "Create an optimal meal timing plan for this client based on scientific principles "
            "of nutrient timing and their individual needs. Design complete meal plans for both "
            "training and rest days with specific macronutrient distribution for each meal.\n\n"
            
            f"CLIENT PROFILE SUMMARY:\n"
            f"- Name: {personal_info.get('name', 'Client')}\n"
            f"- Current Meal Schedule: {current_meal_schedule}\n"
            f"- Meals Per Day: {nutrition_info.get('mealsPerDay', 'Unknown')}\n"
            f"- Work Environment: {lifestyle_info.get('workEnvironment', 'Unknown')}\n"
            f"- Training Time: {lifestyle_info.get('trainingTime', 'Unknown')}\n"
            f"- Wake Time: {lifestyle_info.get('wakeTime', 'Unknown')}\n"
            f"- Sleep Time: {lifestyle_info.get('sleepTime', 'Unknown')}\n"
            f"- Primary Goals: {', '.join(primary_goals)}\n\n"
            
            f"MACRONUTRIENT PLAN:\n{self._format_dict(macro_data)}\n\n"
            f"TRAINING SPLIT:\n{self._format_dict(split_data)}\n\n"
            f"RECOVERY ANALYSIS:\n{self._format_dict(recovery_data)}\n\n"
            
            "Your meal timing plan should include:\n"
            "1. Detailed meal breakdowns for training days, including timing, macros, and food suggestions\n"
            "2. Detailed meal breakdowns for rest days, including timing, macros, and food suggestions\n"
            "3. Strategic nutrient timing around workout sessions\n"
            "4. Practical implementation guidelines based on the client's schedule\n"
            "5. Scientific rationale for meal frequency and macronutrient distribution\n\n"
            
            "Create a complete meal timing plan that optimizes performance, recovery, and goal achievement "
            "while being practical for implementation in the client's daily life."
        )
        
        system_message = self.get_system_message()
        result = self.llm_client.call_llm(prompt, system_message, schema=MealTimingPlan)
        return result
    
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