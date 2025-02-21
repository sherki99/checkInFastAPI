from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from first_time_plans.call_llm_class import BaseLLM
import json
import logging

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class MacroNutrientTarget(BaseModel):
    """Specification for a single macronutrient target."""
    name: str = Field(..., description="Name of the macronutrient (Protein, Carbohydrate, Fat)")
    absolute_grams: int = Field(..., description="Daily target in grams")
    percentage_of_total: float = Field(..., description="Percentage of total caloric intake")
    calories_provided: int = Field(..., description="Calories provided by this macronutrient")
    grams_per_kg_bodyweight: float = Field(..., description="Target expressed as g/kg of bodyweight")
    scientific_rationale: str = Field(..., description="Evidence-based reasoning for this target")
    adjustment_strategy: str = Field(..., description="How to adjust this macro based on progress")

class MealSpecificMacros(BaseModel):
    """Macronutrient distribution for a specific meal."""
    meal_name: str = Field(..., description="Name of the meal (e.g., 'Breakfast', 'Post-workout')")
    meal_timing: str = Field(..., description="Recommended timing for this meal")
    protein_grams: int = Field(..., description="Protein target for this meal in grams")
    carbohydrate_grams: int = Field(..., description="Carbohydrate target for this meal in grams")
    fat_grams: int = Field(..., description="Fat target for this meal in grams")
    total_calories: int = Field(..., description="Total calories for this meal")
    purpose: str = Field(..., description="Physiological purpose of this meal")
    food_suggestions: List[str] = Field(..., description="Suggested food sources aligned with preferences")

class MacroDistributionPlan(BaseModel):
    """Complete macronutrient distribution plan."""
    client_name: str = Field(..., description="Client's name")
    primary_goal: str = Field(..., description="Client's primary nutritional goal")
    total_daily_calories: int = Field(..., description="Total daily caloric target")
    macronutrient_targets: List[MacroNutrientTarget] = Field(..., description="Targets for each macronutrient")
    protein_strategy: str = Field(..., description="Overall protein strategy based on goals and training")
    carbohydrate_strategy: str = Field(..., description="Carbohydrate approach based on activity and goals")
    fat_strategy: str = Field(..., description="Fat intake strategy for hormonal health and preferences")
    meal_specific_recommendations: List[MealSpecificMacros] = Field(..., description="Macros broken down by meal")
    nutrient_timing_principles: List[str] = Field(..., description="Key principles for nutrient timing")
    fiber_recommendation: str = Field(..., description="Daily fiber intake recommendation")
    water_recommendation: str = Field(..., description="Daily hydration recommendation")
    supplement_recommendations: List[str] = Field(..., description="Recommended supplements to support macros")
    adaptation_protocol: str = Field(..., description="How to adapt macros as goals or conditions change")

