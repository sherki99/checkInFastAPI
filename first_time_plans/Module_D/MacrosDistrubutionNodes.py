from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from first_time_plans.call_llm_class import BaseLLM
import json
import logging

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class MacroSplit(BaseModel):
    """Macronutrient split details."""
    protein_percentage: int = Field(..., description="Protein percentage of total calories")
    protein_grams: int = Field(..., description="Daily protein in grams")
    carb_percentage: int = Field(..., description="Carbohydrate percentage of total calories")
    carb_grams: int = Field(..., description="Daily carbohydrates in grams")
    fat_percentage: int = Field(..., description="Fat percentage of total calories")
    fat_grams: int = Field(..., description="Daily fat in grams")
    scientific_rationale: str = Field(..., description="Scientific explanation for this macro split")

class MealNutritionBreakdown(BaseModel):
    """Nutritional breakdown for a specific meal."""
    meal_name: str = Field(..., description="Name of the meal (e.g., 'Breakfast', 'Pre-workout')")
    calorie_allocation: int = Field(..., description="Calories allocated to this meal")
    protein_grams: int = Field(..., description="Protein for this meal in grams")
    carb_grams: int = Field(..., description="Carbohydrates for this meal in grams")
    fat_grams: int = Field(..., description="Fats for this meal in grams")
    meal_purpose: str = Field(..., description="Primary purpose/goal of this meal")
    timing_recommendation: str = Field(..., description="Optimal timing for this meal")
    food_recommendations: List[str] = Field(..., description="Suggested food sources")

class NutrientTiming(BaseModel):
    """Nutrient timing strategies based on scientific principles."""
    training_day_strategy: str = Field(..., description="Nutrient distribution approach on training days")
    rest_day_strategy: str = Field(..., description="Nutrient distribution approach on rest days")
    pre_workout_strategy: str = Field(..., description="Pre-workout nutrition recommendation")
    post_workout_strategy: str = Field(..., description="Post-workout nutrition recommendation")
    scientific_basis: str = Field(..., description="Scientific explanation for timing strategies")

class SupplementRecommendation(BaseModel):
    """Detailed supplement recommendation."""
    supplement_name: str = Field(..., description="Name of the supplement")
    purpose: str = Field(..., description="Primary purpose/benefit")
    daily_dosage: str = Field(..., description="Recommended daily dosage")
    timing: str = Field(..., description="Optimal timing for consumption")
    evidential_support: str = Field(..., description="Level of scientific evidence supporting use")
    priority_level: str = Field(..., description="Importance level (Essential/Beneficial/Optional)")

class MacroDistributionPlan(BaseModel):
    """Complete macronutrient distribution plan."""
    daily_caloric_target: int = Field(..., description="Total daily caloric target")
    primary_goal: str = Field(..., description="Primary nutritional goal")
    macro_split: MacroSplit = Field(..., description="Macronutrient distribution")
    daily_meals: List[MealNutritionBreakdown] = Field(..., description="Individual meal breakdown")
    nutrient_timing: NutrientTiming = Field(..., description="Nutrient timing strategies")
    supplement_recommendations: List[SupplementRecommendation] = Field(..., description="Supplement recommendations")
    dietary_preferences_accommodations: List[str] = Field(..., description="Accommodations for dietary preferences")
    adjustment_strategy: str = Field(..., description="Strategy for adjusting macros based on progress")
    scientific_explanation: str = Field(..., description="Comprehensive scientific explanation")

