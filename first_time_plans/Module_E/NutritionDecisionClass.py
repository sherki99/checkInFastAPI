from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from first_time_plans.call_llm_class import BaseLLM
import json
import logging

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class FoodItem(BaseModel):
    """Specific food item in a meal."""
    name: str = Field(..., description="Name of the food item")
    quantity: str = Field(..., description="Quantity with unit (e.g., '3 eggs', '100g')")

class MealNutrition(BaseModel):
    """Nutritional breakdown of a meal."""
    protein: int = Field(..., description="Protein content in grams")
    carbohydrates: int = Field(..., description="Carbohydrate content in grams")
    fat: int = Field(..., description="Fat content in grams")
    calories: int = Field(..., description="Total calories")

class Meal(BaseModel):
    """Complete meal with timing and nutritional information."""
    name: str = Field(..., description="Name of the meal (e.g., 'Breakfast', 'Pre-workout Meal')")
    timing: str = Field(..., description="Timing of the meal (e.g., '+ 08:00')")
    food_items: List[FoodItem] = Field(..., description="List of food items in the meal")
    nutritional_info: MealNutrition = Field(..., description="Nutritional breakdown of the meal")

class DailyNutrition(BaseModel):
    """Total daily nutritional intake."""
    total_protein: int = Field(..., description="Total daily protein in grams")
    total_carbohydrates: int = Field(..., description="Total daily carbohydrates in grams")
    total_fat: int = Field(..., description="Total daily fat in grams")
    total_calories: int = Field(..., description="Total daily calories")

class DayPlan(BaseModel):
    """Complete meal plan for a specific day type."""
    day_type: str = Field(..., description="Type of day (Training/Non-Training)")
    meals: List[Meal] = Field(..., description="List of meals for this day type")
    daily_nutrition: DailyNutrition = Field(..., description="Total nutritional intake for this day type")

class MealPlan(BaseModel):
    """Complete structured meal plan."""
    name: str = Field(..., description="Name of the meal plan")
    description: str = Field(..., description="Description of the meal plan and principles")
    training_day_plan: DayPlan = Field(..., description="Meal plan for training days")
    non_training_day_plan: DayPlan = Field(..., description="Meal plan for non-training days")