class MacroDistributionDecisionNode:
    """
    Determines optimal macronutrient distribution based on client profile,
    body composition, goals, and caloric targets.
    
    This class uses an LLM-driven decision process to establish precise macronutrient
    targets that align with the client's physiological needs, training demands,
    and dietary preferences while supporting their primary goals.
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
        profile_analysis: Dict[str, Any],
        body_analysis: Dict[str, Any],
        goal_analysis: Dict[str, Any],
        history_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process client data to determine optimal macronutrient distribution.
        
        This method integrates data from previous analysis modules to establish
        precise macronutrient targets considering:
        - Total caloric needs
        - Primary training and body composition goals
        - Individual metabolic factors
        - Training volume and intensity
        - Dietary preferences and restrictions
        - Meal timing relative to training
        
        Args:
            caloric_targets: Caloric requirements determined by previous node
            profile_analysis: Client demographic and metrics analysis
            body_analysis: Body composition analysis
            goal_analysis: Goal clarification analysis
            history_analysis: Training history analysis
            
        Returns:
            A dictionary containing the structured macronutrient distribution plan
        """
        try:
            # Process using the schema-based approach
            schema_result = self._determine_macro_distribution_schema(
                caloric_targets, profile_analysis, body_analysis, goal_analysis, history_analysis
            )
            
            return {
                "macro_distribution_plan": schema_result
            }
            
        except Exception as e:
            logger.error(f"Error determining macronutrient distribution: {str(e)}")
            raise e
    
    def get_system_message(self) -> str:
        """
        Returns the system message to guide the LLM in macronutrient distribution decision-making.
        
        The system message establishes the context and criteria for determining
        optimal macronutrient ratios according to scientific principles of sports nutrition.
        
        Returns:
            Formatted system message string
        """
        return (
            "You are a sports nutrition specialist with expertise in macronutrient optimization, "
            "nutrient timing, and performance nutrition. Your task is to determine optimal "
            "macronutrient distributions for a client based on their caloric needs, body composition, "
            "training goals, exercise regimen, and dietary preferences.\n\n"
            
            "Apply these scientific principles when determining macronutrient distributions:\n"
            "1. **Protein Requirements**: Calculate based on lean body mass, training intensity, and "
            "goal (0.8-1.0g/lb for maintenance, 1.0-1.2g/lb for muscle gain, 1.2-1.5g/lb for fat loss "
            "while preserving muscle).\n"
            "2. **Carbohydrate Periodization**: Align carbohydrate intake with training volume and intensity, "
            "considering training-day vs. rest-day needs and workout timing.\n"
            "3. **Strategic Fat Distribution**: Ensure essential fatty acid intake while balancing saturated, "
            "monounsaturated, and polyunsaturated sources for hormonal health.\n"
            "4. **Nutrient Timing**: Structure macronutrient intake around training for optimal performance "
            "and recovery, with consideration for the anabolic window and glycogen replenishment.\n"
            "5. **Individual Metabolic Factors**: Account for insulin sensitivity, metabolic rate variations, "
            "and previous dietary patterns.\n"
            "6. **Dietary Adherence**: Balance optimal nutritional science with psychological factors and "
            "food preferences to maximize long-term compliance.\n"
            "7. **Meal Frequency**: Optimize protein distribution across meals to maximize muscle protein "
            "synthesis throughout the day.\n\n"
            
            "Your macronutrient plan should include precise targets for each macronutrient, meal-specific "
            "recommendations, nutrient timing strategies relative to training, and protocols for adjusting "
            "macros based on progress assessment."
        )

    def _determine_macro_distribution_schema(
        self,
        caloric_targets: Dict[str, Any],
        profile_analysis: Dict[str, Any],
        body_analysis: Dict[str, Any],
        goal_analysis: Dict[str, Any],
        history_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Determine macronutrient distribution using Pydantic schema validation.
        
        Args:
            caloric_targets: Caloric requirements determined by previous node
            profile_analysis: Client demographic and metrics analysis
            body_analysis: Body composition analysis
            goal_analysis: Goal clarification analysis
            history_analysis: Training history analysis
            
        Returns:
            Structured macronutrient distribution plan as a Pydantic model
        """
        # Extract relevant data from caloric targets
        caloric_recommendation = caloric_targets.get("caloric_recommendation", {})
        total_calories = caloric_recommendation.get("maintenance_calories", 0)
        adjusted_calories = caloric_recommendation.get("goal_adjusted_calories", 0)
        
        # Extract client information
        client_name = profile_analysis.get("client_profile", {}).get("personal_info", {}).get("name", "Client")
        weight_kg = body_analysis.get("body_composition", {}).get("current_weight_kg", 0)
        lean_mass_kg = body_analysis.get("body_composition", {}).get("estimated_lean_mass_kg", 0)
        
        # Extract dietary preferences
        standardized_profile = {}  # This would normally come from the full standardized profile
        diet_preference = standardized_profile.get("nutrition", {}).get("data", {}).get("dietPreference", "")
        supplements = standardized_profile.get("nutrition", {}).get("data", {}).get("supplements", "")
        meal_timing = standardized_profile.get("nutrition", {}).get("data", {}).get("mealTime", "")
        
        # Extract primary goal
        primary_goal = goal_analysis.get("goals", {}).get("primary_goal", "")
        training_phase = goal_analysis.get("goals", {}).get("training_phase", "")
        
        # Extract training information
        training_frequency = history_analysis.get("training_profile", {}).get("training_frequency_weekly", 0)
        training_intensity = history_analysis.get("training_profile", {}).get("intensity_level", "")
        
        # Construct detailed prompt with comprehensive client data
        prompt = (
            "Determine the optimal macronutrient distribution for this client based on their "
            "caloric needs, body composition, training goals, and dietary preferences. Create a "
            "comprehensive macronutrient plan with meal-specific recommendations.\n\n"
            
            f"CLIENT PROFILE:\n"
            f"- Name: {client_name}\n"
            f"- Body Weight: {weight_kg} kg\n"
            f"- Estimated Lean Mass: {lean_mass_kg} kg\n"
            f"- Dietary Preferences: {diet_preference}\n"
            f"- Current Supplements: {supplements}\n"
            f"- Typical Meal Timing: {meal_timing}\n\n"
            
            f"CALORIC TARGETS:\n"
            f"- Maintenance Calories: {total_calories} kcal\n"
            f"- Goal-Adjusted Calories: {adjusted_calories} kcal\n\n"
            
            f"GOAL INFORMATION:\n"
            f"- Primary Goal: {primary_goal}\n"
            f"- Training Phase: {training_phase}\n\n"
            
            f"TRAINING PROFILE:\n"
            f"- Weekly Training Frequency: {training_frequency} sessions\n"
            f"- Training Intensity: {training_intensity}\n\n"
            
            f"BODY COMPOSITION ANALYSIS:\n{self._format_dict(body_analysis)}\n\n"
            
            "Your macronutrient distribution plan should include:\n"
            "1. Precise targets for protein, carbohydrates, and fats (in grams and percentages)\n"
            "2. Scientific rationale for each macronutrient target based on research\n"
            "3. Meal-by-meal breakdown of macronutrients\n"
            "4. Nutrient timing strategies relative to training sessions\n"
            "5. Fiber and water intake recommendations\n"
            "6. Supplement recommendations to support the macronutrient plan\n"
            "7. Protocols for adjusting macros based on progress\n\n"
            
            "Consider macronutrient distribution through the lens of current sports nutrition "
            "research, particularly the International Society of Sports Nutrition position stands "
            "on protein, nutrient timing, and body composition."
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