class MacroDistributionDecisionNode:
    """
    Determines optimal macronutrient distribution based on client data and caloric targets.
    
    This class uses scientific principles and LLM-driven decision process to
    generate personalized macronutrient recommendations aligned with the client's
    goals, body composition, and individual nutritional needs.
    """
    
    def __init__(self, llm_client: Optional[Any] = None):
        """
        Initialize the MacroDistributionDecisionNode with an optional custom LLM client.
        
        Args:
            llm_client: Custom LLM client implementation. If None, uses the default BaseLLM.
        """
        self.llm_client = llm_client or BaseLLM()
    
    def process(
        self,
        caloric_targets: Dict[str, Any],
        client_data: Dict[str, Any],
        body_analysis: Dict[str, Any],
        goal_analysis: Dict[str, Any],
        history_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process client data to determine optimal macronutrient distribution.
        
        This method integrates data from multiple analysis modules to develop
        appropriate macronutrient targets, considering:
        - Total caloric intake
        - Training goals and body composition
        - Meal timing and nutrient partitioning
        - Individual dietary preferences
        
        Args:
            caloric_targets: Caloric needs analysis
            client_data: Raw client profile data
            body_analysis: Body composition analysis
            goal_analysis: Client goals analysis
            history_analysis: Training history analysis
            
        Returns:
            A dictionary containing structured macronutrient recommendations
        """
        try:
            # Process using the schema-based approach
            schema_result = self._determine_macro_distribution_schema(
                caloric_targets, client_data, body_analysis, goal_analysis, history_analysis
            )
            
            return {
                "macro_distribution_plan": schema_result
            }
            
        except Exception as e:
            logger.error(f"Error determining macronutrient distribution: {str(e)}")
            raise e
    
    def get_system_message(self) -> str:
        """
        Returns the system message to guide the LLM in macro distribution determination.
        
        The system message establishes the context and criteria for determining
        optimal macronutrient ratios according to scientific principles.
        
        Returns:
            Formatted system message string
        """
        return (
            "You are a sports nutrition specialist with expertise in determining optimal macronutrient "
            "distribution based on scientific principles. Your task is to develop a personalized "
            "macronutrient plan that aligns with the client's caloric targets, training goals, and "
            "individual preferences.\n\n"
            
            "Apply these scientific principles when determining macronutrient distribution:\n"
            "1. **Protein Requirements**: 1.6-2.2g/kg bodyweight for muscle gain/maintenance, with higher "
            "end for caloric deficits and lower body fat percentages.\n"
            "2. **Carbohydrate Allocation**: Higher carbohydrate intake (3-5g/kg) for performance-focused "
            "goals and around training; moderate (2-3g/kg) for general hypertrophy.\n"
            "3. **Fat Distribution**: Minimum 0.5g/kg body weight to support hormonal function, with remainder "
            "of calories allocated to complete caloric targets.\n"
            "4. **Meal Timing**: Strategic distribution of macronutrients around training windows to "
            "optimize performance and recovery.\n"
            "5. **Individual Adjustments**: Modifications based on dietary preferences, food sensitivities, "
            "and individual response to macronutrient ratios.\n"
            "6. **Supplement Integration**: Evidence-based supplement recommendations that complement "
            "the macronutrient strategy.\n\n"
            
            "Your recommendation should include detailed macronutrient calculations, meal-by-meal breakdown, "
            "nutrient timing strategies, and scientific rationale that aligns with the client's goals and lifestyle."
        )

    def _determine_macro_distribution_schema(
        self,
        caloric_targets: Dict[str, Any],
        client_data: Dict[str, Any],
        body_analysis: Dict[str, Any],
        goal_analysis: Dict[str, Any],
        history_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Determine macronutrient distribution using Pydantic schema validation.
        
        Args:
            caloric_targets: Caloric needs analysis
            client_data: Raw client profile data
            body_analysis: Body composition analysis
            goal_analysis: Client goals analysis
            history_analysis: Training history analysis
            
        Returns:
            Structured macronutrient distribution plan as a Pydantic model
        """
        # Extract relevant data for prompt construction
        personal_info = client_data.get("personal_info", {}).get("data", {})
        name = personal_info.get("name", "Client")
        weight = personal_info.get("weight", "86 kg").split()[0]
        
        nutrition_info = client_data.get("nutrition", {}).get("data", {})
        diet_preference = nutrition_info.get("dietPreference", "Balanced diet")
        meals_per_day = nutrition_info.get("mealsPerDay", "5")
        supplements = nutrition_info.get("supplements", "Whey protein, creatine")
        
        caloric_rec = caloric_targets.get("caloric_needs_recommendation", {})
        daily_calories = caloric_rec.get("daily_caloric_target", 2800)
        
        goals = goal_analysis.get("goal_analysis_schema", {})
        primary_goals = goals.get("primary_goals", [])
        
        training_info = history_analysis.get("history_analysis_schema", {})
        training_frequency = client_data.get("fitness", {}).get("data", {}).get("trainingFrequency", "5x Week")
        
        # Construct detailed prompt with comprehensive client data
        prompt = (
            "Develop a comprehensive macronutrient distribution plan for this client based on scientific "
            "principles of sports nutrition. Consider their caloric targets, training goals, body composition, "
            "and individual preferences.\n\n"
            
            f"CLIENT PROFILE SUMMARY:\n"
            f"- Name: {name}\n"
            f"- Weight: {weight} kg\n"
            f"- Daily caloric target: {daily_calories} calories\n"
            f"- Training frequency: {training_frequency}\n"
            f"- Primary goals: {', '.join(primary_goals)}\n"
            f"- Meals per day: {meals_per_day}\n"
            f"- Dietary preferences: {diet_preference}\n"
            f"- Current supplements: {supplements}\n\n"
            
            f"CALORIC TARGETS ANALYSIS:\n{self._format_dict(caloric_rec)}\n\n"
            f"FULL GOAL ANALYSIS:\n{self._format_dict(goals)}\n\n"
            f"TRAINING HISTORY ANALYSIS:\n{self._format_dict(training_info)}\n\n"
            
            "Your macronutrient distribution plan should include:\n"
            "1. Comprehensive macronutrient split with percentages and gram amounts\n"
            "2. Meal-by-meal breakdown with specific macro allocations\n"
            "3. Nutrient timing strategies for training and rest days\n"
            "4. Evidence-based supplement recommendations\n"
            "5. Adaptations for individual dietary preferences\n"
            "6. Scientific rationale for all recommendations\n\n"
            
            "Provide a detailed macronutrient plan that optimizes performance and recovery while "
            "respecting individual preferences and lifestyle factors."
        )
        
        system_message = self.get_system_message()
        result = self.llm_client.call_llm(prompt, system_message, schema=MacroDistributionPlan)
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