class NutritionDecisionClass:
    """
    Integrates caloric needs, macro distribution, and meal timing decisions
    to generate a complete, formatted meal plan that follows Dr. Mike Israetel's principles.
    
    This class serves as the final nutrition plan generator, taking the outputs from
    previous decision nodes and formatting them into a comprehensive, client-ready
    nutrition program that includes specific meals, food choices, and timing.
    """
    
    def __init__(self, llm_client: Optional[Any] = None):
        """
        Initialize the NutritionDecisionClass with an optional custom LLM client.
        
        Args:
            llm_client: Custom LLM client implementation. If None, uses the default BaseLLM.
        """
        self.llm_client = llm_client or BaseLLM()
    
    def process(
        self,
        client_data: Dict[str, Any],
        caloric_targets: Dict[str, Any],
        macro_plan: Dict[str, Any],
        meal_timing: Dict[str, Any],
        goal_analysis: Dict[str, Any],
        body_analysis: Dict[str, Any],
        workout_split: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process decision node outputs to generate a complete meal plan.
        
        Args:
            client_data: Standardized client profile data
            caloric_targets: Output from CaloricNeedsDecisionNode
            macro_plan: Output from MacroDistributionDecisionNode
            meal_timing: Output from MealTimingDecisionNode
            goal_analysis: Client goals analysis output
            body_analysis: Body composition analysis output
            workout_split: Training split recommendation
            
        Returns:
            Dict containing the formatted meal plan and relevant metadata
        """
        try:
            # Generate the complete meal plan
            meal_plan = self._generate_meal_plan(
                client_data,
                caloric_targets,
                macro_plan,
                meal_timing,
                goal_analysis,
                body_analysis,
                workout_split
            )
            
            # Format the meal plan according to the required format
            formatted_plan = self._format_meal_plan(meal_plan)
            
            return {
                "meal_plan": meal_plan,
                "formatted_meal_plan": formatted_plan
            }
            
        except Exception as e:
            logger.error(f"Error generating meal plan: {str(e)}")
            raise e
    
    def get_system_message(self) -> str:
        """
        Returns the system message to guide the LLM in meal plan generation.
        
        Returns:
            Formatted system message string
        """
        return (
            "You are an expert nutritionist specializing in sports nutrition and meal planning, "
            "following Dr. Mike Israetel's principles. Your task is to create a detailed, practical "
            "meal plan based on previous analyses of the client's caloric needs, macro distribution, "
            "and meal timing requirements.\n\n"
            
            "Follow these guidelines when generating the meal plan:\n"
            "1. **Evidence-Based Nutrition**: Apply scientific principles regarding protein requirements, "
            "carbohydrate timing, and fat distribution.\n"
            "2. **Goal-Specific Approach**: Ensure caloric and macronutrient targets align with the client's "
            "specific training goals (muscle gain, fat loss, performance).\n"
            "3. **Practical Implementation**: Recommend accessible foods and realistic meal timing that "
            "the client can consistently follow.\n"
            "4. **Training/Non-Training Differentiation**: Provide different meal plans for training and "
            "non-training days with appropriate nutrient timing.\n"
            "5. **Precision**: Include exact quantities and nutritional breakdowns for each meal.\n"
            "6. **Format Compliance**: Strictly follow the required output format for the meal plan.\n\n"
            
            "Your output should be a comprehensive meal plan that a client can immediately begin following, "
            "with clear instructions for meal timing, food choices, and portion sizes."
        )
    
    def _generate_meal_plan(
        self,
        client_data: Dict[str, Any],
        caloric_targets: Dict[str, Any],
        macro_plan: Dict[str, Any],
        meal_timing: Dict[str, Any],
        goal_analysis: Dict[str, Any],
        body_analysis: Dict[str, Any],
        workout_split: Dict[str, Any]
    ) -> MealPlan:
        """
        Generate a complete meal plan using the LLM based on decision node outputs.
        
        Args:
            client_data: Standardized client profile data
            caloric_targets: Output from CaloricNeedsDecisionNode
            macro_plan: Output from MacroDistributionDecisionNode
            meal_timing: Output from MealTimingDecisionNode
            goal_analysis: Client goals analysis output
            body_analysis: Body composition analysis output
            workout_split: Training split recommendation
            
        Returns:
            MealPlan object containing the complete meal plan
        """
        # Extract relevant client info
        client_name = client_data.get("personal_info", {}).get("data", {}).get("name", "Client")
        primary_goals = goal_analysis.get("goal_analysis_schema", {}).get("data", {}).get("primary_goals", [])
        food_preferences = client_data.get("nutrition", {}).get("data", {}).get("dietPreference", {})
        food_restrictions = client_data.get("nutrition", {}).get("data", {}).get("food_restrictions", []) # is empty arrauy always bcs does not exist yeat 
        
        # Get caloric targets
        training_day_calories = caloric_targets.get("training_day_calories", 2500)
        rest_day_calories = caloric_targets.get("rest_day_calories", 2200)
        
        # Get macro distribution
        training_day_macros = macro_plan.get("training_day_plan", {}).get("macros", {})
        rest_day_macros = macro_plan.get("rest_day_plan", {}).get("macros", {})
        
        # Get meal timing
        training_day_timing = meal_timing.get("training_day_plan", {}).get("meal_breakdown", [])
        rest_day_timing = meal_timing.get("rest_day_plan", {}).get("meal_breakdown", [])
        
        # Construct the prompt
        prompt = (
            f"Create a detailed meal plan for {client_name} based on the following analyses:\n\n"
            
            f"PRIMARY GOALS:\n{', '.join(primary_goals)}\n\n"
            
            f"FOOD PREFERENCES:\n{', '.join(food_preferences)}\n\n"
            
            f"FOOD RESTRICTIONS:\n{', '.join(food_restrictions)}\n\n"
            
            f"CALORIC TARGETS:\n"
            f"Training Day Calories: {training_day_calories}\n"
            f"Rest Day Calories: {rest_day_calories}\n\n"
            
            f"MACRO DISTRIBUTION:\n"
            f"Training Day: {json.dumps(training_day_macros, indent=2)}\n"
            f"Rest Day: {json.dumps(rest_day_macros, indent=2)}\n\n"
            
            f"MEAL TIMING:\n"
            f"{json.dumps(meal_timing, indent=2)}\n\n"
            
            "Generate a complete meal plan that includes:\n"
            "1. A descriptive name for the meal plan\n"
            "2. A brief overview of the nutrition principles\n"
            "3. Detailed meal plans for both training and non-training days including:\n"
            "   - Specific foods with exact quantities\n"
            "   - Meal timing recommendations\n"
            "   - Complete nutritional breakdown per meal\n"
            "   - Daily nutritional totals\n\n"
            
            "Follow Dr. Mike Israetel's nutrition principles. Create a meal plan that is practical, "
            "aligns with the client's preferences, and supports their training goals."
        )
        
        system_message = self.get_system_message()
        result = self.llm_client.call_llm(prompt, system_message, schema=MealPlan)
        return result
    
    def _format_meal_plan(self, meal_plan: MealPlan) -> str:
        """
        Format the meal plan according to the required output format.
        
        Args:
            meal_plan: MealPlan object containing the complete meal plan
            
        Returns:
            Formatted meal plan as a string
        """
        formatted_output = f"Name of The Meal: {meal_plan.name}  \n"
        formatted_output += f"Description: {meal_plan.description}  \n\n"
        
        # Format Training Day Meals
        formatted_output += "Training Day Meals:  \n\n"
        
        for i, meal in enumerate(meal_plan.training_day_plan.meals, 1):
            formatted_output += f"MEAL {i}: {meal.name} (T) {meal.timing}  \n"
            
            for food in meal.food_items:
                formatted_output += f"- Name: {food.name}  \n"
                formatted_output += f"- Quantity: {food.quantity}  \n\n"
            
            formatted_output += "Nutritional Info:  \n"
            formatted_output += f"- Protein: {meal.nutritional_info.protein}g  \n"
            formatted_output += f"- Carbohydrates: {meal.nutritional_info.carbohydrates}g  \n"
            formatted_output += f"- Fat: {meal.nutritional_info.fat}g  \n"
            formatted_output += f"- Calories: {meal.nutritional_info.calories} kcal  \n\n"
        
        # Format Training Day Totals
        formatted_output += "Total Daily Nutritional Intake (T):  \n"
        formatted_output += f"Total-Protein-T: {meal_plan.training_day_plan.daily_nutrition.total_protein}g  \n"
        formatted_output += f"Total-Carbohydrates-T: {meal_plan.training_day_plan.daily_nutrition.total_carbohydrates}g  \n"
        formatted_output += f"Total-Fat-T: {meal_plan.training_day_plan.daily_nutrition.total_fat}g  \n"
        formatted_output += f"Total-Calories-T: {meal_plan.training_day_plan.daily_nutrition.total_calories} kcal  \n\n"
        
        # Format Non-Training Day Meals
        formatted_output += "Non-Training Day Meals:  \n\n"
        
        for i, meal in enumerate(meal_plan.non_training_day_plan.meals, 1):
            formatted_output += f"MEAL {i}: {meal.name} (NT) {meal.timing}  \n"
            
            for food in meal.food_items:
                formatted_output += f"- Name: {food.name}  \n"
                formatted_output += f"- Quantity: {food.quantity}  \n"
            
            formatted_output += "\nNutritional Info:  \n"
            formatted_output += f"- Protein: {meal.nutritional_info.protein}g  \n"
            formatted_output += f"- Carbohydrates: {meal.nutritional_info.carbohydrates}g  \n"
            formatted_output += f"- Fat: {meal.nutritional_info.fat}g  \n"
            formatted_output += f"- Calories: {meal.nutritional_info.calories} kcal  \n\n"
        
        # Format Non-Training Day Totals
        formatted_output += "Total Daily Nutritional Intake (NT):  \n"
        formatted_output += f"Total-Protein-NT: {meal_plan.non_training_day_plan.daily_nutrition.total_protein}g  \n"
        formatted_output += f"Total-Carbohydrates-NT: {meal_plan.non_training_day_plan.daily_nutrition.total_carbohydrates}g  \n"
        formatted_output += f"Total-Fat-NT: {meal_plan.non_training_day_plan.daily_nutrition.total_fat}g  \n"
        formatted_output += f"Total-Calories-NT: {meal_plan.non_training_day_plan.daily_nutrition.total_calories} kcal  \n"
        
        return formatted_output